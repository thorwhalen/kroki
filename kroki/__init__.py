"""Kroki from python"""

import base64, zlib
from functools import partial
from itertools import chain
from typing import Literal
import re

import requests
from IPython.display import Image, SVG, display

from i2 import validate_literal, wrap, Pipe

_ascii_decode = partial(bytes.decode, encoding="ascii")
_utf8_decode = partial(bytes.decode, encoding="utf-8")
_zlib_compress_level_9 = partial(zlib.compress, level=9)


def encode_src(diagram_source: str):
    """
    Encode a diagram source string into a base64 string that can be used in a URL.
    :param diagram_source: The diagram source string.
    :return: The encoded string.

    >>> encode_src('Bob->Alice : Hello!')
    'eNpzyk_StXPMyUxOVbBS8EjNyclXBAA7UAXs'
    """
    return _ascii_decode(
        base64.urlsafe_b64encode(_zlib_compress_level_9(str.encode(diagram_source)))
    )


def decode_src(encoded_diagram_source: str):
    """
    Decode a diagram source string from a base64 string.

    :param encoded_diagram_source: The encoded diagram source string.
    :return: The decoded string.

    >>> decode_src('eNpzyk_StXPMyUxOVbBS8EjNyclXBAA7UAXs')
    'Bob->Alice : Hello!'

    """
    return _utf8_decode(
        zlib.decompress(base64.urlsafe_b64decode(encoded_diagram_source))
    )


# The output formats supported by each diagram type.
# More precisely, a dictionary, which contains both the choices of diagram_type (as
# keys) and the corresponding output_format each support (as values).
output_formats = {
    "blockdiag": ["png", "svg", "pdf"],
    "bpmn": ["svg"],
    "bytefield": ["svg"],
    "seqdiag": ["png", "svg", "pdf"],
    "actdiag": ["png", "svg", "pdf"],
    "nwdiag": ["png", "svg", "pdf"],
    "packetdiag": ["png", "svg", "pdf"],
    "rackdiag": ["png", "svg", "pdf"],
    "c4plantuml": [
        "png",
        "svg",
        "pdf",
        "txt",
        "base64",
    ],  # manually replaced c4withplantuml
    "d2": ["svg"],
    "dbml": ["svg"],
    "ditaa": ["png", "svg"],
    "erd": ["png", "svg", "jpeg", "pdf"],
    "excalidraw": ["svg"],
    "graphviz": ["png", "svg", "jpeg", "pdf"],
    "mermaid": ["png", "svg"],
    "nomnoml": ["svg"],
    "pikchr": ["svg"],
    "plantuml": ["png", "svg", "pdf", "txt", "base64"],
    "structurizr": ["png", "svg", "pdf", "txt", "base64"],
    "svgbob": ["svg"],
    "symbolator": ["svg"],
    "tikz": ["png", "svg", "jpeg", "pdf"],
    "umlet": ["png", "svg", "jpeg"],
    "vega": ["png", "svg", "pdf"],
    "vegalite": ["png", "svg", "pdf"],
    "wavedrom": ["svg"],
    "wireviz": ["png", "svg"],
}
diagram_types = set(output_formats)


# TODO: Way to avoid dunder __getitem__ in the following:
DiagramKindOptions = Literal.__getitem__(tuple(sorted(diagram_types)))
OutputFormatOptions = Literal.__getitem__(
    tuple(sorted(set(chain.from_iterable(output_formats.values()))))
)

url_template = "https://kroki.io/{diagram_type}/{output_format}/{diagram_source}"


@validate_literal
def diagram_image_bytes(
    diagram_source: str = "Bob->Alice : Hello!",
    diagram_type: DiagramKindOptions = "plantuml",
    output_format: OutputFormatOptions = "svg",
):
    """
    Get the bytes of a diagram image.

    :param diagram_source: The diagram source string.
    :param diagram_type: The diagram type.
    :param output_format: The output format.
    :return: The bytes of the diagram image.
    """
    # if diagram_format not in
    url = url_template.format(
        diagram_type=diagram_type,
        output_format=output_format,
        diagram_source=encode_src(diagram_source),
    )
    r = requests.get(url)
    if r.status_code == 200:
        return r.content
    else:
        # TODO: Do r.raise_for_status() instead?
        raise RuntimeError(
            f"Request returned with an error code {r.status_code}. Content: \n{r.content}"
        )


