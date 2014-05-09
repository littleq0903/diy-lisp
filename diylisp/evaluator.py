# -*- coding: utf-8 -*-

from types import Environment, LispError, Closure
from ast import is_boolean, is_atom, is_symbol, is_list, is_closure, is_integer
from asserts import assert_exp_length, assert_valid_definition, assert_boolean
from parser import unparse

import re
import operator

"""
This is the Evaluator module. The `evaluate` function below is the heart
of your language, and the focus for most of parts 2 through 6.

A score of useful functions is provided for you, as per the above imports, 
making your work a bit easier. (We're supposed to get through this thing 
in a day, after all.)
"""


def eval_arithmetic(op, arg1, arg2):
    op_table = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.div,
        'mod': operator.mod,
        '>': operator.gt
        }

    return op_table[op](arg1, arg2)


def evaluate(ast, env):
    """Evaluate an Abstract Syntax Tree in the specified environment."""
    print ast, env.variables


    # otherwise, it will be a function
    op = ast[0]
    args = ast[1:]

    # Simple Evaluation
    # quote evaluation
    if op == "quote":
        assert_exp_length(args, 1)
        return evaluate(args[0], env)

    # atom function
    if op == "atom":
        assert_exp_length(args, 1)
        return is_atom(evaluate(args[0], env))

    # arithematic evaluation
    if op in ['+', '-', '*', '/', 'mod', '>']:
        assert_exp_length(args, 2)
        
        arg1 = evaluate(args[0], env)
        arg2 = evaluate(args[1], env)

        if not (is_integer(arg1) and is_integer(arg2)):
            raise LispError("Arguments of arithmetic operator should be numbers")

        return eval_arithmetic(op, arg1, arg2)

    # define evaluation
    if op == "define":
        try:
            assert_exp_length(args, 2)
        except LispError:
            raise LispError("Wrong number of arguments")

        var_name = args[0]
        var_value = evaluate(args[1], env)

        if not is_symbol(var_name):
            raise LispError("non-symbol: %s" % var_name)

        env.set(var_name, var_value)
        return var_name
        
    # equal evaluation
    if op == "eq":
        eval_arg1 = evaluate(args[0], env)
        eval_arg2 = evaluate(args[1], env)

        return is_atom(eval_arg1) and is_atom(eval_arg2) and eval_arg1 == eval_arg2

    # Complex Evaluation
    # if evaluation
    if op == "if":
        assert_exp_length(args, 3)

        eval_predicate = evaluate(args[0], env)

        if eval_predicate:
            return evaluate(args[1], env)
        else:
            return evaluate(args[2], env)

    if op == 'lambda':
        try:
            assert_exp_length(args, 2)
        except LispError:
            raise LispError("number of arguments")
        print len(args)

        lambda_params = args[0]
        lambda_body = args[1]

        return Closure(env, lambda_params, lambda_body)

    if is_closure(op):
        closure = op

        assert_exp_length(args, len(closure.params))

        new_env = Environment(closure.env.variables.copy())

        for n, param in enumerate(closure.params):
            new_env.set(param, evaluate(args[n], new_env))

        return evaluate(closure.body, new_env)

    # fundamental
    if is_symbol(ast):
        print 'is_symbol'
        try:
            return evaluate(env.lookup(ast), env)
        except:
            if len(ast) == 1:
                raise LispError("undefined: %s" % ast[0])
            else:
                raise LispError("not a function: %s" % ast[0])

    if is_atom(ast):
        print 'is_atom'
        return ast

    if is_list(ast):
        print 'is_list'
        return evaluate(map(lambda inner_ast: evaluate(inner_ast, env), ast), env)

