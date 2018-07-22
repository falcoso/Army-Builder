# -*- coding: utf-8 -*-
"""
Created on Sat Jul 21 22:13:21 2018

@author: jones
"""

import ply.lex as lex
import ply.yacc as yacc
import string
import init
import enum

init.init("Necron")

def wargear_search(item):
        """
        Searches for a given wargear item in the armoury dictionary
        """
        if item in init.armoury_dict["Range"]:
            return init.armoury_dict["Range"][item]
        elif item in init.armoury_dict["Melee"]:
            return init.armoury_dict["Melee"][item]
        elif item in init.armoury_dict["Other Wargear"]:
            return init.armoury_dict["Other Wargear"][item]
        else:
            raise KeyError("{} not found in _armoury.xlsx file".format(item))
        return

tokens = ['ITEM', 'NUM', 'PLUS', 'MINUS', 'STAR', 'SLASH', 'COMMA']


# these are the regexes that the lexer uses to recognise the tokens
t_ITEM  = r'[a-zA-Z_][\w ]*[\w]'
t_NUM   = '0|[1-9][0-9]*'
t_PLUS  = r'\+'
t_MINUS = '-'
t_STAR  = r'\*'
t_SLASH = '/'
t_COMMA = ','
t_ignore = ' '
def t_error(t):
    print("Illegal characters!")
    t.lexer.skip(1)

lexer = lex.lex()

class CollectedItem():
    def __init__(self, item):
        self.item = item
        self.points = wargear_search(item)
        return

    def __repr__(self):
        ret = self.item + " ({}pts per model)".format(self.points)

class MultipleItem(CollectedItem):
    def __init__(self, *args):
        self.item = args
        self.points = 0
        for i in self.item:
            self.points += wargear_search(i)
        return

    def __repr__(self):
        ret = ''
        for i in range(len(self.item)):
            ret += self.item[i]
            if i == len(self.item) - 1:
                pass
            elif i == len(self.item) - 2:
                ret += ' and '
            else:
                ret += ', '

        ret += " ({}pts per model)".format(self.points)
        return ret

class RepeatedItem(CollectedItem):
    def __init__(self, *args):
        self.no_of = int(args[0])
        self.item = args[1]
        self.points = self.no_of*wargear_search(self.item)
        return

    def __repr__(self):
        return str(self.no_of) + ' of {} ({}pts per model)'.format(self.item, self.points)

#operator precedence
precedence = (
    ('left', 'COMMA'),
    ('left', 'MINUS'),
    ('left', 'SLASH'),
    ('left', 'PLUS'),
    ('left', 'STAR')
)

#define grammar tree
def p_calc(p):
    '''
    calc : expression
         | empty
    '''

    print(run(p[1]))

def p_error(p):
    print("Syntax error")

def p_expression(p):
    '''
    expression : expression COMMA expression
               | expression MINUS expression
               | expression SLASH expression
    '''

    p[0] = (p[2],p[1],p[3])

def p_expression_name(p):
    '''
    expression : ITEM
               | NUM
               | option
    '''
    p[0] = p[1]
    return

def p_mod_item(p):
    '''
    option : NUM STAR ITEM
           | ITEM PLUS ITEM
           | option PLUS option
    '''
    if p[2] == '*':
        p[0] = RepeatedItem(p[1],p[3])
    elif p[2] == '+':
        p[0] = MultipleItem(p[1],p[3])
    return

def p_empty(p):
    '''
    empty :
    '''
    p[0] = None

parse = yacc.yacc()
def run(p, top_level=True):
    index = string.ascii_lowercase
    if top_level:
        run.count = -1
    if type(p) == tuple:
        if p[0] == '/':
            ret = ''
            if top_level:
                ret += "You may take one of the following:\n"
            if type(p[1]) == tuple:
                ret += run(p[1], False)
            else:
                run.count += 1
                ret += '\t' + index[run.count] + '. ' + run(p[1], False) + '\n'
            if type(p[2]) == tuple:
                ret += run(p[2], False)
            else:
                run.count += 1
                ret += '\t' + index[run.count] + '. ' + run(p[2], False) + '\n'
            return ret
        else:
            if p[0] == '-':
                return 'For every {} models, you may exchange {} for:\n'.format(p[2], p[1][1]) + run(p[1], False)

    else:
        try:
            if top_level:
                return "You may take " + str(p)
            else:
                return str(p)
        except:
            print(p)
            return 'VOID ITEM'

s = 'Gauss flayer, Gauss cannon/Heavy gauss cannon-3, 2* Heat ray, Tesla carbine/Synaptic disintergrator/Gauss blaster, Warscythe/Dispersion shield + Hyperphase sword'
run.count = -1
for j, i in enumerate(s.split(',')):
    print('{}. '.format(j+1), end='')
    parse.parse(i)
