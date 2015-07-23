from __future__ import unicode_literals

from posixps.sub import lex, parse, Literal, Substitution


def test_no_subs():
    assert(list(parse(lex("hello world"))) == [Literal("hello world")])


def test_simple_sub():
    assert(list(parse(lex("hello ${thing}"))) == [
        Literal("hello "),
        Substitution("thing"),
    ])

