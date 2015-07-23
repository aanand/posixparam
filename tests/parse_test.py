from __future__ import unicode_literals

import pytest

from posixps.sub import (
    lex, parse, parse_substitution,
    Literal, Substitution,
    MissingOpeningBrace,
    MissingClosingBrace,
)


def test_no_subs():
    assert list(parse(lex("hello world"))) == [Literal("hello world")]


def test_simple_sub():
    assert list(parse(lex("hello ${thing}"))) == [
        Literal("hello "),
        Substitution("thing"),
    ]


def test_no_opening_brace():
    with pytest.raises(MissingOpeningBrace) as excinfo:
        list(parse(lex("hello $thing")))

    assert excinfo.value.position == 7


def test_no_closing_brace():
    with pytest.raises(MissingClosingBrace) as excinfo:
        list(parse(lex("hello ${thing")))

    assert excinfo.value.opening_brace_position == 7
    assert excinfo.value.error_position == 13


def test_parse_substitution():
    tokens = lex("{thing}remainder")

    substitution, length = parse_substitution(tokens, 0)

    assert substitution == Substitution("thing")
    assert length == 7
    assert ''.join(tokens) == "remainder"
