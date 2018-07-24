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

class OptionParser():
    def __init__(self, current_wargear=None):
        self.current_wargear = current_wargear #for checking if an exchange or option for '\' symbol
        self.run_count = -1                    #helps to add sub_index to parsing list

        #create lexer
        self.lexer = OptionLexer()
        self.lexer.build()
        return

    def parse2(self, parse_string, **kwargs):
        '''Wrapper for parser function to check the items being parsed'''
        if '/' in parse_string:
            self.swap_wargear = []
            self.lexer.lexer.input(parse_string)
            while True:
                tok = self.lexer.lexer.token()
                if not tok:
                    break
                if tok.type == 'ITEM':
                    self.swap_wargear.append(tok.value)

        return self.parser.parse(parse_string, **kwargs)

    tokens = OptionLexer.tokens

    #operator precedence
    precedence = (
        ('left', 'COMMA'),
        ('left', 'MINUS'),
        ('left', 'SLASH'),
        ('left', 'PLUS'),
        ('left', 'STAR')
    )

    def build(self, **kwargs):
        self.parser = yacc.yacc(module=self)
        return

    #define grammar tree
    def p_calc(self, p):
        '''
        calc : expression
             | empty
        '''
        return self.run(p[1])

    def p_error(self, p):
        print("Syntax error {} is not valid".format(p))
        return

    def p_expression(self, p):
        '''
        expression : expression COMMA expression
                   | expression MINUS NUM
                   | expression SLASH expression
        '''
        p[0] = (p[2],p[1],p[3])
        return

    def p_expression_name(self, p):
        '''
        expression : ITEM
                   | option
        '''
        p[0] = p[1]
        return

    def p_mult_item(self, p):
        '''
        option : NUM STAR ITEM
               | NUM STAR option
        '''
        p[0] = p[3] * p[1]
        return

    def p_add_item(self, p):
        '''
        option : option PLUS option
               | ITEM PLUS option
               | ITEM PLUS ITEM
        '''
        p[0] = p[1] + p[3]
        return

    def p_empty(self, p):
        '''
        empty :
        '''
        p[0] = None
        return


    def run(self, p, top_level=True):
        index = string.ascii_lowercase #for sub lists
        if top_level:
            self.run_count = -1

        if type(p) == tuple:
            if p[0] == '/':
                ret = ''
                if top_level: #add header to listing
                    #check if any wargear items are already in use
                    already_used = [False]
                    if self.current_wargear != None:
                        for i in self.swap_wargear:
                            if i in self.current_wargear:
                                already_used[0] = True
                                already_used.append(i)
                                break #may cause errors but don't think there should be more than one swap out

                    if already_used[0]: #select header based on search above
                        ret+="You may exchange {} with one of the following:\n".format(already_used[1].item)
                    else:
                        ret += "You may take one of the following:\n"

                if type(p[1]) == tuple: #stops double sub-indexing if there is more than 2 options
                    ret += self.run(p[1], False)
                else:
                    self.run_count += 1
                    ret += '\t' + index[self.run_count] + ') ' + self.run(p[1], False)

                #testing for tuple as above does not have the same problems if ommitted
                self.run_count += 1
                ret += '\t' + index[self.run_count] + ') ' + self.run(p[2], False)

            elif p[0] == '-':
                ret = 'For every {} models, you may exchange {} for:\n'.format(p[2], p[1][1].item) + self.run(p[1], False)

        else:
            try:
                if top_level: #just a single item that needs listing
                    ret = "You may take " + str(p)
                else: #sub level that needs to be appended to a listing
                    ret = str(p)
            except:
                ret = 'VOID ITEM'

        if top_level: #if top level save the output to be manipulated
            self.ret = ret
        return ret

if __name__ == "__main__":
    parser = OptionParser([init.WargearItem("Tesla carbine")])
    parser.build()
    s = 'Gauss flayer,Gauss cannon/Heavy gauss cannon-3,2*Heat ray,Tesla carbine/Synaptic disintegrator/Gauss blaster,Warscythe/Voidblade+Dispersion shield+Hyperphase sword'
    for j, i in enumerate(s.split(',')):
        print('{}. '.format(j+1), end='')
        parser.parse2(i)
        print(parser.ret)
