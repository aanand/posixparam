from __future__ import unicode_literals

import pytest

from posixps.parser import (
    lex, parse, parse_substitution,
    Literal, Substitution,
    MissingOpeningBrace,
    MissingClosingBrace,
)


def test_no_subs():
    assert list(parse(lex("hello world"))) == [Literal("hello world")]


def test_simple_subs():
    assert list(parse(lex("${thing}"))) == [
        Substitution("thing"),
    ]

    assert list(parse(lex("${subject} love you"))) == [
        Substitution("subject"),
        Literal(" love you"),
    ]

    assert list(parse(lex("i ${verb} you"))) == [
        Literal("i "),
        Substitution("verb"),
        Literal(" you"),
    ]

    assert list(parse(lex("i love ${object}"))) == [
        Literal("i love "),
        Substitution("object"),
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
