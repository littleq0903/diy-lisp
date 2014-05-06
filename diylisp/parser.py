# -*- coding: utf-8 -*-

import re
from ast import is_boolean, is_list
from types import LispError

"""
This it the parser module, with the `parse` function which you'll implement as part 1 of
the workshop. It's job is to convert strings into data structures that the evaluator can 
understand. 
"""


def clean_boundary_paren(source):
    new_source = re.sub(r"^\((.*)\)$", r'\1', source.strip())
    return new_source, source == new_source


def clean_newline_spaces(source):
    return re.sub(r'[ \n]+', ' ', source)


def expression(exp):
    # TODO: to real expression in Python
    # like #f to False, #t to True
    # '1' to 1
    # '"1"' to "1"
    directMapping = {
        "#f": False,
        "#t": True,
    }

    if exp in directMapping:
        return directMapping[exp]
    elif re.match(r'^\d+$', exp):
        return int(exp)
    elif re.match(r'^\d+\.\d+$', exp):
        return float(exp)
    else:
        return exp


def parse(source):
    """Parse string representation of one *single* expression
    into the corresponding Abstract Syntax Tree."""

    source = remove_comments(source)
    source = clean_newline_spaces(source).strip()

    return recursive_parse(source)


def recursive_parse(source):
    if source[0] == "'":
        return ["quote", recursive_parse(source[1:])]
    elif source[0] == "(":
        end = find_matching_paren(source)

        if end + 1 < len(source):
            raise LispError("Expected EOF: %s" % source)
        if end + 1 > len(source):
            raise LispError("Incomplete expression: %s" % source)

    source, isterminal = clean_boundary_paren(source.strip())

    if isterminal:
        return expression(source)

    exps = split_exps(source)

    return map(recursive_parse, exps)


##
## Below are a few useful utility functions. These should come in handy when 
## implementing `parse`. We don't want to spend the day implementing parenthesis 
## counting, after all.
## 

def remove_comments(source):
    """Remove from a string anything in between a ; and a linebreak"""
    return re.sub(r";.*\n", "\n", source)

def find_matching_paren(source, start=0):
    """Given a string and the index of an opening parenthesis, determines 
    the index of the matching closing paren."""

    assert source[start] == '('
    pos = start
    open_brackets = 1
    while open_brackets > 0:
        pos += 1
        if len(source) == pos:
            raise LispError("Incomplete expression: %s" % source[start:])
        if source[pos] == '(':
            open_brackets += 1
        if source[pos] == ')':
            open_brackets -= 1
    return pos

def split_exps(source):
    """Splits a source string into subexpressions 
    that can be parsed individually.

    Example: 

        > split_exps("foo bar (baz 123)")
        ["foo", "bar", "(baz 123)"]
    """

    rest = source.strip()
    exps = []
    while rest:
        exp, rest = first_expression(rest)
        exps.append(exp)
    return exps

def first_expression(source):
    """Split string into (exp, rest) where exp is the 
    first expression in the string and rest is the 
    rest of the string after this expression."""
    
    source = source.strip()
    if source[0] == "'":
        exp, rest = first_expression(source[1:])
        return source[0] + exp, rest
    elif source[0] == "(":
        last = find_matching_paren(source)
        return source[:last + 1], source[last + 1:]
    else:
        match = re.match(r"^[^\s)']+", source)
        end = match.end()
        atom = source[:end]
        return atom, source[end:]

##
## The functions below, `parse_multiple` and `unparse` are implemented in order for
## the REPL to work. Don't worry about them when implementing the language.
##

def parse_multiple(source):
    """Creates a list of ASTs from program source constituting multiple expressions.

    Example:

        >>> parse_multiple("(foo bar) (baz 1 2 3)")
        [['foo', 'bar'], ['baz', 1, 2, 3]]

    """

    source = remove_comments(source)
    return [parse(exp) for exp in split_exps(source)]

def unparse(ast):
    """Turns an AST back into lisp program source"""

    if is_boolean(ast):
        return "#t" if ast else "#f"
    elif is_list(ast):
        if len(ast) > 0 and ast[0] == "quote":
            return "'%s" % unparse(ast[1])
        else:
            return "(%s)" % " ".join([unparse(x) for x in ast])
    else:
        # integers or symbols (or lambdas)
        return str(ast)
