# -*- coding: utf-8 -*-
"""
Created on Sat Jul  7 12:59:35 2018

@author: jones
"""

import main
import pandas as pd

main.init("Necron")
faction = "Necron"

army = main.detachment("Patrol")
army.add_unit("HQ")

for keys, values in units_dict.items():
    print(keys)
    for key2, values2 in values.items():
        print(values2)