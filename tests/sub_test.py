from __future__ import unicode_literals

import pytest

from posixps import sub, ParseError


def test_no_subs():
    assert(sub("hello world") == "hello world")


def test_simple_sub():
    assert(sub("hello ${thing}", thing="world") == "hello world")


def test_no_opening_brace():
    with pytest.raises(ParseError) as excinfo:
        sub("hello $thing")

    assert excinfo.value.reason == "Missing opening brace"
    assert excinfo.value.diagram == \
        "hello $thing\n" \
        "-------^"


def test_no_closing_brace():
    with pytest.raises(ParseError) as excinfo:
        sub("hello ${thing")

    assert excinfo.value.reason == "Opening brace at char 7 is missing a closing brace"
    assert excinfo.value.diagram == \
        "hello ${thing\n" \
        "-------^-----^"
