from __future__ import unicode_literals

from collections import namedtuple


Literal = namedtuple('Literal', 'text')
Substitution = namedtuple('Substitution', 'variable_name')


def sub(text, **variables):
    tokens = lex(text)
    nodes = parse(tokens)
    chunks = perform_substitutions(nodes, variables)
    return ''.join(chunks)


def lex(text):
    return (c for c in text)


def parse(tokens):
    literal_text = ''

    for char in tokens:
        if char == '$':
            if literal_text:
                yield Literal(literal_text)
                literal_text = ''

            yield parse_substitution(tokens)
        else:
            literal_text += char

    if literal_text:
        yield Literal(literal_text)
        literal_text = ''


def parse_substitution(tokens):
    opening_brace = next(tokens)
    if opening_brace != '{':
        raise ParseError("Expected '{', got {!r}".format(opening_brace))

    variable_name = ''

    for char in tokens:
        if char == '}':
            return Substitution(variable_name)
        else:
            variable_name += char

    if variable_name:
        raise ParseError("Expected '}', got to end of input")


def perform_substitutions(nodes, variables):
    for node in nodes:
        if isinstance(node, Literal):
            yield node.text
        elif isinstance(node, Substitution):
            yield variables[node.variable_name]
        else:
            raise ValueError("Unrecognised node type: {!r}".format(node))


class ParseError(Exception):
    pass
