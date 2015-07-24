from __future__ import unicode_literals

from collections import namedtuple
from six.moves import zip as izip
from itertools import count

Token = namedtuple('Token', 'char pos')

Literal = namedtuple('Literal', 'text')
Substitution = namedtuple('Substitution', 'variable_name')


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

            substitution = parse_substitution(tokens)
            yield substitution
        else:
            literal_text += token.char

    if literal_text:
        yield Literal(literal_text)
        literal_text = ''


def parse_substitution(tokens):
    next_token = next(tokens)
    if next_token.char != '{':
        raise MissingOpeningBrace(next_token.pos)

    opening_brace_position = next_token.pos
    current_position = next_token.pos

    variable_name = ''

    for token in tokens:
        current_position = token.pos
        if token.char == '}':
            return Substitution(variable_name)
        else:
            variable_name += token.char

    if variable_name:
        raise MissingClosingBrace(opening_brace_position, current_position+1)


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
