# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest

from posixparam.parser import (
    lex, Token,
    parse, parse_substitution,
    Literal, Substitution,
    MissingOpeningBrace,
    MissingClosingBrace,
    PrematureEndOfInput,
    EmptyVariableName,
    InvalidVariableName,
)


def test_empty_string():
    assert list(parse(lex(""))) == []


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

    with pytest.raises(MissingOpeningBrace) as excinfo:
        list(parse(lex("hello $$")))

    assert excinfo.value.position == 7

    with pytest.raises(MissingOpeningBrace) as excinfo:
        list(parse(lex("hello $}")))

    assert excinfo.value.position == 7


def test_no_closing_brace():
    with pytest.raises(MissingClosingBrace) as excinfo:
        list(parse(lex("hello ${thing")))

    assert excinfo.value.opening_brace_position == 7
    assert excinfo.value.error_position == 13


def test_premature_end_of_input():
    with pytest.raises(PrematureEndOfInput) as excinfo:
        list(parse(lex("hello $")))

    assert excinfo.value.character == '$'
    assert excinfo.value.position == 7

    with pytest.raises(PrematureEndOfInput) as excinfo:
        print(list(parse(lex("hello ${"))))

    assert excinfo.value.character == '{'
    assert excinfo.value.position == 8


def test_empty_variable_name():
    with pytest.raises(EmptyVariableName) as excinfo:
        list(parse(lex("hello ${}")))

    assert excinfo.value.position == 8


def test_valid_variable_name():
    assert next(parse(lex("${foo}"))) == Substitution("foo")
    assert next(parse(lex("${foo_bar}"))) == Substitution("foo_bar")
    assert next(parse(lex("${foo_bar_1}"))) == Substitution("foo_bar_1")
    assert next(parse(lex("${_foo_bar_1}"))) == Substitution("_foo_bar_1")
    assert next(parse(lex("${_foo_bar_1_}"))) == Substitution("_foo_bar_1_")

    assert next(parse(lex("${FOO}"))) == Substitution("FOO")
    assert next(parse(lex("${FOO_BAR}"))) == Substitution("FOO_BAR")
    assert next(parse(lex("${FOO_BAR_1}"))) == Substitution("FOO_BAR_1")
    assert next(parse(lex("${_FOO_BAR_1}"))) == Substitution("_FOO_BAR_1")
    assert next(parse(lex("${_FOO_BAR_1_}"))) == Substitution("_FOO_BAR_1_")

    assert next(parse(lex("${fooBar}"))) == Substitution("fooBar")
    assert next(parse(lex("${fooBar1}"))) == Substitution("fooBar1")
    assert next(parse(lex("${_fooBar1}"))) == Substitution("_fooBar1")
    assert next(parse(lex("${_fooBar1_}"))) == Substitution("_fooBar1_")

    assert next(parse(lex("${_1}"))) == Substitution("_1")
    assert next(parse(lex("${_1_}"))) == Substitution("_1_")


def test_invalid_variable_name():
    with pytest.raises(InvalidVariableName) as excinfo:
        next(parse(lex("${123}")))
    assert excinfo.value.position == 2

    with pytest.raises(InvalidVariableName) as excinfo:
        next(parse(lex("${123}")))
    assert excinfo.value.variable_name == '123'

    with pytest.raises(InvalidVariableName) as excinfo:
        next(parse(lex("${1foo}")))
    assert excinfo.value.variable_name == '1foo'

    with pytest.raises(InvalidVariableName) as excinfo:
        next(parse(lex("${1_}")))
    assert excinfo.value.variable_name == '1_'

    with pytest.raises(InvalidVariableName) as excinfo:
        next(parse(lex("${!}")))
    assert excinfo.value.variable_name == '!'

    with pytest.raises(InvalidVariableName) as excinfo:
        next(parse(lex("${gegenüber}")))
    assert excinfo.value.variable_name == 'gegenüber'

    with pytest.raises(InvalidVariableName) as excinfo:
        next(parse(lex("${ foo }")))
    assert excinfo.value.variable_name == ' foo '


def test_parse_substitution():
    tokens = lex("{thing}remainder")

    assert parse_substitution(tokens, Token('$', 0)) == Substitution("thing")
    assert ''.join(char for (char, _) in tokens) == "remainder"


def test_escape_dollar():
    strings = [
        "\\${subject} love you",
        "i \\${verb} you",
        "i love \\${object}",
        "hello \\$",
        "hello \\$\\$",
        "hello \\${",
        "hello \\${thing",
        "hello \\$}",
        "hello \\${}",
        "hello \\${123}",
    ]

    for string in strings:
        assert next(parse(lex(string))) == Literal(string)


def test_backslash_in_literal():
    assert list(parse(lex("i\\ ${verb} you"))) == [
        Literal("i\\ "),
        Substitution("verb"),
        Literal(" you"),
    ]

    assert list(parse(lex("i love ${object}\\"))) == [
        Literal("i love "),
        Substitution("object"),
        Literal("\\"),
    ]


def test_invalid_escape():
    with pytest.raises(MissingOpeningBrace) as excinfo:
        next(parse(lex("$\\{thing}")))
    assert excinfo.value.position == 1

    with pytest.raises(InvalidVariableName) as excinfo:
        next(parse(lex("${thing\\}")))
    assert excinfo.value.position == 2
    assert excinfo.value.variable_name == 'thing\\'

    with pytest.raises(InvalidVariableName) as excinfo:
        next(parse(lex("${th\\ing}")))
    assert excinfo.value.position == 2
