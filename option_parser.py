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

class Option():
    """
    Collect together the list of options so that the the programme can select
    and validate any options
    """
    def __init__(self, items_involved):
        self.items_involved = items_involved
        self.no_required = 1
        self.selected = None
        self.all_models = True

    def __getitem__(self, i):
        return self.items_involved[i]

    def __repr__(self):
        return str(self.items_involved)

    def select(self, index):
        self.selected = self.items_involved[index]
        return

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

class OptionParser():
    def __init__(self, current_wargear=None):
        self.current_wargear = current_wargear #for checking if an exchange or option for '\' symbol
        self.run_count = -1                    #helps to add sub_index to parsing list

        #create lexer
        self.lexer = OptionLexer()
        self.lexer.build()
        self.options_list = [] #stores all available wargear in an options list
        return

    def parse2(self, parse_string, **kwargs):
        """Wrapper for parser function to check the items being parsed"""
        self.swap_wargear = [] #saves all items being parsed
        self.lexer.lexer.input(parse_string)

        if len(self.swap_wargear) == 1:     #if single item, unpack to help with error detection
            self.options_list.append(self.swap_wargear[0])
        else:
            self.options_list.append(Option(self.swap_wargear))

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
        self.parser = yacc.yacc(module=self, **kwargs)
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
                   | expression MINUS empty
                   | expression SLASH expression
        '''
        p[0] = (p[2],p[1],p[3])
        return

    def p_expression_name(self, p):
        '''
        expression : ITEM
                   | option
        '''
        #save all items in the string to be accessed outside
        self.swap_wargear.append(p[1])
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

    def check_already_used(self):
        """Helper function for run() to check if a wargear option is in use"""
        #check if any wargear items are already in use in the unit
        self.already_used = [False]
        if self.current_wargear != None:
            for i in self.swap_wargear:
                if i in self.current_wargear:
                    self.already_used[0] = True
                    self.already_used.append(i)
                    break #may cause errors but don't
        return

    def run(self, p, top_level=True):

        index = string.ascii_lowercase #for sub lists
        if top_level:
            self.run_count = -1
            self.already_used = [False]

        if type(p) == tuple:
            if p[0] == '/':
                ret = ''
                if top_level: #add header to listing
                    self.check_already_used()

                    if self.already_used[0]: #select header based on search above
                        ret+="The whole unit may exchange {} with one of the following:\n".format(self.already_used[1].item)
                    else:
                        ret += "The whole unit may take one of the following:\n"

                if type(p[1]) == tuple: #stops double sub-indexing if there is more than 2 options
                    ret += self.run(p[1], False)
                else:
                    self.run_count += 1
                    ret += '\t' + index[self.run_count] + ') ' + self.run(p[1], False)

                #testing for tuple as above does not have the same problems if ommitted
                self.run_count += 1
                ret += '\t' + index[self.run_count] + ') ' + self.run(p[2], False)

            elif p[0] == '-':
                if p[2] == None: #if just a tag to check its the whole unit
                    ret = "Any model"
                    ret += self.run(p[1], True)
                    ret = ret.replace("The whole unit", '')
                else: #requires per X models to be taken
                    ret = "For every {} models, you may ".format(p[2])
                    self.options_list[-1].no_required = p[2] #save the min amount requirement for access in main
                    self.check_already_used()
                    if self.already_used[0]:
                        ret += "exchange {} for:\n".format(self.already_used[1].item) + self.run(p[1], False)
                    else:
                        ret += "take one of:\n" + self.run(p[1], False)

        else:
            if top_level: #just a single item that needs listing
                ret = "The whole unit may take " + str(p)
            else: #sub level that needs to be appended to a listing
                if self.already_used[0]:
                    ret = p.__repr__(self.already_used[1])
                else:
                    ret = str(p)
            ret += '\n'

        if top_level: #if top level save the output to be manipulated
            self.ret = ret
        return ret

parser = OptionParser()
parser.build()
parser.parse2("Gauss blaster/Tesla carbine")
print(parser.ret)