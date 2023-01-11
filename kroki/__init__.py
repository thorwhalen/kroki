"""Kroki from python"""

import base64, zlib
from functools import partial
from i2 import Pipe

encode_code = Pipe(
    str.encode,
    partial(zlib.compress, level=9),
    base64.urlsafe_b64encode,
    partial(bytes.decode, encoding='ascii'),
)

decode_code = Pipe(
    base64.urlsafe_b64decode, zlib.decompress, partial(bytes.decode, encoding='utf8')
)


def test_code_codecs():
    x = 'Bob->Alice : Hello!'

    encoded_x = encode_code(x)
    assert encoded_x == 'eNpzyk_StXPMyUxOVbBS8EjNyclXBAA7UAXs'

    decoded_x = decode_code(encoded_x)
    assert decoded_x == x


test_code_codecs()

from itertools import chain
from typing import Literal

output_formats = {
    'blockdiag': ['png', 'svg', 'pdf'],
    'bpmn': ['svg'],
    'bytefield': ['svg'],
    'seqdiag': ['png', 'svg', 'pdf'],
    'actdiag': ['png', 'svg', 'pdf'],
    'nwdiag': ['png', 'svg', 'pdf'],
    'packetdiag': ['png', 'svg', 'pdf'],
    'rackdiag': ['png', 'svg', 'pdf'],
    'c4plantuml': ['png', 'svg', 'jpeg', 'base64'],  # manutally replaced c4withplantuml
    'ditaa': ['png', 'svg'],
    'erd': ['png', 'svg', 'jpeg', 'pdf'],
    'excalidraw': ['svg'],
    'graphviz': ['png', 'svg', 'jpeg', 'pdf'],
    'mermaid': ['svg'],
    'nomnoml': ['svg'],
    'pikchr': ['svg'],
    'plantuml': ['png', 'svg', 'jpeg', 'base64'],
    'structurizr': ['svg'],
    'svgbob': ['svg'],
    'umlet': ['png', 'svg', 'jpeg'],
    'vega': ['png', 'svg', 'pdf'],
    'vegalite': ['png', 'svg', 'pdf'],
    'wavedrom': ['svg'],
}

# TODO: Way to avoid dunder __getitem__ in the following:
DiagramKindOptions = Literal.__getitem__(tuple(sorted(output_formats)))
OutputFormatOptions = Literal.__getitem__(
    tuple(sorted(set(chain.from_iterable(output_formats.values()))))
)

url_template = 'https://kroki.io/{diagram_kind}/{output_format}/{code}'


def get_diagram_image_bytes(
    code: str = 'Bob->Alice : Hello!',
    diagram_kind: DiagramKindOptions = 'plantuml',
    output_format: OutputFormatOptions = 'svg',
):
    import requests

    url = url_template.format(
        diagram_kind=diagram_kind, output_format=output_format, code=encode_code(code)
    )
    r = requests.get(url)
    if r.status_code == 200:
        return r.content
    else:
        # TODO: Do r.raise_for_status() instead?
        raise RuntimeError(
            f'Request returned with an error code {r.status_code}. Content: \n{r.content}'
        )


import re
from i2 import wrap
from IPython.display import Image, SVG

svg_re = r'(?:<\?xml\b[^>]*>[^<]*)?(?:<!--.*?-->[^<]*)*(?:<svg|<!DOCTYPE svg)\b'
svg_re = re.compile(svg_re.encode(), re.DOTALL)


def is_svg(b: bytes):
    return bool(svg_re.match(b))


def bytes_to_image(b: bytes):

    if is_svg(b):
        return SVG(b)
    else:
        return Image(b)


get_diagram_image = wrap(get_diagram_image_bytes, egress=bytes_to_image)
