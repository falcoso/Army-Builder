# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 21:31:25 2018

@author: jones
"""

import enum

from lex import Lexer
from parse import Parser


# these are all the types of tokens present in our grammar
token_types = enum.Enum('Types', 'item num plus minus star slash comma space newline empty EOF')

t = token_types

# these are the regexes that the lexer uses to recognise the tokens
terminals_regexes = {
    t.item: r'[a-zA-Z_][\w ]*',
    t.num: '0|[1-9][0-9]*',
    t.plus: r'\+',
    t.minus: '-',
    t.star: r'\*',
    t.slash: '/',
    t.comma: ',',
    t.space: r'[ \t]',
    t.newline: r'\n'
}

lexer = Lexer(token_types, terminals_regexes)
parser = Parser(lexer)

string = 'itemA, itemB/itemC-3, 2*itemD, itemE/itemF/itemG, itemH/itemI+itemJ'
print(f'STRING FROM THE QUESTION: {string!r}\nRESULT:')
print(parser.parse(string), '\n\n')


string = input('Enter a command: ')

while string and string.lower() not in {'q', 'quit', 'e', 'exit'}:
    try:
        print(parser.parse(string))
    except SyntaxError as e:
        print(f'    Syntax error: {e}\n    {e.text}\n' + ' ' * (4 + e.offset - 1) + '^\n')

    string = input('Enter a command: ')