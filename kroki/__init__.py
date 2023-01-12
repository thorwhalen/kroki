"""Kroki from python"""

import base64, zlib
from functools import partial
from itertools import chain
from typing import Literal
import re

import requests
from IPython.display import Image, SVG, display

from i2 import validate_literal, wrap, Pipe

_ascii_decode = partial(bytes.decode, encoding='ascii')
_utf8_decode = partial(bytes.decode, encoding='utf-8')
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
        base64.urlsafe_b64encode(
            _zlib_compress_level_9(
                str.encode(diagram_source)
            )
        )
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
        zlib.decompress(
            base64.urlsafe_b64decode(encoded_diagram_source)
        )
    )


# The output formats supported by each diagram type.
# More precisely, a dictionary, which contains both the choices of diagram_type (as
# keys) and the corresponding output_format each support (as values).
output_formats = {
    'blockdiag': ['png', 'svg', 'pdf'],
    'bpmn': ['svg'],
    'bytefield': ['svg'],
    'seqdiag': ['png', 'svg', 'pdf'],
    'actdiag': ['png', 'svg', 'pdf'],
    'nwdiag': ['png', 'svg', 'pdf'],
    'packetdiag': ['png', 'svg', 'pdf'],
    'rackdiag': ['png', 'svg', 'pdf'],
    'c4plantuml': ['png', 'svg', 'jpeg', 'base64'],  # manually replaced c4withplantuml
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
diagram_types = set(output_formats)


# TODO: Way to avoid dunder __getitem__ in the following:
DiagramKindOptions = Literal.__getitem__(tuple(sorted(diagram_types)))
OutputFormatOptions = Literal.__getitem__(
    tuple(sorted(set(chain.from_iterable(output_formats.values()))))
)

url_template = 'https://kroki.io/{diagram_type}/{output_format}/{diagram_source}'


@validate_literal
def diagram_image_bytes(
    diagram_source: str = 'Bob->Alice : Hello!',
    diagram_type: DiagramKindOptions = 'plantuml',
    output_format: OutputFormatOptions = 'svg',
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
        diagram_source=encode_src(diagram_source)
    )
    r = requests.get(url)
    if r.status_code == 200:
        return r.content
    else:
        # TODO: Do r.raise_for_status() instead?
        raise RuntimeError(
            f'Request returned with an error code {r.status_code}. Content: \n{r.content}'
        )

svg_re = r'(?:<\?xml\b[^>]*>[^<]*)?(?:<!--.*?-->[^<]*)*(?:<svg|<!DOCTYPE svg)\b'
svg_re = re.compile(svg_re.encode(), re.DOTALL)


def is_svg(b: bytes):
    return bool(svg_re.match(b))


def bytes_to_image(b: bytes):

    if is_svg(b):
        return SVG(b)
    else:
        return Image(b)


diagram_image = wrap(diagram_image_bytes, egress=bytes_to_image)


from IPython.core.magic import Magics, cell_magic, magics_class


# see https://kroki.io/examples.html#wbs for working examples

@magics_class
class KrokiMagic(Magics):

    @cell_magic
    def kroki(self, line, cell):
        return diagram_image(cell, *line.split())


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
