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
    mock_inputs  = [["Battalion",
                     "b2", "C'tan Shard of the Deciever",
                     "1", "Necron Warriors", "Immortals"],
                    ["Patrol", "A1", '1']]

    for i in mock_inputs:
        main.input = lambda s: i.pop(0)
        army = main.army_list("Necron")
        army.add_detachment()
#        print(army.detachments[0])

def test_auto_naming():
    mock_inputs = ["Patrol,Patrol",
                   "a1", "Necron Warriors",
                   "b2", "Immortals"]

    main.input = lambda s: mock_inputs.pop(0)
    army = main.army_list("Necron")
    army.add_detachment()
    for i in range(len(army.detachments)):
        assert army.detachments[i].name == "Patrol {}".format(i+1)
    assert army.detachment_names == ['Patrol 1', 'Patrol 2']

def test_add_unit():
    mock_input = ["A1", "1", "Triarch Stalker"]
    main.input = lambda s: mock_input.pop(0)
    detach = main.detachment("Patrol")
    detach.add_unit("Elites")
    stalker = detach.units["Elites"][0]
    assert stalker.name == "Triarch Stalker"
    assert stalker.pts == 171
    assert stalker.wargear == ["Heat ray", "Massive forelimbs"]

