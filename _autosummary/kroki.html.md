# kroki

Kroki from python

### Module Attributes

| [`ISOLATE_SVG`](#kroki.ISOLATE_SVG)   | Whether SVGs are shown isolated (as an image) when a caller does not say.   |
|----------------------------------------------------------------|-----------------------------------------------------------------------------|

### Functions

| [`bytes_to_image`](#kroki.bytes_to_image)(b, \*[, isolate_svg])       | A displayable object for diagram bytes: an SVG for SVG bytes, else an Image.   |
|---------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| [`decode_src`](#kroki.decode_src)(encoded_diagram_source)         | Decode a diagram source string from a base64 string.                           |
| [`diagram_image_bytes`](#kroki.diagram_image_bytes)([diagram_source, ...]) | Get the bytes of a diagram image.                                              |
| [`encode_src`](#kroki.encode_src)(diagram_source)                 | Encode a diagram source string into a base64 string that can be used in a URL. |
| `is_svg`(b)                                                                                 |                                                                                |
| `load_ipython_extension`(ipython)                                                           |                                                                                |
| [`svg_to_img_html`](#kroki.svg_to_img_html)(svg)                       | An `<img>` showing *svg* as its own document.                                  |

### Classes

| [`IsolatedSVG`](#kroki.IsolatedSVG)([data, url, filename, metadata])   | An IPython `SVG` whose HTML representation cannot restyle the page.   |
|-------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| [`KrokiMagic`](#kroki.KrokiMagic)([shell])                            | `%%kroki [diagram_type] [output_format] [--inline | --isolate]`.      |

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

`%%kroki [diagram_type] [output_format] [--inline | --isolate]`.

`--inline` shows an SVG inlined, so its links, tooltips, selectable text and
web fonts work, at the cost of letting its CSS restyle the notebook (#7);
`--isolate` forces the safe image display. Without either, [`ISOLATE_SVG`](#kroki.ISOLATE_SVG)
decides.

### kroki.bytes_to_image(b, , isolate_svg=None)

A displayable object for diagram bytes: an SVG for SVG bytes, else an Image.

Isolated, an SVG is an [`IsolatedSVG`](#kroki.IsolatedSVG), shown as an image so its CSS cannot
leak into the notebook. Inlined (`isolate_svg=False`), it is the plain
`IPython.display.SVG`: its CSS reaches the page, but its links, `<title>`
tooltips, selectable text and external fonts work. `None` (the default)
follows [`ISOLATE_SVG`](#kroki.ISOLATE_SVG).

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

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

```pycon
>>> html = svg_to_img_html('<svg viewBox="0 0 120 40" width="100%"><style>p{}</style></svg>')
>>> html.startswith('<img src="data:image/svg+xml;base64,')
True
>>> 'max-width:120px' in html
True
```

### Modules

| [`test`](kroki.test.html.md#module-kroki.test)   | Backwards compatible shim for the legacy `kroki.test` module.   |
|---------------------------------------------------------------------------|-----------------------------------------------------------------|
