"""Test suite for :mod:`kroki`.

The tests live in this subpackage, rather than in the legacy ``kroki/test.py``,
because pytest's default ``python_files`` patterns are ``test_*.py`` and
``*_test.py`` -- and the filename ``test.py`` matches neither. Nothing there was
ever collected; the assertions ran only because ``--doctest-modules`` *imports*
every module under ``testpaths`` and that module called its own test function at
import time. A regression therefore surfaced as a collection error that aborted
the whole run, instead of as a single failing test.

Every test in this package is offline: none of them performs an HTTP request.
"""
