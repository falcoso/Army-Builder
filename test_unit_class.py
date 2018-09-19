# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 14:43:36 2018

@author: jones
"""

import unit_class
import init
import copy
import pytest

init.init('Necron')

def test_unit_class():
    """Checks the attributes of the units class"""
    warriors = unit_class.Unit("Necron Warriors", "Troops")
    assert warriors.pts == 120
    assert warriors.default_model.wargear == [init.WargearItem("Gauss flayer")]
    return

def test_re_size():
    """Checks the Unit.re_size() method"""
    warriors = unit_class.Unit("Necron Warriors", "Troops")
    mock_input = ["test", 2, 15]
    unit_class.input = lambda s: mock_input.pop(0)
    #first two should error but re-call to input
    warriors.re_size()
    assert warriors.pts == warriors.default_model.pts_per_model*15 #check valid input modifies the unit points

    #check programmer input raises the correct errors
    for i in ["test", 2]:
        try:
            warriors.re_size("test")
            raise AssertionError("Test should reach exception at this point. Current i={}".format(i))
        except (TypeError, ValueError):
            continue

    #check valid programmer input
    warriors.re_size(10)
    assert warriors.pts == 120
    return

def test_change_wargear():
    """Checks the Unit.change_wargear() method applies correct wargear"""
    unit = unit_class.Unit("Catacomb Command Barge", "HQ")
    mock_input = ["test", "1b, 2c,3, 4", "1b", "1b", "1b", "y"]
    unit_class.input = lambda s: mock_input.pop(0)
    unit.change_wargear()
    wargear_selected = [init.WargearItem("Tesla cannon"),
                        init.WargearItem("Hyperphase sword"),
                        init.WargearItem("Phylactery"),
                        init.WargearItem("Resurrection orb")]
    for i in wargear_selected:
        assert i in unit.default_model.wargear

    #check that changes no applied to the whole unit creates a new model
    unit = unit_class.Unit("Destroyers", "Fast Attack")
    unit.re_size(3)
    unit.change_wargear()
    assert unit.get_size() == 3
    assert unit.default_model.no_models == 2
    assert list(unit.ex_models)[0].wargear == [init.WargearItem("Heavy gauss cannon")]

    #check that when re-sizing and repeating the existing extra model is modified
    unit.re_size(6)
    unit.change_wargear()
    assert unit.get_size() == 6
    assert unit.default_model.no_models == 4
    assert list(unit.ex_models)[0].wargear == [init.WargearItem("Heavy gauss cannon")]

    unit.reset(False)
    unit.change_wargear()
    assert unit.get_size() == 3
    assert unit.default_model.no_models == 2
    assert list(unit.ex_models)[0].wargear == [init.WargearItem("Heavy gauss cannon")]
    return

def test_reset():
    """
    Checks the Unit.reset() method returns the Unit back to its initial state
    """
    mock_input = ["1b", 'no', 'y']
    unit_class.input = lambda s: mock_input.pop(0)
    unit = unit_class.Unit("Destroyers", "Fast Attack")
    unit_copy = copy.deepcopy(unit)
    unit.re_size(3)
    unit.change_wargear()   #input = '1b'

    #input = 'no'
    unit.reset()
    assert unit_copy.get_size() != unit.get_size()
    assert unit_copy.ex_models  != unit.ex_models
    assert unit_copy.default_model.no_models != unit.default_model.no_models

    #input = 'y'
    unit.reset()
    assert unit_copy.get_size() == unit.get_size()
    assert unit_copy.ex_models  == unit.ex_models
    assert unit_copy.default_model.no_models == unit.default_model.no_models
