# -*- coding: utf-8 -*-
"""
Created on Sat Jul  7 12:59:35 2018

@author: jones
"""

import main
import pandas as pd



#Open list of possible detachments and generate object for each one
main.init()


faction = "Necron"
units = pd.read_excel("{}_units.xlsx".format(faction), sheetname=None, index_col=0, header=0)
units_dict = {}
for key, value in units.items():
    units_dict[key] = {}
    for index, rows in units[key].iterrows():
        units_dict[key][index] = main.unit_types(index,rows)

armoury = pd.read_excel("{}_armoury.xlsx".format(faction), sheetname=None, index_col=0, header=0)
armoury_dict = {}
for key, value in armoury.items():
    armoury_dict[key] = {}
    for index, rows in armoury[key].iterrows():
        armoury_dict[key][index] = rows[0]

army = main.army_list("Necrons")
army.add_detachment()