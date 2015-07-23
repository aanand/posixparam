from __future__ import unicode_literals

from collections import namedtuple


Literal = namedtuple('Literal', 'text')
Substitution = namedtuple('Substitution', 'variable_name')


def sub(text, **variables):
    try:
        tokens = lex(text)
        nodes = parse(tokens)
        chunks = perform_substitutions(nodes, variables)
        return ''.join(chunks)
    except InternalParseError as e:
        raise ParseError(e, text)


def lex(text):
    return (c for c in text)


def parse(tokens):
    literal_text = ''
    position = 0

    for char in tokens:
        if char == '$':
            if literal_text:
                yield Literal(literal_text)
                literal_text = ''

            position += 1

            substitution, length = parse_substitution(tokens, position)
            yield substitution
            position += length
        else:
            literal_text += char
            position += 1

    if literal_text:
        yield Literal(literal_text)
        literal_text = ''


def parse_substitution(tokens, starting_position):
    position = starting_position

    opening_brace = next(tokens)
    if opening_brace != '{':
        raise MissingOpeningBrace(position)

    position += 1

    variable_name = ''

    for char in tokens:
        position += 1

        if char == '}':
            return Substitution(variable_name), position - starting_position
        else:
            variable_name += char

    if variable_name:
        raise MissingClosingBrace(starting_position, position)


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
        self.diagram = build_diagram(text, internal_parse_error.arrows)

    def __unicode__(self):
        return "ParseError: {}\n\n{}".format(self.reason, self.diagram)

    def __str__(self):
        return unicode(self).encode('utf-8')


def build_diagram(text, arrows):
    diagram = text + "\n"
    position = 0

    for arrow_position in arrows:
        for _ in range(position, arrow_position):
            diagram += "-"
        diagram += "^"
        position = arrow_position + 1

    return diagram


class InternalParseError(Exception):
    pass


class MissingOpeningBrace(InternalParseError):
    def __init__(self, position):
        self.position = position
        self.reason = "Missing opening brace"
        self.arrows = [position]


class MissingClosingBrace(InternalParseError):
    def __init__(self, opening_brace_position, error_position):
        self.opening_brace_position = opening_brace_position
        self.error_position = error_position

        self.reason = "Opening brace at char {} is " \
                      "missing a closing brace".format(opening_brace_position)

        self.arrows = [opening_brace_position, error_position]