svg_re = r"(?:<\?xml\b[^>]*>[^<]*)?(?:<!--.*?-->[^<]*)*(?:<svg|<!DOCTYPE svg)\b"
svg_re = re.compile(svg_re.encode(), re.DOTALL)


def is_svg(b: bytes):
    return bool(svg_re.match(b))


_svg_root_re = re.compile(r"<svg\b[^>]*>", re.DOTALL)
# Not preceded by a name character or "-", so "width" never matches "stroke-width".
_attr_re = r'(?<![\w-]){}\s*=\s*["\']([^"\']*)["\']'


def _root_attr(svg_tag: str, name: str):
    m = re.search(_attr_re.format(re.escape(name)), svg_tag)
    return m.group(1) if m else None


def svg_to_img_html(svg) -> str:
    """An ``<img>`` showing *svg* as its own document.

    Inlined into a notebook, an SVG's ``<style>`` block is page CSS: mermaid's,
    for one, restyles the notebook's own output text (thorwhalen/kroki#1). As an
    image the SVG is a separate document, so its styles (and any script) stay
    inside it.

    A root ``width`` that is relative (mermaid writes ``100%``) gives the image no
    natural width, so the ``viewBox`` width becomes its ``max-width``.

    >>> html = svg_to_img_html('<svg viewBox="0 0 120 40" width="100%"><style>p{}</style></svg>')
    >>> html.startswith('<img src="data:image/svg+xml;base64,')
    True
    >>> 'max-width:120px' in html
    True
    """
    if isinstance(svg, bytes):
        svg = svg.decode("utf-8", errors="replace")
    style = ""
    root = _svg_root_re.search(svg)
    if root:
        width = _root_attr(root.group(0), "width")
        view_box = _root_attr(root.group(0), "viewBox")
        if (width is None or width.strip().endswith("%")) and view_box:
            parts = view_box.replace(",", " ").split()
            if len(parts) == 4:
                style = f' style="max-width:{parts[2]}px;width:100%"'
    data = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f'<img src="data:image/svg+xml;base64,{data}"{style}/>'


class IsolatedSVG(SVG):
    """An IPython ``SVG`` whose HTML representation cannot restyle the page.

    Jupyter frontends (JupyterLab, the classic notebook, VS Code) prefer
    ``text/html`` to ``image/svg+xml``, so they show :func:`svg_to_img_html`'s
    image instead of inlining the SVG. The raw SVG stays available as ``.data``
    and as the ``image/svg+xml`` representation, for exporters that want it.
    """

    def _repr_html_(self):
        return svg_to_img_html(self.data)


def svg_to_scoped_html(svg, *, scope_id: str | None = None) -> str:
    """*svg* inlined, with its CSS confined to it (see :mod:`kroki.scoped_css`).

    The middle ground between :func:`svg_to_img_html` and a plain inline SVG (#8):
    links, ``<title>`` tooltips, selectable text and web fonts work, as inlined,
    while every rule of the SVG's ``<style>`` blocks is rewritten to match only
    inside it, so it cannot restyle the notebook (#1).

    >>> html = svg_to_scoped_html('<svg><style>p{margin:0}</style></svg>', scope_id='k')
    >>> html
    '<svg id="k"><style>#k p{margin:0}</style></svg>'
    """
    from kroki.scoped_css import scope_svg

    if isinstance(svg, bytes):
        svg = svg.decode("utf-8", errors="replace")
    return scope_svg(svg, scope_id)


class ScopedSVG(SVG):
    """An IPython ``SVG`` shown inline, with its CSS scoped to itself (#8).

    Both its HTML and its SVG representations are the scoped SVG, under one id
    fixed for the object, so a frontend that inlines either cannot be restyled.
    """

    @property
    def scope_id(self) -> str:
        from kroki.scoped_css import new_scope_id

        return self.__dict__.setdefault("_scope_id", new_scope_id())

    def _repr_html_(self):
        return svg_to_scoped_html(self.data, scope_id=self.scope_id)

    def _repr_svg_(self):
        return self._repr_html_()


#: Whether SVGs are shown isolated (as an image) when a caller does not say. Set it
#: to ``False`` to inline every SVG of a notebook (``kroki.ISOLATE_SVG = False``),
#: trading the protection of thorwhalen/kroki#1 for interactivity (#7).
ISOLATE_SVG = True

