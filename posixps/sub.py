from __future__ import unicode_literals

from .parser import (
    lex, parse,
    Literal, Substitution,
    InternalParseError,
)


def sub(text, **variables):
    try:
        tokens = lex(text)
        nodes = parse(tokens)
        chunks = perform_substitutions(nodes, variables)
        return ''.join(chunks)
    except InternalParseError as e:
        raise ParseError(e, text)


def perform_substitutions(nodes, variables):
    for node in nodes:
        if isinstance(node, Literal):
            yield node.text
        elif isinstance(node, Substitution):
            yield variables[node.variable_name]
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
    position = 0

    for arrow_position in points:
        for _ in range(position, arrow_position):
            diagram += "-"
        diagram += "^"
        position = arrow_position + 1

    return diagram
