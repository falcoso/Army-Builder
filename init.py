# -*- coding: utf-8 -*-
"""
Created on Sat Jul  7 13:06:29 2018

@author: jones
"""

import pandas as pd
import numpy as np

class unit_types():
    """
    Class to group together the properties and options of a unit available to a
    given faction in the army list
    """
    def __init__(self, name, props):
        self.name = name
        self.base_pts = int(props[1])
        self.pts = self.base_pts
        if props[3] != props[3]:
            self.options = None
        else:
            self.options = props[3].split(', ')

        #if range of unit size, save as array, otherwise single number
        try:
            self.size = np.array([int(i) for i in props[0].split('-')])
        except AttributeError:
            self.size = np.array([int(props[0])])


        if props[2] != props[2]: #if entry is nan
            self.wargear = None
        else:
            self.wargear = []
            #split list if multiple wargear items in temporary variable for
            #processing
            wargear_temp = props[2].split(', ')
            for i in wargear_temp:
                self.wargear.append(i)

        #find default wargear costs
        self.wargear_pts = 0
        if self.wargear == None:
            return

        for i in self.wargear:
            if '*' in i:
                option, points = self.multiple_option(i)
                self.wargear_pts += points
            else:
                self.wargear_pts += self.wargear_search(i)
        self.pts += self.wargear_pts
        return

    def multiple_option(self, option):
        no_of, wargear = option.split('*')
        return "{} {}s".format(no_of, wargear), self.wargear_search(wargear)*int(no_of)

    def wargear_search(self, item):
        """
        Searches for a given wargear item in the armoury dictionary
        """
        if item in armoury_dict["Range"]:
            return armoury_dict["Range"][item]
        elif item in armoury_dict["Melee"]:
            return armoury_dict["Melee"][item]
        elif item in armoury_dict["Other Wargear"]:
            return armoury_dict["Other Wargear"][item]
        else:
            raise KeyError("{} for {} not found in _armoury.xlsx file".format(item, self.name))
        return

    def __repr__(self):
        output = self.name + "\t" + str(self.pts) + "pts per model\t"
        if self.wargear != None:
            for i in self.wargear:
                output += i +", "
        return output

class option(unit_types):
    def __init__(self, option_str):
        self.no_models = 1

        #extract per number of options allowed for option
        if '-' in option_str:
            option_str = option_str.split('-')
            self.no_models = int(option_str[-1])
            option_str = option_str[-2]

        wargear_temp = option_str.split('/')
        self.wargear=[]
        for i in wargear_temp:
            temp_dict = {}
            if '*' in i:
                temp_dict["no_of"], temp_dict["wargear"] = i.split('*')
            if '+' in i:
                temp_dict["wargear"] = i.split('+')

    def __repr__():
        pass

def init(faction, return_out = False):
    """
    Initialises the global variables for the chosen faction
    """
    #Open list of possible detachments and generate object for each one
    detachments = pd.read_excel("./Detachments.xlsx", header=0, index_col=0)
    global detachments_dict
    detachments_dict = {}
    for index, rows in detachments.iterrows():
        detachments_dict[index] = {"cp": int(rows[0]),
                                   "foc": {"HQ":     np.array([int(i) for i in rows[1].split('-')]),
                                           "Troops": np.array([int(i) for i in rows[2].split('-')]),
                                           "Elites": np.array([int(i) for i in rows[3].split('-')]),
                                           "Fast Attack":   np.array([int(i) for i in rows[4].split('-')]),
                                           "Heavy Support": np.array([int(i) for i in rows[5].split('-')])}}

    #determine faction of armylist and open units and wargear data
    armoury = pd.read_excel("{}_armoury.xlsx".format(faction), sheetname=None, index_col=0, header=0)
    global armoury_dict
    armoury_dict = {}
    for key in armoury.keys():
        armoury_dict[key] = {}
        for index, rows in armoury[key].iterrows():
            armoury_dict[key][index] = rows[0]

    global units
    units = pd.read_excel("{}_units.xlsx".format(faction), sheetname=None, index_col=0, header=0)
    global units_dict
    units_dict = {}
    for key in units.keys():
        units_dict[key] = {}
        for index, rows in units[key].iterrows():
            units_dict[key][index] = unit_types(index,rows)

    if return_out:
        return detachments_dict, armoury_dict, units_dict
    return