# kroki

Kroki from python

### Module Attributes

| [`ISOLATE_SVG`](#kroki.ISOLATE_SVG)   | Whether SVGs are shown isolated (as an image) when a caller does not say.   |
|----------------------------------------------------------------|-----------------------------------------------------------------------------|

### Functions

| [`bytes_to_image`](#kroki.bytes_to_image)(b, \*[, isolate_svg, svg_display])   | A displayable object for diagram bytes: an SVG for SVG bytes, else an Image.                                                                |
|------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| [`decode_src`](#kroki.decode_src)(encoded_diagram_source)                  | Decode a diagram source string from a base64 string.                                                                                        |
| [`diagram_image_bytes`](#kroki.diagram_image_bytes)([diagram_source, ...])          | Get the bytes of a diagram image.                                                                                                           |
| [`encode_src`](#kroki.encode_src)(diagram_source)                          | Encode a diagram source string into a base64 string that can be used in a URL.                                                              |
| `is_svg`(b)                                                                                          |                                                                                                                                             |
| `load_ipython_extension`(ipython)                                                                    |                                                                                                                                             |
| [`svg_to_img_html`](#kroki.svg_to_img_html)(svg)                                | An `<img>` showing *svg* as its own document.                                                                                               |
| [`svg_to_scoped_html`](#kroki.svg_to_scoped_html)(svg, \*[, scope_id])             | *svg* inlined, with its CSS confined to it (see [`kroki.scoped_css`](kroki.scoped_css.html.md#module-kroki.scoped_css)). |

### Classes

| [`IsolatedSVG`](#kroki.IsolatedSVG)([data, url, filename, metadata])   | An IPython `SVG` whose HTML representation cannot restyle the page.         |
|-------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| [`KrokiMagic`](#kroki.KrokiMagic)([shell])                            | `%%kroki [diagram_type] [output_format] [--inline | --isolate | --scoped]`. |
| [`ScopedSVG`](#kroki.ScopedSVG)([data, url, filename, metadata])     | An IPython `SVG` shown inline, with its CSS scoped to itself (#8).          |

### kroki.ISOLATE_SVG *= True*

Whether SVGs are shown isolated (as an image) when a caller does not say. Set it
to `False` to inline every SVG of a notebook (`kroki.ISOLATE_SVG = False`),
trading the protection of thorwhalen/kroki#1 for interactivity (#7).

### *class* kroki.IsolatedSVG(data=None, url=None, filename=None, metadata=None)

Bases: `SVG`

An IPython `SVG` whose HTML representation cannot restyle the page.

Jupyter frontends (JupyterLab, the classic notebook, VS Code) prefer
`text/html` to `image/svg+xml`, so they show [`svg_to_img_html()`](#kroki.svg_to_img_html)’s
image instead of inlining the SVG. The raw SVG stays available as `.data`
and as the `image/svg+xml` representation, for exporters that want it.

### *class* kroki.KrokiMagic(shell=None, \*\*kwargs)

Bases: `Magics`

`%%kroki [diagram_type] [output_format] [--inline | --isolate | --scoped]`.

`--inline` shows an SVG inlined, so its links, tooltips, selectable text and
web fonts work, at the cost of letting its CSS restyle the notebook (#7);
`--isolate` forces the safe image display; `--scoped` inlines it with its
CSS confined to it, keeping both (#8). Without any, [`ISOLATE_SVG`](#kroki.ISOLATE_SVG) decides.

### *class* kroki.ScopedSVG(data=None, url=None, filename=None, metadata=None)

Bases: `SVG`

An IPython `SVG` shown inline, with its CSS scoped to itself (#8).

Both its HTML and its SVG representations are the scoped SVG, under one id
fixed for the object, so a frontend that inlines either cannot be restyled.

### kroki.bytes_to_image(b, , isolate_svg=None, svg_display=None)

A displayable object for diagram bytes: an SVG for SVG bytes, else an Image.

*svg_display* picks how an SVG is shown:

- `"isolate"`: an [`IsolatedSVG`](#kroki.IsolatedSVG), shown as an image so its CSS cannot
  leak into the notebook, but without links, tooltips or text selection;
- `"inline"`: the plain `IPython.display.SVG`, whose links, `<title>`
  tooltips, selectable text and external fonts work, but whose CSS reaches the
  page;
- `"scoped"`: a [`ScopedSVG`](#kroki.ScopedSVG), inlined with its CSS rewritten to apply
  only inside it, so it keeps the interactivity and does not leak (#8).

Without *svg_display*, *isolate_svg* chooses between `"isolate"` and
`"inline"`, and `None` for both follows [`ISOLATE_SVG`](#kroki.ISOLATE_SVG).

### kroki.decode_src(encoded_diagram_source)

Decode a diagram source string from a base64 string.

* **Parameters:**
  **encoded_diagram_source** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – The encoded diagram source string.
* **Returns:**
  The decoded string.

```pycon
>>> decode_src('eNpzyk_StXPMyUxOVbBS8EjNyclXBAA7UAXs')
'Bob->Alice : Hello!'
```

### kroki.diagram_image_bytes(diagram_source='Bob->Alice : Hello!', diagram_type='plantuml', output_format='svg')

Get the bytes of a diagram image.

* **Parameters:**
  * **diagram_source** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – The diagram source string.
  * **diagram_type** ([`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal)[`'actdiag'`, `'blockdiag'`, `'bpmn'`, `'bytefield'`, `'c4plantuml'`, `'d2'`, `'dbml'`, `'ditaa'`, `'erd'`, `'excalidraw'`, `'graphviz'`, `'mermaid'`, `'nomnoml'`, `'nwdiag'`, `'packetdiag'`, `'pikchr'`, `'plantuml'`, `'rackdiag'`, `'seqdiag'`, `'structurizr'`, `'svgbob'`, `'symbolator'`, `'tikz'`, `'umlet'`, `'vega'`, `'vegalite'`, `'wavedrom'`, `'wireviz'`]) – The diagram type.
  * **output_format** ([`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal)[`'base64'`, `'jpeg'`, `'pdf'`, `'png'`, `'svg'`, `'txt'`]) – The output format.
* **Returns:**
  The bytes of the diagram image.

### kroki.encode_src(diagram_source)

Encode a diagram source string into a base64 string that can be used in a URL.

* **Parameters:**
  **diagram_source** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – The diagram source string.
* **Returns:**
  The encoded string.

```pycon
>>> encode_src('Bob->Alice : Hello!')
'eNpzyk_StXPMyUxOVbBS8EjNyclXBAA7UAXs'
```

### kroki.svg_to_img_html(svg)

An `<img>` showing *svg* as its own document.

Inlined into a notebook, an SVG’s `<style>` block is page CSS: mermaid’s,
for one, restyles the notebook’s own output text (thorwhalen/kroki#1). As an
image the SVG is a separate document, so its styles (and any script) stay
inside it.

A root `width` that is relative (mermaid writes `100%`) gives the image no
natural width, so the `viewBox` width becomes its `max-width`.

```pycon
>>> html = svg_to_img_html('<svg viewBox="0 0 120 40" width="100%"><style>p{}</style></svg>')
>>> html.startswith('<img src="data:image/svg+xml;base64,')
True
>>> 'max-width:120px' in html
True
```

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### kroki.svg_to_scoped_html(svg, , scope_id=None)

*svg* inlined, with its CSS confined to it (see [`kroki.scoped_css`](kroki.scoped_css.html.md#module-kroki.scoped_css)).

The middle ground between [`svg_to_img_html()`](#kroki.svg_to_img_html) and a plain inline SVG (#8):
links, `<title>` tooltips, selectable text and web fonts work, as inlined,
while every rule of the SVG’s `<style>` blocks is rewritten to match only
inside it, so it cannot restyle the notebook (#1).

```pycon
>>> html = svg_to_scoped_html('<svg><style>p{margin:0}</style></svg>', scope_id='k')
>>> html
'<svg id="k"><style>#k p{margin:0}</style></svg>'
```

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### Modules

| [`scoped_css`](kroki.scoped_css.html.md#module-kroki.scoped_css)   | Scope a stylesheet to one element, so an inlined SVG's CSS cannot restyle the page.   |
|---------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| [`test`](kroki.test.html.md#module-kroki.test)               | Backwards compatible shim for the legacy `kroki.test` module.                         |
