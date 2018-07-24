# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 14:48:16 2018

@author: jones
"""

import pytest
import init
import option_parser

def test_units_dict_options():
    """
    Parses all the options in the units pict to check that they run without
    error. Similar to the test_units_dict() in test_init but parses the option strings
    directly rather than through the main module.
    """
    #create parser
    parser = option_parser.OptionParser()
    parser.build()



    detachments_dict, armoury_dict, units_dict = init.init("Necron", True)
    for foc, units in units_dict.items():
        for title, i in units.items():
            if i.options == None:
                continue

            for option in i.options:
                parser.parse2(option)
    return

def test_direct_string():
    """Parses the a direct string through the parser and confirms its output"""
     #create parser
    parser = option_parser.OptionParser([init.WargearItem("Tesla carbine")])
    parser.build()

    #create test string
    comp_string = ['You may take Gauss flayer (0pts per model)\n',
                   'For every 3 models, you may take one of:\n\ta) Gauss cannon (20pts per model)\n\tb) Heavy gauss cannon (27pts per model)\n',
                   'You may take 2 Heat rays (108pts per model)\n',
                   'You may exchange Tesla carbine with one of the following:\n\ta) Tesla carbine (net 0pts per model)\n\tb) Synaptic disintegrator (net -9pts per model)\n\tc) Gauss blaster (net 0pts per model)\n',
                   'You may take one of the following:\n\ta) Warscythe (11pts per model)\n\tb) Dispersion shield, Hyperphase sword & Voidblade (21pts per model)\n']

    s = 'Gauss flayer,Gauss cannon/Heavy gauss cannon-3,2*Heat ray,Tesla carbine/Synaptic disintegrator/Gauss blaster, Warscythe/Voidblade+Dispersion shield+Hyperphase sword'

    for i,j in zip(s.split(','), comp_string):
        parser.parse2(i)
        assert parser.ret == j