SvgDisplay = Literal["isolate", "inline", "scoped"]
_SVG_DISPLAYS = {"isolate": IsolatedSVG, "inline": SVG, "scoped": ScopedSVG}


def bytes_to_image(
    b: bytes, *, isolate_svg: bool | None = None, svg_display: SvgDisplay | None = None
):
    """A displayable object for diagram bytes: an SVG for SVG bytes, else an Image.

    *svg_display* picks how an SVG is shown:

    - ``"isolate"``: an :class:`IsolatedSVG`, shown as an image so its CSS cannot
      leak into the notebook, but without links, tooltips or text selection;
    - ``"inline"``: the plain ``IPython.display.SVG``, whose links, ``<title>``
      tooltips, selectable text and external fonts work, but whose CSS reaches the
      page;
    - ``"scoped"``: a :class:`ScopedSVG`, inlined with its CSS rewritten to apply
      only inside it, so it keeps the interactivity and does not leak (#8).

    Without *svg_display*, *isolate_svg* chooses between ``"isolate"`` and
    ``"inline"``, and ``None`` for both follows :data:`ISOLATE_SVG`.
    """
    if svg_display is None:
        if isolate_svg is None:
            isolate_svg = ISOLATE_SVG
        svg_display = "isolate" if isolate_svg else "inline"
    if svg_display not in _SVG_DISPLAYS:
        raise ValueError(
            f"svg_display must be one of {sorted(_SVG_DISPLAYS)}, got {svg_display!r}"
        )
    if is_svg(b):
        return _SVG_DISPLAYS[svg_display](b)
    else:
        return Image(b)


diagram_image = wrap(diagram_image_bytes, egress=bytes_to_image)
mermaid_image = wrap(
    partial(diagram_image_bytes, diagram_type="mermaid"), egress=bytes_to_image
)
graphviz_image = wrap(
    partial(diagram_image_bytes, diagram_type="graphviz"), egress=bytes_to_image
)
kroki = diagram_image  # alias

from IPython.core.magic import Magics, cell_magic, magics_class


# see https://kroki.io/examples.html#wbs for working examples


_DISPLAY_FLAGS = {"--inline": "inline", "--isolate": "isolate", "--scoped": "scoped"}


def _parse_magic_line(line: str) -> tuple[list[str], SvgDisplay | None]:
    """Split a ``%%kroki`` line into positional args and the SVG display choice.

    >>> _parse_magic_line("graphviz --inline")
    (['graphviz'], 'inline')
    >>> _parse_magic_line("mermaid svg")
    (['mermaid', 'svg'], None)
    """
    args, display = [], None
    for token in line.split():
        if token in _DISPLAY_FLAGS:
            if display is not None and display != _DISPLAY_FLAGS[token]:
                raise ValueError(
                    f"%%kroki: {', '.join(_DISPLAY_FLAGS)} are exclusive"
                )
            display = _DISPLAY_FLAGS[token]
        elif token.startswith("-"):
            raise ValueError(
                f"Unknown %%kroki option {token!r}; known: {', '.join(_DISPLAY_FLAGS)}"
            )
        else:
            args.append(token)
    return args, display


@magics_class
class KrokiMagic(Magics):
    """``%%kroki [diagram_type] [output_format] [--inline | --isolate | --scoped]``.

    ``--inline`` shows an SVG inlined, so its links, tooltips, selectable text and
    web fonts work, at the cost of letting its CSS restyle the notebook (#7);
    ``--isolate`` forces the safe image display; ``--scoped`` inlines it with its
    CSS confined to it, keeping both (#8). Without any, :data:`ISOLATE_SVG` decides.
    """

    @cell_magic
    def kroki(self, line, cell):
        args, display = _parse_magic_line(line)
        return bytes_to_image(diagram_image_bytes(cell, *args), svg_display=display)


def load_ipython_extension(ipython):
    ipython.register_magics(KrokiMagic)


# --------------------------------------------------------------------------------------

# Miscellaneous notes ------------------------------------------------------------------
# Note: Equivalent to the following, but didn't use to not need i2
# encode_src = Pipe(
#     str.encode,
#     partial(zlib.compress, level=9),
#     base64.urlsafe_b64encode,
#     partial(bytes.decode, encoding='ascii'),
# )
#
# decode_src = Pipe(
#     base64.urlsafe_b64decode, zlib.decompress, partial(bytes.decode, encoding='utf8')
# )
