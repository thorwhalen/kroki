"""kroki tests"""

from kroki import encode_src, decode_src


def test_code_codecs():
    x = 'Bob->Alice : Hello!'

    encoded_x = encode_src(x)
    assert encoded_x == 'eNpzyk_StXPMyUxOVbBS8EjNyclXBAA7UAXs'

    decoded_x = decode_src(encoded_x)
    assert decoded_x == x


test_code_codecs()