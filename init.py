# -*- coding: utf-8 -*-
"""
Created on Sat Jul  7 13:06:29 2018

@author: jones
"""

import pandas as pd
import numpy as np
import glob

def wargear_search_base(item):
    """
    Searches for a given wargear item in the armoury dictionary
    """
    for key, obj in armoury_dict.items():
        if item in obj:
            return obj[item]
    raise KeyError("{} not found in Armoury/*.csv file".format(item))
    return

class WargearItem():
    def __init__(self, item):
        self.item = item
        self.no_of = 1
        if '*' in item:
            self.no_of = int(item.split('*')[0])
            self.item  = item.split('*')[1]
        self.points = self.no_of*self.wargear_search(self.item)
        return

    def wargear_search(self, item):
        return wargear_search_base(item)

    def __repr__(self, comparison=None, tidy=False):
        if self.no_of == 1:
            ret = self.item
        else:
            ret = str(self.no_of) + ' ' + self.item + 's'

        ret = ret.ljust(24)
        if comparison:
            ret += " \t(net {}pts per model)".format(self.points-comparison.points)
        elif self.points != 0:
            ret += " \t({}pts per model)".format(self.points)
        return ret

    def __mul__(self, integer):
        self.points = self.points*integer
        self.no_of  = self.no_of*integer
        return self

    def __add__(self, other_item):
        if type(other_item) == MultipleItem:
            other_item.item.append(self.item)
            other_item.points += self.points
            return other_item

        else:
            ret = MultipleItem(self, other_item)
            return ret

    def __eq__(self, other):
        try:
            if self.item != other.item or self.no_of != self.no_of or self.points != self.points:
                return False
            return True
        except:
            return False

    def __hash__(self):
            return hash((tuple(self.item), self.no_of, self.points))

class MultipleItem(WargearItem):
    def __init__(self, *args, storage=False):
        if type(args[0]) == str:
            args = (WargearItem(i) for i in args)
        self.item = list(map(lambda s: s.item, args))
        self.points = 0
        self.no_of  = 1
        self.storage = storage
        for i in args:
            self.points += i.points
        return

    def __mul__(self, other):
        raise TypeError("Multiplication of MultiplItem types not yet defined")
        return

    def __add__(self, other_item):
        if type(other_item) == MultipleItem:
            self.item += other_item.item
        else:
            self.item.append(other_item.item)
        self.points += other_item.points
        return self

    def __repr__(self, comparison=None):
        ret = ''
        for i in range(len(self.item)):
            ret += self.item[i]
            if i == len(self.item) - 1:
                pass
            elif i == len(self.item) - 2:
                ret += ' & '
            else:
                ret += ', '

        if comparison:
            ret += " \t(net {}pts per model)".format(self.points-comparison.points)
        else:
            ret += " \t({}pts per model)".format(self.points)
        return ret

class UnitTypes():
    """
    Class to group together the properties and options of a unit available to a
    given faction in the army list
    """
    def __init__(self, name, props):
        self.name = name
        try:
            self.base_pts = int(props[1])
        except:
            raise ValueError("Unable to load base_pts from {} for {}".format(props[1],self.name))
        self.pts = self.base_pts
        if props[3] != props[3]:
            self.options = None
        else:
            self.options = props[3].split(', ')

        #if range of unit size, save as array, otherwise single number
        try:
            self.size = tuple([int(i) for i in props[0].split('-')])
        except AttributeError:
            self.size = tuple([int(props[0])])


        if props[2] != props[2]: #if entry is nan
            self.wargear = None
        else:
            self.wargear = []
            #split list if multiple wargear items in temporary variable for
            #processing
            wargear_temp = props[2].split(', ')
            for i in wargear_temp:
                try:
                    self.wargear.append(WargearItem(i))
                except KeyError:
#                    try:
                    self.wargear.append(MultipleItem(*i.split('/'), storage=True))
#                    except:
#                        raise KeyError("{} for {} not found in Armoury/*.csv file".format(i, self.name))

        #find default wargear costs
        self.wargear_pts = 0
        if self.wargear == None:
            return
        else:
            for i in self.wargear:
                if type(i) == MultipleItem:
                    self.wargear_pts +=  i.wargear_search(i.item[0])
                else:
                    self.wargear_pts += i.points

        self.pts += self.wargear_pts
        return

    def multiple_option(self, option):
        no_of, wargear = option.split('*')
        return "{} {}s".format(no_of, wargear), self.wargear_search(wargear)*int(no_of)

    def wargear_search(self, item):
        try:
            return wargear_search_base(item)
        except KeyError:
            raise KeyError("{} for {} not found in _armoury.xlsx file".format(item, self.name))
        return

    def __repr__(self):
        output = self.name + "\t" + str(self.pts) + "pts per model\t"
        if self.wargear != None:
            for i in self.wargear:
                output += i.__repr__() +", "
        return output

def extract_files(folder):
    """Creates a dictionary of all the csv files in the given folder"""
    files = glob.glob(folder + "/*.csv")
    ret = {}
    for file in files:
        name = file.replace(folder + "\\", '')
        name = name.replace(".csv", '')
        ret[name] = pd.read_csv(file, index_col=0, header=0)
    return ret

def init(faction, return_out=False):
    """
    Initialises the global variables for the chosen faction
    """
    #Open list of possible detachments and generate object for each one
    detachments = pd.read_csv("./Detachments.csv", header=0, index_col=0)
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
    armoury = extract_files("{}/Armoury".format(faction))
    global armoury_dict
    armoury_dict = {}
    for key in armoury.keys():
        armoury_dict[key] = {}
        for index, rows in armoury[key].iterrows():
            armoury_dict[key][index] = rows[0]

    units = extract_files("{}/Units".format(faction))
    global units_dict
    units_dict = {}
    for key in units.keys():
        units_dict[key] = {}
        for index, rows in units[key].iterrows():
            units_dict[key][index] = UnitTypes(index,rows)

    if return_out:
        return detachments_dict, armoury_dict, units_dict
    return

if __name__ == '__main__':
    init('Tau')