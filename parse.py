# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 21:23:04 2018

@author: jones
"""

import lex

class Parser:

    def __init__(self, lexer):
        self.string, self.tokens = None, None
        self.lexer = lexer
        self.t = self.lexer.token_types

        self.__lookahead = None

    @property
    def lookahead(self):
        if not self.__lookahead:
            try:
                self.__lookahead = next(self.tokens)
            except StopIteration:
                self.__lookahead = lex.Token(self.t.EOF, '', 0, -1)

        return self.__lookahead

    def next(self):
        if self.__lookahead and self.__lookahead.type == self.t.EOF:
            return self.__lookahead

        self.__lookahead = None
        return self.lookahead

    def match(self, token_type):
        if self.lookahead.type == token_type:
            return self.next()

        raise SyntaxError(f'Expected {token_type}, got {self.lookahead.type}', ('<string>', self.lookahead.lineno, self.lookahead.pos, self.string))

    # THE PARSING STARTS HERE
    def parse(self, string):
        # setup
        self.string = string
        self.tokens = self.lexer.tokenize(string)
        self.__lookahead = None
        self.next()

        # do parsing
        ret = [''] + self.parse_opt_list()

        return ' '.join(ret)

    def parse_opt_list(self) -> list:
        ret = self.parse_option(1)
        ret.extend(self.parse_opt_list_(1))

        return ret

    def parse_opt_list_(self, curr_opt_number) -> list:
        if self.lookahead.type in {self.t.EOF}:
            return []

        self.match(self.t.comma)

        ret = self.parse_option(curr_opt_number + 1)
        ret.extend(self.parse_opt_list_(curr_opt_number + 1))

        return ret

    def parse_option(self, opt_number) -> list:
        ret = [f'{opt_number}.']

        if self.lookahead.type == self.t.item:
            ret.extend(self.parse_choice())
        elif self.lookahead.type == self.t.num:
            ret.extend(self.parse_mult())
        else:
            raise SyntaxError(f'Expected {token_type}, got {self.lookahead.type}', ('<string>', self.lookahead.lineno, self.lookahead.pos, self.string))

        ret[-1] += '\n'

        return ret

    def parse_choice(self) -> list:
        c = self.parse_compound()
        m = self.parse_more_choices()
        e = self.parse_exchange()

        if not m:
            if not e:
                ret = f'You may take {" ".join(c)}'
            else:
                ret = f'for every {e} models you may take item {" ".join(c)}'
        elif m:
            c.extend(m)

            if not e:
                ret = f'each model may take one of: {", ".join(c)}'
            else:
                ret = f'for every {e} models you may exchange the following items with each other: {", ".join(c)}'
        else:
            ret = 'Semantic error!'

        return [ret]


    def parse_compound(self) -> list:
        ret = [self.lookahead.value]

        self.match(self.t.item)
        _ret = self.parse_add_item()

        return [' '.join(ret + _ret)]

    def parse_add_item(self) -> list:
        if self.lookahead.type in {self.t.comma, self.t.minus, self.t.slash, self.t.EOF}:
            return []

        ret = ['with']
        self.match(self.t.plus)

        ret.append(self.lookahead.value)
        self.match(self.t.item)

        return ret + self.parse_add_item()


    def parse_more_choices(self) -> list:
        if self.lookahead.type in {self.t.comma, self.t.minus, self.t.EOF}:
            return []

        self.match(self.t.slash)
        ret = self.parse_compound()

        return ret + self.parse_more_choices()


    def parse_exchange(self) -> str:
        if self.lookahead.type in {self.t.comma, self.t.EOF}:
            return ''

        self.match(self.t.minus)

        ret = self.lookahead.value
        self.match(self.t.num)

        return ret

    def parse_mult(self) -> list:
        ret = [f'each model may take {self.lookahead.value} of:']

        self.match(self.t.num)
        self.match(self.t.star)

        return ret + self.parse_compound()