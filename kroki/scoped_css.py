"""Scope a stylesheet to one element, so an inlined SVG's CSS cannot restyle the page.

An SVG inlined into a notebook keeps its links, ``<title>`` tooltips, selectable text
and web fonts, but its ``<style>`` blocks become page CSS (thorwhalen/kroki#1).
:func:`scope_css` rewrites a stylesheet so that every rule only matches inside one
element, ``#<scope_id>``; :func:`scope_svg` applies it to an SVG document's
``<style>`` elements and gives the SVG root that id (thorwhalen/kroki#8).

The rewrite works on CSS *tokens* (strings, comments, blocks, top-level commas), not
on regular expressions over the text, so a ``{`` or ``,`` inside a string, a comment,
``:is(a, b)`` or an attribute selector does not derail it.

>>> scope_css("p, .label { color: red }", "k1")
'#k1 p, #k1 .label { color: red }'
>>> scope_css("@media print { :root svg { display: none } }", "k1")
'@media print { #k1 svg { display: none } }'
"""

from __future__ import annotations

import html
import re
import uuid
from xml.sax.saxutils import escape as xml_escape

__all__ = ["scope_css", "scope_svg", "new_scope_id"]

#: At-rules whose block holds rules to scope in turn.
_RULE_BLOCK_AT_RULES = frozenset(
    {
        "media", "supports", "container", "layer", "scope", "document",
        "-moz-document", "starting-style",
    }
)
#: At-rules dropped from a scoped stylesheet: an ``@import`` pulls in a stylesheet
#: whose rules would apply to the whole page, and ``@page`` styles the printed page
#: itself; neither can be scoped from here.
_DROPPED_AT_RULES = frozenset({"import", "page"})
#: A leading compound naming the document root rather than something inside it.
_ROOT_SELECTORS = frozenset({":root", "html", "body", "svg"})

def new_scope_id(prefix: str = "kroki-scope") -> str:
    """A fresh, random element id.

    Random rather than counted: a saved notebook keeps the ids of an earlier
    session's outputs, and a counter restarting at 1 would give a new diagram the
    id of an old one, whose scoped CSS would then style both.
    """
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


# --------------------------------------------------------------------------- tokens


def _skip_string(css: str, i: int) -> int:
    """Index just past the string literal starting at ``css[i]`` (a quote)."""
    quote, i = css[i], i + 1
    while i < len(css):
        c = css[i]
        if c == "\\":
            i += 2
            continue
        if c == quote or c == "\n":  # an unclosed string ends at the line, as in CSS
            return i + 1
        i += 1
    return i


_UNQUOTED_URL_RE = re.compile(r"url\(\s*(?![\s\"'])", re.IGNORECASE)


def _is_name_char(c: str) -> bool:
    return c.isalnum() or c in "-_" or ord(c) > 127


def _skip_comment(css: str, i: int) -> int:
    end = css.find("*/", i + 2)
    return len(css) if end < 0 else end + 2


def _scan(css: str, i: int, stops: str) -> int:
    """Index of the first of *stops* at nesting depth 0 from *i*, or ``len(css)``.

    Strings, comments, and ``()``/``[]``/``{}`` nesting are skipped over.
    """
    depth = 0
    while i < len(css):
        c = css[i]
        if c in "\"'":
            i = _skip_string(css, i)
            continue
        if _UNQUOTED_URL_RE.match(css, i) and (i == 0 or not _is_name_char(css[i - 1])):
            # An unquoted url( is one token up to its ")", quotes and "/*" included,
            # as a browser reads it: a stray quote must not swallow later rules.
            close = css.find(")", i)
            i = len(css) if close < 0 else close + 1
            continue
        if css.startswith("/*", i):
            i = _skip_comment(css, i)
            continue
        if c == "\\":
            i += 2
            continue
        if depth == 0 and c in stops:
            return i
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth = max(depth - 1, 0)
        i += 1
    return i


def _split_top_level(text: str, sep: str = ",") -> list[str]:
    parts, i = [], 0
    while True:
        j = _scan(text, i, sep)
        parts.append(text[i:j])
        if j >= len(text):
            return parts
        i = j + 1


# ------------------------------------------------------------------------ selectors


def _scope_selector(selector: str, scope: str, old_ids: frozenset) -> str:
    lead = selector[: len(selector) - len(selector.lstrip())]
    trail = selector[len(selector.rstrip()) :]
    body = selector.strip()
    if not body:
        return selector
    # The leading compound: up to the first combinator or whitespace at depth 0.
    end = _scan(body, 0, " \t\n\r>+~")
    first, rest = body[:end], body[end:]
    for old in old_ids:  # mermaid writes `#mermaid-1 .node`: that id is the root's
        if re.fullmatch(rf"#{re.escape(old)}(?![\w-])\S*", first):
            return f"{lead}#{scope}{first[len(old) + 1 :]}{rest}{trail}"
    if first.lower() in _ROOT_SELECTORS or first.lower().startswith(
        tuple(f"{s}:" for s in _ROOT_SELECTORS) + tuple(f"{s}." for s in _ROOT_SELECTORS)
    ):
        name = next(s for s in _ROOT_SELECTORS if first.lower().startswith(s))
        return f"{lead}#{scope}{first[len(name):]}{rest}{trail}"
    return f"{lead}#{scope} {body}{trail}"


def _scope_prelude(prelude: str, scope: str, old_ids: frozenset) -> str:
    return ",".join(
        _scope_selector(s, scope, old_ids) for s in _split_top_level(prelude, ",")
    )


