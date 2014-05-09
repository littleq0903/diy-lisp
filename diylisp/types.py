# -*- coding: utf-8 -*-

"""
This module holds some types we'll have use for along the way.

It's your job to implement the Closure and Environment types.
The LispError class you can have for free :)
"""

class LispError(Exception): 
    """General lisp error class."""
    pass

class Closure:
    
    def __init__(self, env, params, body):
        from ast import is_list

        if not is_list(params):
            raise LispError("param %s is not a list")

        self.env = env
        self.params = params
        self.body = body

    def __str__(self):
        return "<closure/%d>" % len(self.params)

class Environment:

    def __init__(self, variables=None):
        self.variables = variables if variables else {}

    def lookup(self, symbol):
        try:
            return self.variables[symbol]
        except KeyError:
            raise LispError("undefined: %s" % symbol)

    def extend(self, variables):
        old_variables = self.variables.copy()
        old_variables.update(variables)
        old_env = Environment(old_variables)

        return old_env

    def set(self, symbol, value):
        if symbol in self.variables:
            raise LispError("symbol already defined: %s" % symbol)
        else:
            self.variables[symbol] = value
            return self.variables[symbol]
