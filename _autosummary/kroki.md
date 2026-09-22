# kroki

Kroki from python

### Functions

| `bytes_to_image`(b)                                                                         |                                                                                |
|---------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| [`decode_src`](#kroki.decode_src)(encoded_diagram_source)         | Decode a diagram source string from a base64 string.                           |
| [`diagram_image_bytes`](#kroki.diagram_image_bytes)([diagram_source, ...]) | Get the bytes of a diagram image.                                              |
| [`encode_src`](#kroki.encode_src)(diagram_source)                 | Encode a diagram source string into a base64 string that can be used in a URL. |
| `is_svg`(b)                                                                                 |                                                                                |
| `load_ipython_extension`(ipython)                                                           |                                                                                |

### Classes

| [`KrokiMagic`](#kroki.KrokiMagic)([shell])   |    |
|------------------------------------------------------------------------|----|

### *class* kroki.KrokiMagic(shell=None, \*\*kwargs)

Bases: `Magics`

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

### Modules

| [`test`](kroki.test.md#module-kroki.test)   | Backwards compatible shim for the legacy `kroki.test` module.   |
|---------------------------------------------------------------------------|-----------------------------------------------------------------|
