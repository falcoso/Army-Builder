# -*- coding: utf-8 -*-
"""
Created on Sat Jul  7 12:59:35 2018

@author: jones
"""

import main
import init
import pytest

init.init("Necron")

def test_army_list():
    """
    Checks adding of simple detachments and minimum requirement units in
    different formats
    """
    mock_inputs  = [["Battalion",
                     "b2", "C'tan Shard of the Deciever",
                     "1", "Necron Warriors", "Immortals"],
                    ["Patrol", "A1", '1']]

    for i in mock_inputs:
        main.input = lambda s: i.pop(0)
        army = main.ArmyList("Necron")
        army.add_detachment()
    return

def test_auto_naming():
    """Checks the automatic numbering of repeated detachment types"""
    mock_inputs = ["Patrol,Patrol",
                   "a1", "Necron Warriors",
                   "b2", "Immortals"]

    main.input = lambda s: mock_inputs.pop(0)
    army = main.ArmyList("Necron")
    army.add_detachment()
    for i in range(len(army.detachments)):
        assert army.detachments[i].name == "Patrol {}".format(i+1)
    assert army.detachment_names == ['Patrol 1', 'Patrol 2']
    return

def test_add_unit_prog_input():
    """Checks adding a unit from programmers input for default option"""
    mock_input = ["A1", "1", "Triarch Stalker"]
    main.input = lambda s: mock_input.pop(0)
    detach = main.Detachment("Patrol")
    detach.add_unit("Elites")
    stalker = detach.units["Elites"][0]
    assert stalker.name == "Triarch Stalker"
    assert stalker.pts == 171
    assert stalker.wargear == [init.WargearItem("Heat ray"), init.WargearItem("Massive forelimbs")]
    return

def test_invalid_input_handling():
    """
    Checks a range of different possible invalid inputs to make sure they are
    caught
    """
    mock_input = ["Test invalid", "A1", "1",
                  "Test invalid", "Break foc", "102", "Elites",
                  "Triarch something", "26", "Triarch Stalker"]
    main.input = lambda s: mock_input.pop(0)
    detach = main.Detachment("Patrol")
    detach.add_unit()
    stalker = detach.units["Elites"][0]
    assert stalker.name == "Triarch Stalker"
    assert stalker.pts == 171
    assert stalker.wargear == [init.WargearItem("Heat ray"), init.WargearItem("Massive forelimbs")]
    return

def test_add_unit_user_input():
    """Checks adding a unit from user input"""
    mock_input = ["A1", "1",
                  "fast attack", "1",
                  "fa", "1",
                  "3", "1"]
    main.input = lambda s: mock_input.pop(0)
    detach = main.Detachment("Patrol")
    for i in range(3):
        detach.add_unit()
        assert detach.units["Fast Attack"][-1].name == "Canoptek Scarabs"
    assert detach.units["Elites"][-1].name == "Deathmarks"
    return

def test_detachment_rename():
    """Checks renaming method for detachment"""
    mock_input = ["A1", "1"]
    main.input = lambda s: mock_input.pop(0)
    detach = main.Detachment("Patrol")
    detach.rename("Test Name", True)
    assert detach.name != detach.type
    assert detach.default_name == False
    assert detach.name == "Test Name"
    return

def test_unit_class():
    """Checks the attributes of the units class"""
    warriors = main.Unit("Necron Warriors", "Troops")
    assert warriors.pts == 120
    assert warriors.wargear == [init.WargearItem("Gauss flayer")]
    return

def test_re_size():
    """Checks the Unit.re_size() method"""
    warriors = main.Unit("Necron Warriors", "Troops")
    mock_input = ["test", 2, 15]
    main.input = lambda s: mock_input.pop(0)
    #first two should error but re-call to input
    warriors.re_size()
    assert warriors.pts == warriors.pts_per_model*15 #check valid input modifies the unit points

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
    unit = main.Unit("Catacomb Command Barge", "HQ")
    mock_input = ["test", "1b, 2c,3, 4"]
    main.input = lambda s: mock_input.pop(0)
    unit.change_wargear()
    wargear_selected = [init.WargearItem("Tesla cannon"),
                        init.WargearItem("Hyperphase sword"),
                        init.WargearItem("Phylactery"),
                        init.WargearItem("Resurrection orb")]
    for i in wargear_selected:
        assert i in unit.wargear

