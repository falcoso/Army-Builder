# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 16:48:48 2018

@author: jones
"""
import json
import pandas as pd

data = pd.read_excel("./Necron/Models.xlsx", index_col=0)
models = {}
keys = ["name", "no_per_unit", "wargear", "options"]
for index, props in data.iterrows():
    models[index] = {}
    for i in range(len(props)):
        if props[i] != props[i]:
            models[index][keys[i]] = None
        elif keys[i] == "no_per_unit":
            models[index]["no_per_unit"] = int(props[i])
        elif keys[i] in {"options", "wargear"}:
            models[index][keys[i]] = props[i].split(', ')
        else:
            models[index][keys[i]] = props[i]


with open("./Necron/Models.json", 'w') as fp:
    json.dump(models, fp)