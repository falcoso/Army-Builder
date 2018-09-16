# -*- coding: utf-8 -*-
"""
Created on Sat Jul 14 17:55:37 2018

@author: jones
"""

import init
import pandas as pd
import pytest
import main
import unit_class

def test_units_dict():
    """Checks the points calculations for the units dict"""
    detachments_dict, armoury_dict, units_dict = init.init("Necron", True)
    units = pd.read_csv("Necron/Units/Elites.csv", index_col=0, header=0)

    #check that points for wargear are being added
    assert units.loc["Lychguard"]["Points per Model"] != units_dict["Elites"]["Lychguard"].pts
    return

def test_units_dict_wargear():
    """
    Checks spelling of the options in the units_dict by creating a unit for
    each one.
    """
    for faction in ["Tau", "Necron"]:
        detachments_dict, armoury_dict, units_dict = init.init(faction, True)
        for foc, units in units_dict.items():
            for title, i in units.items():
                squad = unit_class.Unit(title, foc)
                squad.change_wargear(split_only=True)
    return

def test_detachments_dict_selection():
    """Makes sure all detachments in detachments_dict can be made"""
    for key in init.detachments_dict:
        main.input = lambda s: (['a1','a1','1','1']*20).pop(0)
        detach = main.Detachment(key)
    return

def test_WargearItem():
    """Checks that items can be created properly"""
    for cat, wargear_list in init.armoury_dict.items():
        for i in wargear_list:
            item = init.WargearItem(i)