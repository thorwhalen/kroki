"""Backwards compatible shim for the legacy ``kroki.test`` module.

The tests themselves now live in :mod:`kroki.tests`. They had to move: pytest's
default ``python_files`` patterns are ``test_*.py`` and ``*_test.py``, and the
filename ``test.py`` matches neither, so nothing here was ever collected. The
assertions ran only because ``--doctest-modules`` imports every module under
``testpaths`` and this one called its own test function at import time -- meaning a
regression showed up as a collection error that aborted the entire run, rather than
as one failing test.

This module is kept so that ``from kroki.test import test_code_codecs`` keeps
working. It re-exports from :mod:`kroki.tests.test_codecs`, which does not import
pytest, so importing ``kroki.test`` still requires nothing beyond ``kroki`` itself.
"""

from kroki.tests.test_codecs import test_code_codecs

__all__ = ["test_code_codecs"]
