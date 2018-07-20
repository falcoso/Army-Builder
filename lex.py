# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 21:12:00 2018

@author: jones
"""

import re
import enum

class Token:
    def __init__(self, type, value: str, lineno: int, pos: int):
        self.type, self.value, self.lineno, self.pos = type, value, lineno, pos

    def __str__(self):
        v = f'({self.value!r})' if self.value else ''

        return f'{self.type.name}{v} at {self.lineno}:{self.pos}'

    __repr__ = __str__


class Lexer:
    def __init__(self, token_types: enum.Enum, tokens_regexes: dict):
        self.token_types = token_types

        regex = '|'.join(map('(?P<{}>{})'.format, *zip(*((tok.name, regex) for tok, regex in tokens_regexes.items()))))
        self.regex = re.compile(regex)

    def tokenize(self, string, skip=['space']):
        # TODO: detect invalid input

        lineno, pos = 0, 0
        skip = set(map(self.token_types.__getitem__, skip))

        for matchobj in self.regex.finditer(string):
            type_name = matchobj.lastgroup
            value = matchobj.groupdict()[type_name]

            Type = self.token_types[type_name]

            if Type == self.token_types.newline: # possibly buggy, but not catastrophic
                self.lineno += 1
                self.pos = 0
                continue

            pos = matchobj.end()

            if Type not in skip:
                yield Token(Type, value, lineno, pos)

        yield Token(self.token_types.EOF, '', lineno, pos)