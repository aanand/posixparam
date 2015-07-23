from __future__ import unicode_literals

import pytest

from posixps.sub import lex, parse, Literal, Substitution, ParseError


def test_no_subs():
    assert(list(parse(lex("hello world"))) == [Literal("hello world")])


def test_simple_sub():
    assert(list(parse(lex("hello ${thing}"))) == [
        Literal("hello "),
        Substitution("thing"),
    ])


def test_no_opening_brace():
    with pytest.raises(ParseError):
        list(parse(lex("hello $thing")))

    with pytest.raises(ParseError):
        list(parse(lex("hello $thing}")))


def test_no_closing_brace():
    with pytest.raises(ParseError):
        list(parse(lex("hello ${thing")))
