# kroki

Access [kroki](https://kroki.io/) from python. 

To install:	```pip install kroki```

Read the overview below, or
view/download/play [this demo notebook](https://github.com/thorwhalen/kroki/blob/main/misc/kroki%20demo.ipynb) 
to see how to use this package.

The `kroki` python package is a convenience package for you to be able to generate diagrams, 
through [kroki](https://kroki.io/), getting your images as bytes or as ipython objects via python 
functions or doing some "cell magic" in your jupyter notebooks.

I suggest you have a look at the [kroki's excellent homepage](https://kroki.io/) 
where you'll be able to try different diagram types out. 
Don't miss the nice [cheatsheet](https://kroki.io/assets/kroki_cheatsheet_20210515_v1.1_EN.pdf) there.


# Overview

You can get the bytes of an image of a diagram like so:

```python
from kroki import diagram_image_bytes

svn_bytes = diagram_image_bytes("Bob->Alice : Hello!")
# which you can then save in a file...
```

When in a jupyter notebook though, you have a more convenient function that will put those bytes into an IPython display object, which you can then display (will automatically call display if it's the last command of the cell), amongst other things.


```python
from kroki import diagram_image

diagram_image("Bob->Alice : Hello!")
```

<img width="123" alt="image" src="https://user-images.githubusercontent.com/1906276/211854316-501ec323-bd26-4428-a722-2fa200bfbea3.png">


In both those functions, the default is `diagram_type='plantuml'` and `output_format='svg'`.

But you have other choices.


```python
diagram_image("digraph D {Alice -> Bob, Charles -> Darwin}", diagram_type="graphviz")
```

<img width="240" alt="image" src="https://user-images.githubusercontent.com/1906276/212101184-376b2565-c241-4bcb-81f9-50c1eb538675.png">


```python
png_bytes = diagram_image_bytes("Bob->Alice : Hello!", output_format="png")
png_bytes[:7]
```


    b'\x89PNG\r\n\x1a'


And then, there's magic, which will allow you to write your diagram source directly in a notebook's cell.


```python
%load_ext kroki
```


```python
%%kroki

Bob->Alice : Hello!
```

<img width="123" alt="image" src="https://user-images.githubusercontent.com/1906276/211854316-501ec323-bd26-4428-a722-2fa200bfbea3.png">


The default `diagram_type` is still `plantuml`, but you can specify another type if you want.


```python
%%kroki graphviz

digraph D {
    Alice -> Bob, Charles -> Darwin
}
```

<img width="240" alt="image" src="https://user-images.githubusercontent.com/1906276/212101184-376b2565-c241-4bcb-81f9-50c1eb538675.png">


SVG diagrams are shown as an image (`<img src="data:image/svg+xml;...">`) rather than inlined into the page. An inlined SVG's `<style>` block is page CSS, and mermaid's would otherwise restyle the notebook's own output text, e.g. turning it dark gray in dark mode. The raw SVG is still there, as `.data` on the returned object; `kroki.bytes_to_image(svg_bytes, isolate_svg=False)` gives the old inlined display.

The image costs the SVG's interactivity: no links, no `<title>` tooltips, no text selection, and no web fonts. When you need those and trust the diagram's CSS, inline it: `%%kroki graphviz --inline` for one cell, or `kroki.ISOLATE_SVG = False` for every diagram in the notebook (then `--isolate` forces the image again). From Python, `kroki.bytes_to_image(svg_bytes, isolate_svg=False)` does the same.

A third mode keeps the interactivity without the leak: `%%kroki mermaid --scoped` (or `bytes_to_image(svg_bytes, svg_display="scoped")`) inlines the SVG, but rewrites every rule of its `<style>` blocks to apply only inside the diagram. It gives the SVG root a random id and prefixes each selector with it. A leading `:root`, `html`, `body` or `svg`, and mermaid's own `#mermaid-N` selectors, become that root. `@media` and `@supports` blocks are scoped inside, and `@font-face` and `@keyframes` are kept as they are. `@import` and `@page` are dropped, because neither can be scoped. The rewrite works on CSS tokens (`kroki.scoped_css`), not on regular expressions.

To see what diagram types `kroki` supports through the `diagram_types` variable.


```python
from kroki import diagram_types

print(diagram_types)
```

    {'svgbob', 'vega', 'packetdiag', 'mermaid', 'structurizr', 'bytefield', 'vegalite', 'c4plantuml', 'pikchr', 'rackdiag', 'ditaa', 'wavedrom', 'nwdiag', 'graphviz', 'excalidraw', 'plantuml', 'erd', 'umlet', 'actdiag', 'nomnoml', 'bpmn', 'seqdiag', 'blockdiag'}


Not all `output_format` values are supported for all diagram types. To which are supported for which types, you can have a look at the `output_formats` dictionary, which which contains both the choices of diagram_type (as keys) and the corresponding output_format each support (as values).


```python
from kroki import output_formats

output_formats["plantuml"]
```


    ['png', 'svg', 'jpeg', 'base64']


```python
output_formats["mermaid"]
```



    ['svg']




```python
output_formats["seqdiag"]
```


    ['png', 'svg', 'pdf']



# Misc

The `kroki` function is just an alias of `diagram_image` which itself, is the composition of `diagram_image_bytes` and `bytes_to_image` to get an iPython image object as your output (which results in displaying the image when it's the last command of your cell). 

The default `diagram_type` of `diagram_image` is `plantuml`. 
We also made some ready-to-use `mermaid_image` and `graphviz_image` by fixing `diagram_type` with `functools.partial`. 

```python
diagram_image = wrap(diagram_image_bytes, egress=bytes_to_image)
mermaid_image = wrap(
    partial(diagram_image_bytes, diagram_type="mermaid"), egress=bytes_to_image
)
graphviz_image = wrap(
    partial(diagram_image_bytes, diagram_type="graphviz"), egress=bytes_to_image
)
kroki = diagram_image  # alias
```

You can import these directory from `kroki`.