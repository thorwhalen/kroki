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

svn_bytes = diagram_image_bytes('Bob->Alice : Hello!')
# which you can then save in a file...
```

When in a jupyter notebook though, you have a more convenient function that will put those bytes into an IPython display object, which you can then display (will automatically call display if it's the last command of the cell), amongst other things.


```python
from kroki import diagram_image

diagram_image('Bob->Alice : Hello!')
```

<img width="123" alt="image" src="https://user-images.githubusercontent.com/1906276/211854316-501ec323-bd26-4428-a722-2fa200bfbea3.png">


In both those functions, the default is `diagram_type='plantuml'` and `output_format='svg'`.

But you have other choices.


```python
diagram_image('digraph D {Alice -> Bob, Charles -> Darwin}', diagram_type='graphviz')
```

<img width="240" alt="image" src="https://user-images.githubusercontent.com/1906276/212101184-376b2565-c241-4bcb-81f9-50c1eb538675.png">


```python
png_bytes = diagram_image_bytes('Bob->Alice : Hello!', output_format='png')
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


To see what diagram types `kroki` supports through the `diagram_types` variable.


```python
from kroki import diagram_types

print(diagram_types)
```

    {'svgbob', 'vega', 'packetdiag', 'mermaid', 'structurizr', 'bytefield', 'vegalite', 'c4plantuml', 'pikchr', 'rackdiag', 'ditaa', 'wavedrom', 'nwdiag', 'graphviz', 'excalidraw', 'plantuml', 'erd', 'umlet', 'actdiag', 'nomnoml', 'bpmn', 'seqdiag', 'blockdiag'}


Not all `output_format` values are supported for all diagram types. To which are supported for which types, you can have a look at the `output_formats` dictionary, which which contains both the choices of diagram_type (as keys) and the corresponding output_format each support (as values).


```python
from kroki import output_formats

output_formats['plantuml']
```


    ['png', 'svg', 'jpeg', 'base64']


```python
output_formats['mermaid']
```




    ['svg']




```python
output_formats['seqdiag']
```




    ['png', 'svg', 'pdf']


