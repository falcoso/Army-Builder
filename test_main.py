# -*- coding: utf-8 -*-
"""
Created on Sat Jul  7 12:59:35 2018

@author: jones
"""

import main
import pandas as pd
import pytest

main.init("Necron")

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
        army = main.army_list("Necron")
        army.add_detachment()

def test_auto_naming():
    """Checks the automatic numbering of repeated detachment types"""
    mock_inputs = ["Patrol,Patrol",
                   "a1", "Necron Warriors",
                   "b2", "Immortals"]

    main.input = lambda s: mock_inputs.pop(0)
    army = main.army_list("Necron")
    army.add_detachment()
    for i in range(len(army.detachments)):
        assert army.detachments[i].name == "Patrol {}".format(i+1)
    assert army.detachment_names == ['Patrol 1', 'Patrol 2']

def test_add_unit_prog_input():
    """Checks adding a unit from programmers input for default option"""
    mock_input = ["A1", "1", "Triarch Stalker"]
    main.input = lambda s: mock_input.pop(0)
    detach = main.detachment("Patrol")
    detach.add_unit("Elites")
    stalker = detach.units["Elites"][0]
    assert stalker.name == "Triarch Stalker"
    assert stalker.pts == 171
    assert stalker.wargear == ["Heat ray", "Massive forelimbs"]

def test_add_unit_user_input():
    """Checks adding a unit from user input"""
    mock_input = ["A1", "1",
                  "fast attack", "1",
                  "fa", "1",
                  "3", "1"]
    main.input = lambda s: mock_input.pop(0)
    detach = main.detachment("Patrol")
    for i in range(3):
        detach.add_unit()
        assert detach.units["Fast Attack"][-1].name == "Canoptek Scarabs"
    assert detach.units["Elites"][-1].name == "Deathmarks"


def test_detachment_rename():
    """Checks renaming method for detachment"""
    mock_input = ["A1", "1"]
    main.input = lambda s: mock_input.pop(0)
    detach = main.detachment("Patrol")
    detach.rename("Test Name", True)
    assert detach.name != detach.type
    assert detach.default_name == False
    assert detach.name == "Test Name"

def test_unit_class():
    """Checks the attributes of the units class"""
    warriors = main.unit("Necron Warriors", "Troops")
    assert warriors.pts == 120
    assert warriors.wargear == ["Gauss flayer"]

def test_units_dict():
    """Checks the points calculations for the units dict"""
    detachments_dict, armoury_dict, units_dict = main.init("Necron", True)
    units = pd.read_excel("Necron_units.xlsx", sheetname=None, index_col=0, header=0)

    #check that points for wargear are being added
    assert units["Elites"].loc["Lychguard"]["Points per Model"] != units_dict["Elites"]["Lychguard"].pts


