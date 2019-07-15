"""
Parsing classes to process the options strings for each unit.

Classes:
--------
Option:
    Collects together the list of wargear so that the the programme can select
    and validate any options.

OptionLexer: Container class for yacc Lexer.

OptionParser:
    Container class to parse option strings and contextually create options
    based on the current set of wargear in use on the unit/model.
"""
import ply.lex as lex
import ply.yacc as yacc
import numpy as np
import string

import init


class Option:
    """
    Collects together the list of wargear so that the the programme can select
    and validate any options.

    Parameters
    ----------
    items_involved : list (init.WargearItem)
        List of all the Wargear that could be selected within the option.

    Public Attributes
    ----------
    items_involved : list (init.WargearItem)
        List of all the Wargear that could be selected within the option.
    selected : list (init.WargearItem)
        List of any Wargear that has been chosen to be added.
    no_required : int
        Number of models required in a unit before this option can be taken.
    no_picks : int
        Number of Wargear that can be chosen in the option.
    header : str
        Heading given when displaying the options.

    Public Methods
    --------------
    select(self, index):
        Chooses the index option in items_involved to be added to selected.
    select_list(self, index):
        Resets self.selected and replaces it with the supplied list.
    """

    def __init__(self, items_involved):
        self.items_involved = items_involved
        self.no_required = 1
        self.selected = []
        self.no_picks = 1
        self.header = ''

    def __getitem__(self, i):
        return self.items_involved[i]

    def __hash__(self):
        return hash(self.items_involved) + hash(self.no_required) + hash(self.no_picks) + hash(self.header)

    def __repr__(self, comparison=None):
        ret = self.header
        if len(self.items_involved) == 1:
            return ret
        for i, j in enumerate(self.items_involved):
            ret += '\n\t' + string.ascii_lowercase[i] + ') ' + j.__repr__(tidy=True,
                                                                          comparison=comparison)
        return ret

    def select(self, index):
        """
        Chooses the index option in items_involved to be added to selected.
        """
        if isinstance(index, int) or isinstance(index, np.uint8):
            index = self.items_involved[index]

        if self.selected == []:
            self.selected = [index]

        # if choice is chosen again have more than one
        elif index in self.selected:
            for i in self.selected:
                if i == index:
                    i.set_no_of(i.no_of + 1)
        # append to selected items
        else:
            self.selected.append(index)

        if len(self.selected) > self.no_picks:
            raise RuntimeError("Unable to select item as only {} picks are allowed for this option. Current selected:{}".format(
                self.no_picks, self.selected))
        return

    def select_list(self, index):
        """Resets self.selected and replaces it with the supplied list."""
        self.selected = [self.items_involved[i] for i in index]
        return


class OptionLexer:
    """Container class for yacc Lexer."""
    tokens = ['ITEM', 'NUM', 'PLUS', 'MINUS', 'STAR', 'SLASH', 'HASH', 'CARET']

    # these are the regexes that the lexer uses to recognise the tokens
    t_PLUS = r'\+'
    t_MINUS = '-'
    t_STAR = r'\*'
    t_SLASH = '/'
    t_HASH = r'\#'
    t_CARET = r'\^'
    t_ignore = ' '

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def t_ITEM(self, t):
        r'[a-zA-Z_][\w -]*[\w]+[\w]'
        t.value = init.WargearItem(t.value)
        return t

    def t_NUM(self, t):
        '0|[1-9][0-9]*'
        t.value = int(t.value)
        return t

    # Build the lexer
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    # Test it output
    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)


