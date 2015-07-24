from __future__ import unicode_literals

import six

from .parser import (
    lex, parse,
    Literal, Substitution,
    InternalParseError,
)


def sub(text, variables):
    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    try:
        tokens = lex(text)
        nodes = parse(tokens)
        chunks = perform_substitutions(nodes, variables)
        return six.text_type().join(chunks)
    except InternalParseError as e:
        raise ParseError(e, text)


def perform_substitutions(nodes, variables):
    for node in nodes:
        if isinstance(node, Literal):
            yield node.text
        elif isinstance(node, Substitution):
            value = variables.get(node.variable_name, six.text_type())
            if isinstance(value, six.text_type):
                yield value
            elif isinstance(value, six.binary_type):
                yield value.decode('utf-8')
            else:
                raise ValueError(
                    "Unsupported value type ({}): {!r}"
                    .format(type(value), value)
                )
        else:
            raise ValueError("Unrecognised node type: {!r}".format(node))


class ParseError(Exception):
    def __init__(self, internal_parse_error, text):
        self.reason = internal_parse_error.reason
        self.diagram = build_diagram(text, internal_parse_error.points)

    def __unicode__(self):
        return "ParseError: {}\n\n{}".format(self.reason, self.diagram)

    def __str__(self):
        return unicode(self).encode('utf-8')


def build_diagram(text, points):
    diagram = text + "\n"
    current_position = 0
    fill_char = " "

    for point in points:
        if point >= current_position:
            for _ in range(current_position, point):
                diagram += fill_char
            diagram += "^"
            current_position = point + 1
        fill_char = "-"

    return diagram
