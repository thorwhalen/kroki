"""Tests for the diagram source codecs: :func:`kroki.encode_src` and
:func:`kroki.decode_src`.

This module deliberately does **not** import ``pytest``. The backwards compatible
:mod:`kroki.test` shim re-exports :func:`test_code_codecs` from here, and
``import kroki.test`` has never required anything beyond ``kroki`` itself; keeping
this module pytest-free preserves that.
"""

from kroki import decode_src, encode_src


def test_code_codecs():
    x = "Bob->Alice : Hello!"

    encoded_x = encode_src(x)
    assert encoded_x == "eNpzyk_StXPMyUxOVbBS8EjNyclXBAA7UAXs"

    decoded_x = decode_src(encoded_x)
    assert decoded_x == x


def test_encode_src_is_url_safe():
    """The encoding is spliced straight into a kroki.io URL path, so it must use the
    *url-safe* base64 alphabet (``-`` and ``_``) and never plain base64's ``+`` / ``/``.

    ``=`` padding is allowed: it is a legal character in a URL path segment.
    """
    url_safe_alphabet = set(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_="
    )
    for source in ["Bob->Alice : Hello!", "Bob->Alice : Hello!" * 20, "?&#% /+"]:
        encoded = encode_src(source)
        assert set(encoded) <= url_safe_alphabet, f"unsafe characters in {encoded!r}"


def test_encode_decode_round_trip():
    """``decode_src`` must invert ``encode_src`` for more than just ASCII one-liners."""
    sources = [
        "Bob->Alice : Hello!",
        "",
        "digraph G {\n  a -> b;\n  b -> c;\n}",
        "graph LR\n  A[Café] --> B[naïve]\n  B --> C[日本語]",
        "x" * 10_000,
    ]
    for source in sources:
        assert decode_src(encode_src(source)) == source
