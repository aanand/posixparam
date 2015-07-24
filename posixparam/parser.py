from __future__ import unicode_literals

from collections import namedtuple
from six.moves import zip as izip
from itertools import count

import re

Token = namedtuple('Token', 'char pos')

Literal = namedtuple('Literal', 'text')
Substitution = namedtuple('Substitution', 'variable_name')

VARIABLE_NAME = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


def lex(text):
    return (
        Token(char, pos)
        for (char, pos) in izip(iter(text), count())
    )


def parse(tokens):
    literal_text = ''

    for token in tokens:
        if token.char == '$':
            if literal_text:
                yield Literal(literal_text)
                literal_text = ''

            substitution = parse_substitution(tokens, token)
            yield substitution
        else:
            literal_text += token.char

    if literal_text:
        yield Literal(literal_text)
        literal_text = ''


def parse_substitution(tokens, last_token):
    try:
        next_token = next(tokens)
    except StopIteration:
        raise PrematureEndOfInput(last_token)

    if next_token.char != '{':
        raise MissingOpeningBrace(next_token.pos)

    last_token = next_token
    opening_brace_position = next_token.pos

    variable_name = ''

    for token in tokens:
        last_token = token

        if token.char == '}':
            if not variable_name:
                raise EmptyVariableName(token.pos)

            if not VARIABLE_NAME.match(variable_name):
                raise InvalidVariableName(
                    opening_brace_position+1, variable_name)

            return Substitution(variable_name)
        else:
            variable_name += token.char

    if variable_name:
        raise MissingClosingBrace(opening_brace_position, last_token.pos + 1)
    else:
        raise PrematureEndOfInput(last_token)


class InternalParseError(Exception):
    pass


class MissingOpeningBrace(InternalParseError):
    def __init__(self, position):
        self.position = position
        self.reason = "Missing opening brace"
        self.points = [position]


class MissingClosingBrace(InternalParseError):
    def __init__(self, opening_brace_position, error_position):
        self.opening_brace_position = opening_brace_position
        self.error_position = error_position

        self.reason = "Opening brace at char {} is " \
                      "missing a closing brace".format(opening_brace_position)

        self.points = [opening_brace_position, error_position]


class PrematureEndOfInput(InternalParseError):
    def __init__(self, last_token):
        self.character = last_token.char
        self.position = last_token.pos + 1
        self.reason = "Input ends abruptly after '{}'".format(self.character)
        self.points = [self.position]


class EmptyVariableName(InternalParseError):
    def __init__(self, position):
        self.position = position
        self.reason = "Empty variable name"
        self.points = [position]


class InvalidVariableName(InternalParseError):
    def __init__(self, position, variable_name):
        self.position = position
        self.variable_name = variable_name
        self.reason = "Invalid variable name '{}'. " \
                      "Names must contain only a-z, A-Z, 0-9 and underscores, " \
                      "and not begin with a digit.".format(variable_name)
        self.points = [position]