class OptionParser:
    """
    Container class to parse option strings and contextually create options
    based on the current set of wargear in use on the unit/model.

    <NUM>#<List of wargear> : May take <NUM> choices from the list
    <List of wargear>-: Option applies on model by model basis rather than whole
                        unit
    <List of wargear>-<NUM> : Option can be take once per <NUM> models
    <wargear1>/<wargear2>... : List of wargear containing <wargear1>, <wargear2>

    Parameters
    ----------
    current_wargear : list (init.WargearItem)
        List of wargear currently in the unit to add context to any Options that
        are generated.
    unit : bool
        True if the parser is attached to a unit, False if attached to a model.

    Public Attributes
    ----------
    current_wargear : list (init.WargearItem)
        List of wargear currently in the unit to add context to any Options that
        are generated.
    unit : bool
        True if the parser is attached to a unit, False if attached to a model.
    lexer : OptionLexer
        Lexer to generate tokens for the scanner
    options_list : list (Option)
        List of fully parsed options.

    Public Methods
    --------------
    parse2(self, parse_string, **kwargs):
        Wrapper for parser function to check the items being parsed
    """

    def __init__(self, current_wargear=None, unit=True):
        self.current_wargear = current_wargear  # for checking if an exchange or addition option for '/' symbol
        self.unit = unit

        # create lexer
        self.lexer = OptionLexer()
        self.lexer.build()
        self.options_list = []  # stores all available wargear in an options list
        return

    def __repr__(self):
        ret = ''
        for index, i in enumerate(self.options_list):
            ret += str(index + 1) + ". "
            pr = False
            if i.no_picks == 1:
                for j in i.items_involved:
                    if j in self.current_wargear:
                        ret += i.__repr__(comparison=j) + "\n"
                        pr = True
                        break
                if pr:
                    continue

            ret += i.__repr__() + "\n\n"
        return ret

    def parse2(self, parse_string, **kwargs):
        """Wrapper for parser function to check the items being parsed"""
        self.options_list = []
        for item in parse_string:
            self.swap_wargear = []  # saves all items being parsed
            self.options_list.append(Option(self.swap_wargear))
            self.parser.parse(item, **kwargs)
        return self.options_list

    tokens = OptionLexer.tokens

    # operator precedence
    precedence = (('left', 'HASH'),
                  ('left', 'MINUS'),
                  ('left', 'SLASH'),
                  ('left', 'PLUS'),
                  ('left', 'STAR'))

    def build(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)
        return

    # define grammar tree
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
        expression : expression MINUS NUM
                   | expression MINUS empty
                   | expression CARET NUM
                   | expression CARET empty
                   | NUM HASH expression
                   | expression SLASH expression
        '''
        p[0] = (p[2], p[1], p[3])
        return

    def p_expression_name(self, p):
        '''
        expression : ITEM
                   | option
        '''
        # save all items in the string to be accessed outside
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

    def __check_already_used(self):
        """Helper function for run() to check if a wargear option is in use"""
        # check if any wargear items are already in use in the unit
        self.already_used = [False]
        if self.current_wargear is not None:
            for i in self.swap_wargear:
                if i in self.current_wargear:
                    self.already_used[0] = True
                    self.already_used.append(i)
                    break  # may cause errors but don't
        return

    def run(self, p, top_level=True):

        if top_level:
            self.already_used = [False]

        if type(p) == tuple:
            if p[0] == '/':
                ret = ''
                if top_level:  # add header to listing
                    self.__check_already_used()
                    if self.unit:
                        ret += "The whole unit may"
                    else:
                        ret += "You may"

                    if self.already_used[0]:  # select header based on search above
                        ret += " exchange {} with one of the following:".format(
                            self.already_used[1].item)
                    else:
                        ret += " take one of the following:"

            elif p[0] == '-':
                if p[2] is None:  # if just a tag to check its the whole unit
                    ret = "Any model"
                    ret += self.run(p[1], True)
                    ret = ret.replace("The whole unit", '')

                else:  # requires per X models to be taken
                    ret = "For every {} models, you may ".format(p[2])
                    # save the min amount requirement for access in main
                    self.options_list[-1].no_required = p[2]
                    self.__check_already_used()
                    if self.already_used[0]:
                        ret += "exchange {} for:".format(
                            self.already_used[1].item) + self.run(p[1], False)
                    else:
                        ret += "take one of:" + self.run(p[1], False)
                self.options_list[-1].all_models = False

            elif p[0] == '^':
                if p[2] == 1:
                    ret = '{} model may take one of:'.format(p[2])
                else:
                    ret = '{} models may take one of:'.format(p[2])
                self.run(p[1], False)

            elif p[0] == '#':
                self.options_list[-1].no_picks = p[1]
                ret = self.run(p[2], True)
                ret = ret.replace("take one", "take {}".format(p[1]))

        else:
            if top_level:  # just a single item that needs listing
                ret = "The whole unit may take " + str(p)
            else:  # sub level that needs to be appended to a listing
                if self.already_used[0]:
                    ret = p.__repr__(self.already_used[1])
                else:
                    ret = str(p)
            ret += '\n'

        if top_level:  # if top level save the output to be manipulated
            self.options_list[-1].header = ret
        return ret


global main_parser
main_parser = OptionParser()
main_parser.build()