# ---------------------------------------------------------------------- stylesheets


def scope_css(css: str, scope_id: str, *, root_ids=()) -> str:
    """*css* with every rule confined to the element ``#<scope_id>``.

    Each selector is prefixed with ``#<scope_id> ``; a leading ``:root``, ``html``,
    ``body`` or ``svg`` (the document the stylesheet was written for) becomes the
    scope element itself, and so does a leading ``#<id>`` for an id in *root_ids*
    (the SVG root's own id, which mermaid's selectors name). ``@media``,
    ``@supports`` and similar blocks are scoped inside; ``@font-face``,
    ``@keyframes`` and other descriptor blocks are kept as they are; ``@import`` is
    dropped, since what it imports could not be scoped.

    >>> scope_css('#mermaid-1 .node, svg{fill:red}', 'k', root_ids=['mermaid-1'])
    '#k .node, #k{fill:red}'
    >>> scope_css('@import url(x.css); a[title="a,b{"]{x:1}', 'k')
    ' #k a[title="a,b{"]{x:1}'
    """
    old_ids = frozenset(root_ids)
    out, i = [], 0
    while i < len(css):
        # Whitespace and comments between rules pass through unchanged.
        if css[i].isspace():
            out.append(css[i])
            i += 1
            continue
        if css.startswith("/*", i):
            j = _skip_comment(css, i)
            out.append(css[i:j])
            i = j
            continue
        if css.startswith("<!--", i) or css.startswith("-->", i):
            j = i + (4 if css.startswith("<!--", i) else 3)
            out.append(css[i:j])
            i = j
            continue
        if css[i] == "@":
            j = _scan(css, i, ";{")
            name = re.match(r"@([-\w]+)", css[i:j])
            name = name.group(1).lower() if name else ""
            if j < len(css) and css[j] == "{":
                close = _scan(css, j + 1, "}")
                inner = css[j + 1 : close]
                if name in _RULE_BLOCK_AT_RULES:
                    inner = scope_css(inner, scope_id, root_ids=root_ids)
                if name not in _DROPPED_AT_RULES:
                    out.append(f"{css[i:j]}{{{inner}}}")
                i = close + 1
            else:
                if name not in _DROPPED_AT_RULES:
                    out.append(css[i : j + 1])
                i = j + 1
            continue
        if css[i] == "}":  # a stray closer: keep it, so nothing after it is lost
            out.append("}")
            i += 1
            continue
        j = _scan(css, i, "{")
        if j >= len(css):  # a trailing prelude with no block is no rule at all
            out.append(css[i:])
            break
        close = _scan(css, j + 1, "}")
        out.append(f"{_scope_prelude(css[i:j], scope_id, old_ids)}{css[j:close + 1]}")
        i = close + 1
    return "".join(out)


# ------------------------------------------------------------------------------ svg

# Tags are matched with quoted attribute values skipped, so a ">" inside one does
# not end the tag; a self-closing <style/> is not an opener.
_ATTRS = r"""(?:[^>"'/]|"[^"]*"|'[^']*'|/(?!>))*"""
_STYLE_RE = re.compile(
    rf"(<style\b{_ATTRS}>)(.*?)(</style\s*>)", re.DOTALL | re.IGNORECASE
)
_CDATA_RE = re.compile(r"^(\s*<!\[CDATA\[)(.*)(\]\]>\s*)$", re.DOTALL)
_ROOT_RE = re.compile(rf"<svg\b{_ATTRS}/?>", re.DOTALL)
_ATTR_RE = re.compile(r"""(\s)([\w:.-]+)(\s*=\s*)(["'])(.*?)\4""", re.DOTALL)


def scope_svg(svg: str, scope_id: str | None = None) -> str:
    """*svg* with its root's id set to *scope_id* and its ``<style>`` CSS scoped to it.

    The ``<style>`` elements are found as markup (the CSS inside them is rewritten by
    :func:`scope_css`), with a ``CDATA`` wrapper kept as it was. The root's previous
    id, if any, is what its own selectors are rewritten from.

    >>> s = scope_svg('<svg id="m1"><style>#m1 p{x:1} q{y:2}</style></svg>', 'k')
    >>> s
    '<svg id="k"><style>#k p{x:1} #k q{y:2}</style></svg>'
    """
    scope_id = scope_id or new_scope_id()
    root = _ROOT_RE.search(svg)
    if not root:
        return svg
    tag = root.group(0)
    old = next((a for a in _ATTR_RE.finditer(tag) if a.group(2) == "id"), None)
    old_ids = (html.unescape(old.group(5)),) if old else ()
    if old:
        new_tag = f"{tag[: old.start(5)]}{scope_id}{tag[old.end(5) :]}"
    else:
        new_tag = f'<svg id="{scope_id}"{tag[4:]}'

    def rewrite(m):
        open_, css, close = m.groups()
        cdata = _CDATA_RE.match(css)
        if cdata:
            pre, body, post = cdata.groups()
            return f"{open_}{pre}{scope_css(body, scope_id, root_ids=old_ids)}{post}{close}"
        # Outside CDATA the text is XML: "&gt;" and "&quot;" are what a browser
        # reads as ">" and '"', so the CSS is scoped decoded and escaped back, or a
        # quote the tokenizer cannot see would let a rule slip out unscoped.
        scoped = scope_css(html.unescape(css), scope_id, root_ids=old_ids)
        return f"{open_}{xml_escape(scoped)}{close}"

    rest = _STYLE_RE.sub(rewrite, svg[root.end() :])
    return f"{svg[: root.start()]}{new_tag}{rest}"
