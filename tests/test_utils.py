from __future__ import unicode_literals

from easysnmp.compat import ub
from easysnmp.utils import strip_non_printable, tostr


def test_strip_non_printable_regular():
    assert strip_non_printable("hello there") == "hello there"


def test_strip_non_printable_contains_binary():
    assert strip_non_printable(ub(chr(20)) + "my thingo" + ub(chr(155))) == (
        "my thingo (contains binary)"
    )


def test_strip_non_printable_only_binary():
    assert strip_non_printable(ub(chr(20)) + ub(chr(155))) == ("(contains binary)")


def test_tostr_none():
    assert tostr(None) is None


def test_tostr_string():
    assert tostr("hello there") == "hello there"


def test_tostr_integer():
    assert tostr(1234) == "1234"
