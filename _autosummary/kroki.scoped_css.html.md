# kroki.scoped_css

Scope a stylesheet to one element, so an inlined SVG’s CSS cannot restyle the page.

An SVG inlined into a notebook keeps its links, `<title>` tooltips, selectable text
and web fonts, but its `<style>` blocks become page CSS (thorwhalen/kroki#1).
[`scope_css()`](#kroki.scoped_css.scope_css) rewrites a stylesheet so that every rule only matches inside one
element, `#<scope_id>`; [`scope_svg()`](#kroki.scoped_css.scope_svg) applies it to an SVG document’s
`<style>` elements and gives the SVG root that id (thorwhalen/kroki#8).

The rewrite works on CSS *tokens* (strings, comments, blocks, top-level commas), not
on regular expressions over the text, so a `{` or `,` inside a string, a comment,
`:is(a, b)` or an attribute selector does not derail it.

```pycon
>>> scope_css("p, .label { color: red }", "k1")
'#k1 p, #k1 .label { color: red }'
>>> scope_css("@media print { :root svg { display: none } }", "k1")
'@media print { #k1 svg { display: none } }'
```

### Functions

| [`scope_css`](#kroki.scoped_css.scope_css)(css, scope_id, \*[, root_ids])   | *css* with every rule confined to the element `#<scope_id>`.                   |
|---------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| [`scope_svg`](#kroki.scoped_css.scope_svg)(svg[, scope_id])                 | *svg* with its root's id set to *scope_id* and its `<style>` CSS scoped to it. |
| [`new_scope_id`](#kroki.scoped_css.new_scope_id)([prefix])                     | A fresh, random element id.                                                    |

### kroki.scoped_css.new_scope_id(prefix='kroki-scope')

A fresh, random element id.

Random rather than counted: a saved notebook keeps the ids of an earlier
session’s outputs, and a counter restarting at 1 would give a new diagram the
id of an old one, whose scoped CSS would then style both.

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### kroki.scoped_css.scope_css(css, scope_id, , root_ids=())

*css* with every rule confined to the element `#<scope_id>`.

Each selector is prefixed with `#<scope_id> ``; a leading ``:root`, `html`,
`body` or `svg` (the document the stylesheet was written for) becomes the
scope element itself, and so does a leading `#<id>` for an id in *root_ids*
(the SVG root’s own id, which mermaid’s selectors name). `@media`,
`@supports` and similar blocks are scoped inside; `@font-face`,
`@keyframes` and other descriptor blocks are kept as they are ([`scope_svg()`](#kroki.scoped_css.scope_svg)
renames their global names per scope); `@import` is
dropped, since what it imports could not be scoped.

```pycon
>>> scope_css('#mermaid-1 .node, svg{fill:red}', 'k', root_ids=['mermaid-1'])
'#k .node, #k{fill:red}'
>>> scope_css('@import url(x.css); a[title="a,b{"]{x:1}', 'k')
' #k a[title="a,b{"]{x:1}'
```

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### kroki.scoped_css.scope_svg(svg, scope_id=None)

*svg* with its root’s id set to *scope_id* and its `<style>` CSS scoped to it.

The `<style>` elements are found as markup (the CSS inside them is rewritten by
[`scope_css()`](#kroki.scoped_css.scope_css)), with a `CDATA` wrapper kept as it was. The root’s previous
id, if any, is what its own selectors are rewritten from.

```pycon
>>> s = scope_svg('<svg id="m1"><style>#m1 p{x:1} q{y:2}</style></svg>', 'k')
>>> s
'<svg id="k"><style>#k p{x:1} #k q{y:2}</style></svg>'
```

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)
