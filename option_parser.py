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

class OptionLexer():
    tokens = ['ITEM', 'NUM', 'PLUS', 'MINUS', 'STAR', 'SLASH', 'COMMA']

    # these are the regexes that the lexer uses to recognise the tokens
    t_PLUS  = r'\+'
    t_MINUS = '-'
    t_STAR  = r'\*'
    t_SLASH = '/'
    t_COMMA = ','
    t_ignore = ' '

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def t_ITEM(self, t):
        r'[a-zA-Z_][\w ]*[\w]'
        t.value = WargearItem(t.value)
        return t

    def t_NUM(self,t):
        '0|[1-9][0-9]*'
        t.value = int(t.value)
        return t

    # Build the lexer
    def build(self,**kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    # Test it output
    def test(self,data):
        self.lexer.input(data)
        while True:
             tok = self.lexer.token()
             if not tok:
                 break
             print(tok)


lexer = OptionLexer()
lexer.build()

class WargearItem():
    def __init__(self, item):
        self.item = item
        self.points = self.wargear_search(item)
        self.no_of = 1
        return

    def wargear_search(self, item):
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

    def __repr__(self):
        if self.no_of == 1:
            ret = self.item
        else:
            ret = str(self.no_of) + ' ' + self.item + 's'
        ret += " ({}pts per model)".format(self.points)
        return ret

    def __mul__(self, integer):
        self.points = self.points*integer
        self.no_of  = self.no_of*integer
        return self

    def __add__(self, other_item):
        if type(other_item) == MultipleItem:
            other_item.item.append(self.item)
            other_item.points += self.points
            return other_item

        else:
            ret = MultipleItem(self, other_item)
            return ret

class MultipleItem(WargearItem):
    def __init__(self, *args):
        self.item = list(map(lambda s: s.item, args))
        self.points = 0
        for i in args:
            self.points += i.points
        return

    def __mul__(self, other):
        pass

    def __add__(self, other_item):
        if type(other_item) == MultipleItem:
            self.item += other_item.item
        else:
            self.item.append(other_item.item)
        self.points += other_item.points
        return self

    def __repr__(self):
        ret = ''
        for i in range(len(self.item)):
            ret += self.item[i]
            if i == len(self.item) - 1:
                pass
            elif i == len(self.item) - 2:
                ret += ' & '
            else:
                ret += ', '

        ret += " ({}pts per model)".format(self.points)
        return ret

tokens = ['ITEM', 'NUM', 'PLUS', 'MINUS', 'STAR', 'SLASH', 'COMMA']
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
    print("Syntax error {} is not valid".format(p))

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

def p_mult_item(p):
    '''
    option : NUM STAR ITEM
           | NUM STAR option
    '''
    p[0] = p[3] * p[1]
    return

def p_add_item(p):
    '''
    option : option PLUS option
           | ITEM PLUS option
           | ITEM PLUS ITEM
    '''
    p[0] = p[1] + p[3]

def p_empty(p):
    '''
    empty :
    '''
    p[0] = None

# Build the lexer
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
                ret += '\t' + index[run.count] + ') ' + run(p[1], False) + '\n'
            if type(p[2]) == tuple:
                ret += run(p[2], False)
            else:
                run.count += 1
                ret += '\t' + index[run.count] + ') ' + run(p[2], False) + '\n'
            return ret
        else:
            if p[0] == '-':
                return 'For every {} models, you may exchange {} for:\n'.format(p[2], p[1][1].item) + run(p[1], False)

    else:
        try:
            if top_level:
                return "You may take " + str(p)
            else:
                return str(p)
        except:
            return 'VOID ITEM'

s = 'Gauss flayer,Gauss cannon/Heavy gauss cannon-3,2*Heat ray,Tesla carbine/Synaptic disintegrator/Gauss blaster,Warscythe/Voidblade+Dispersion shield+Hyperphase sword'
run.count = -1
for j, i in enumerate(s.split(',')):
    print('{}. '.format(j+1), end='')
    parse.parse(i)
