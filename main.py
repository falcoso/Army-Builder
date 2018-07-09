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

        #define list of names to make searching and labelling easier
        self.detachment_names = []
        return

    def add_detachment(self, user_input=None):
        """Adds a detachment to the army list"""

        if user_input == None:

            print("Which detachment would you like to add?")
            for index, keys in enumerate(detachments_dict.keys()):
                print(str(index +1)+'. ' + keys)

            #get input to decide which detachments to add
            user_input = input(">> ")

        #allows users to add multiple detachments at once
        for i in user_input.split(','):
            i = i.replace(' ','')   #remove any extra spaces added by user
            try:
                self.detachments.append(detachment(i))
            except KeyError:
                i = list(detachments_dict.keys())[int(i)-1]
                self.detachments.append(detachment(i))
            self.detachment_names.append(i)

        #number repeated detachment types
        for keys in detachments_dict.keys():
            if self.detachment_names.count(keys) > 1:
                counter = 1
                for i in self.detachments:
                    if i.type == keys and i.default_name:
                        i.rename(keys + ' ' + str(counter))
                        counter += 1
        return

class detachment():
    def __init__(self, detachment_type, instance_no=None):
        self.foc = detachments_dict[detachment_type]
        self.type = detachment_type
        self.name = self.type
        self.default_name = True
        self.units = {"HQ":[],
                      "Troops":[],
                      "Elites":[],
                      "Fast Attack":[],
                      "Heavy Support":[]}

        if instance_no != None:
            self.name += ' ' + str(instance_no)

    def __repr__(self):
        return self.name

    def rename(self, new_name, user_given=False):
        """
        Changes the name of the detachment to the given new_name string,
        user_given should only be True if the name change is from the user, and
        not the addition of numbers to disambiguiate between multiple
        detachments of the same type
        """
        self.name = new_name
        if user_given:
            self.default_name = False

    def add_unit(self, battlefield_role=None):
        """ Adds a unit to the detachment"""
        #list battlefield roles of chosen unit
        if battlefield_role == None:

            roles = ["HQ", "Troops", "Elites", "Fast Attack", "Heavy Support"]
            print("Which Battlefield Role would you like to add?")
            for index, role in enumerate(roles):
                print(str(index)+'. '+role)
            battlefield_role = input(">> ")
            battlefield_role = battlefield_role.replace(' ', '')

            try:
                battlefield_role = roles[int(battlefield_role)]
            except:
                #sanitise inputs
                if battlefield_role == "hq" or battlefield_role == "HQ":
                    battlefield_role = "HQ"
                elif "roop" in battlefield_role:
                    battlefield_role = "Troops"
                elif "lite" in battlefield_role:
                    battlefield_role = "Elites"
                elif "eavy" in battlefield_role or battlefield_role == "HS" or battlefield_role == "hs":
                    battlefield_role = "Heavy Support"
                elif "ast" in battlefield_role or battlefield_role == "FA" or battlefield_role == "fa":
                    battlefield_role = "Fast Attack"

        #list available units from that role
        print("\nWhich {} unit would you like to add?".format(battlefield_role))
        #if HQ add named characters as well
        if battlefield_role == "HQ":
            print("Named Characters (Including Wargear):")
            keys = list(units_dict["Named Characters"].keys())
            top_len = len(max(keys, key=len))
            for index, [keys, value] in enumerate(units_dict["Named Characters"].items()):
                print("A" + str(index+1)+". " + keys.ljust(top_len) + "\t({}pts)".format(value.pts))
            print('')

            print("Other Characters (Without Wargear):")
            units = list(units_dict[battlefield_role].keys())
            top_len = len(max(units, key=len))
            for index, [keys, value] in enumerate(units_dict[battlefield_role].items()):
                print("B" + str(index+1) + ". " + keys.ljust(top_len) + "\t({}pts)".format(value.pts))

        else:
            #print available models and their points
            print("Available Models (Without Wargear):")
            units = list(units_dict[battlefield_role].keys())
            top_len = len(max(units, key=len))
            for index, [keys, value] in enumerate(units_dict[battlefield_role].items()):
                print(str(index+1) + ". " + keys.ljust(top_len) + "\t({}pts)".format(value.pts))

#            unit = input(">> ")
#            try:
#                self.detachments.append(detachment(i))
#            except KeyError:
#                i = list(detachments_dict.keys())[int(i)-1]
#                self.detachments.append(detachment(i))
#            self.detachment_names.append(i)
class unit():
    def __init__(self, name, properties):
        pass


class detachment_types():
    """
    Class to group together the properties and benefits of each detachment
    available to an army
    """
    def __init__(self, name, props):
        self.name = name
        self.command_points = int(props[0])
        self.hq =        np.array([int(i) for i in props[1].split('-')])
        self.troops =    np.array([int(i) for i in props[2].split('-')])
        self.elites =    np.array([int(i) for i in props[3].split('-')])
        self.fast_at =   np.array([int(i) for i in props[4].split('-')])
        self.heavy_sup = np.array([int(i) for i in props[5].split('-')])

class unit_types():
    """
    Class to group together the properties and options of a unit available to a
    given faction in the army list
    """
    def __init__(self, name, props):
        self.name = name

        #if range of unit size, save as array, otherwise single number
        try:
            self.size = np.array([int(i) for i in props[0].split('-')])
        except AttributeError:
            self.size = props[0]

        self.pts = int(props[1])

        if props[2] != props[2]: #if entry is nan
            self.wargear = None
        else:
            self.wargear = []
            #split list if multiple wargear items in temporary variable for
            #processing
            wargear_temp = props[2].split(',')
            for i in wargear_temp:
                if '*' in i:
                    i = i.split('*')
                    #check to see if first item is a number i.e. that the li
                    i[0] = int(i[0])
                    for j in range(i[0]):
                        self.wargear.append(i[-1])
                else:
                    self.wargear.append(i)

    def __repr__(self):
        output = self.name + "\t" + str(self.pts) + "pts per model\t"
        if self.wargear != None:
            for i in self.wargear:
                output += i +", "
        return output

def init(faction):
    """
    Initialises the global variables for the chosen faction
    """
    #Open list of possible detachments and generate object for each one
    detachments = pd.read_excel("./Detachments.xlsx", header=0, index_col=0)
    global detachments_dict
    detachments_dict = {}
    for index, rows in detachments.iterrows():
        detachments_dict[index] = detachment_types(index, rows)

    #determine faction of armylist and open units and wargear data
    global units
    units = pd.read_excel("{}_units.xlsx".format(faction), sheetname=None, index_col=0, header=0)
    global units_dict
    units_dict = {}
    for key in units.keys():
        units_dict[key] = {}
        for index, rows in units[key].iterrows():
            units_dict[key][index] = unit_types(index,rows)

    armoury = pd.read_excel("{}_armoury.xlsx".format(faction), sheetname=None, index_col=0, header=0)
    global armoury_dict
    armoury_dict = {}
    for key in armoury.keys():
        armoury_dict[key] = {}
        for index, rows in armoury[key].iterrows():
            armoury_dict[key][index] = rows[0]

if __name__ == "__main__":
    print("Army Builder Version 1.0")
#    print("Which army are you using?")
#    faction = input(">> ")
    faction = "Necron"
    init(faction)
