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

#print(detachments_dict.items())
army = main.army_list("Necron")
#army.add_detachment()
#army = main.detachment("Patrol")
#army.add_unit("Elites")
#print(type(army))
#for keys, values in units_dict.items():
#    print(keys)
#    for key2, values2 in values.items():
#        print(values2)