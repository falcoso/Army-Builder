# -*- coding: utf-8 -*-
"""
Created on Sat Jul 21 22:13:21 2018

@author: jones
"""

import ply.lex as lex
import ply.yacc as yacc
import init
import string

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
        t.value = init.WargearItem(t.value)
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
                ret += '\t' + index[run.count] + ') ' + run(p[1], False)
            if type(p[2]) == tuple:
                ret += run(p[2], False)
            else:
                run.count += 1
                ret += '\t' + index[run.count] + ') ' + run(p[2], False)
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
