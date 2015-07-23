from __future__ import unicode_literals

import pytest

from posixparam import sub, ParseError


def test_no_subs():
    assert sub("hello world") == "hello world"


def test_simple_sub():
    assert sub("hello ${thing}", thing="world") == "hello world"


def test_no_value():
    assert sub("${thing}") == ""


def test_binary_value():
    assert sub(
        u"\U0001F630${thing}\U0001F630",
        thing=b"\xF0\x9F\x98\x81",
    ) == u"\U0001F630\U0001F601\U0001F630"


def test_binary_input():
    assert sub(
        b"\xF0\x9F\x98\xB0${thing}\xF0\x9F\x98\xB0",
        thing=u"\U0001F601",
    ) == u"\U0001F630\U0001F601\U0001F630"


def test_binary_value_and_input():
    assert sub(
        b"\xF0\x9F\x98\xB0${thing}\xF0\x9F\x98\xB0",
        thing=b"\xF0\x9F\x98\x81",
    ) == u"\U0001F630\U0001F601\U0001F630"


def test_non_string_values():
    with pytest.raises(ValueError):
        print(repr(sub("${thing}", thing=1)))

    with pytest.raises(ValueError):
        print(repr(sub("${thing}", thing=1.5)))

    with pytest.raises(ValueError):
        print(repr(sub("${thing}", thing=None)))


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
