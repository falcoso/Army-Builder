# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 22:45:30 2018

@author: jones
"""
import pandas as pd
import os, sys
import numpy as np

class army_list():
    def __init__(self, faction):
        self.faction = faction
        self.detachments = []
        return

    def add_detachment(self):
        print("Which detachment would you like to add?")
        for keys, items in detachments_dict.items():
            print(keys)
        self.detachments.append(detachment(input(">> ")))
        return

class detachment():
    def __init__(self, detachment_type):
        self.foc = detachments_dict[detachment_type]
        self.type = detachment_type

    def __repr__(self):
        return self.type


class detachment_types():
    def __init__(self, name, props):
        self.name = name
        self.command_points = int(props[0])
        self.hq =        np.array([int(i) for i in props[1].split('-')])
        self.troops =    np.array([int(i) for i in props[2].split('-')])
        self.elites =    np.array([int(i) for i in props[3].split('-')])
        self.fast_at =   np.array([int(i) for i in props[4].split('-')])
        self.heavy_sup = np.array([int(i) for i in props[5].split('-')])

class unit_types():
    def __init__(self, name, props):
        self.name = name
        try:
            self.size = np.array([int(i) for i in props[0].split('-')])
        except AttributeError:
            self.size = props[0]

        self.pts = int(props[1])




def init():
    detachments = pd.read_excel("./Detachments.xlsx", header=0, index_col=0)
    global detachments_dict
    detachments_dict = {}
    for index, rows in detachments.iterrows():
        detachments_dict[index] = detachment_types(index, rows)

if __name__ == "__main__":
    print("Army Builder Version 1.0")

    #Open list of possible detachments and generate object for each one
    init()

    #determine faction of armylist and open units and wargear data
#    print("Which army are you using?")
#    faction = input(">> ")
    faction = "Necron"
    units = pd.read_excel("{}_units.xlsx".format(faction), sheetname=None, index_col=0, header=0)
    global units_dict
    units_dict = {}
    for key, value in units.items():
        units_dict[key] = {}
        for index, rows in units[key].iterrows():
            units_dict[key][index] = unit_types(index,rows)

    armoury = pd.read_excel("{}_armoury.xlsx".format(faction), sheetname=None, index_col=0, header=0)
    global armoury_dict
    armoury_dict = {}
    for key, value in armoury.items():
        armoury_dict[key] = {}
        for index, rows in armoury[key].iterrows():
            armoury_dict[key][index] = rows[0]




