# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 22:45:30 2018

@author: jones
"""
import pandas as pd
import os, sys
import numpy as np

class army_list():
    """
    Overarching class to collect together all the detachments and keep track
    of the army's factions and properties
    """
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
                for i in range(len(self.detachment_names)):
                    if self.detachments[i].type == keys and self.detachments[i].default_name:
                        self.detachments[i].rename(keys + ' ' + str(counter))
                        self.detachment_names[i] = keys + ' ' + str(counter)
                        counter += 1
        return

class detachment():
    """
    Collects together all the units within a detachment, making sure that
    minimum requirements are met and keeping track of points.
    """
    def __init__(self, detachment_type, instance_no=None):
        self.foc = detachments_dict[detachment_type]["foc"]
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

        #populate compulsory slots
        for keys, values in self.units.items():
            while len(values) < self.foc[keys][0]:
                print("***Adding compulsory units from " + keys + "***")
                self.add_unit(keys)

    def __repr__(self):
        output = "***" + self.name + "***\n"
        for key, value in self.units.items():
            if len(value) != 0:
                output += "*" + key + "*\n"
                for i in value:
                    output += i.__repr__() + "\n"
                output += "\n"

        return output

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
                print(str(index+1)+'. '+role)
            battlefield_role = input(">> ")
            battlefield_role = battlefield_role.replace(' ', '')

            try:
                battlefield_role = roles[int(battlefield_role)-1]
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

            print("Other Characters (Including base Wargear):")
            units = list(units_dict[battlefield_role].keys())
            top_len = len(max(units, key=len))
            for index, [keys, value] in enumerate(units_dict[battlefield_role].items()):
                print("B" + str(index+1) + ". " + keys.ljust(top_len) + "\t({}pts)".format(value.pts))

            user_input = input(">> ")
            if len(user_input) < 3:
                if user_input[0] in ['A','a']:
                    user_input = list(units_dict["Named Characters"].keys())[int(user_input[1:])-1]
                    self.units[battlefield_role].append(unit(user_input, battlefield_role))
                elif user_input[0] in ['B','b']:
                    user_input = list(units_dict["HQ"].keys())[int(user_input[1:])-1]
                    self.units[battlefield_role].append(unit(user_input, battlefield_role))
                else:
                    raise ValueError("Invalid user input for HQ selection")
            else:
                self.units[battlefield_role].append(unit(user_input, battlefield_role))

        else:
            #print available models and their points
            print("Available Models (Including base Wargear):")
            units = list(units_dict[battlefield_role].keys())
            top_len = len(max(units, key=len))
            for index, [keys, value] in enumerate(units_dict[battlefield_role].items()):
                print(str(index+1) + ". " + keys.ljust(top_len) + "\t({}pts for {} models)".format(value.pts*value.size[0], value.size[0]))

            user_input = input(">> ")
            try:
                self.units[battlefield_role].append(unit(user_input, battlefield_role))
            except KeyError:
                user_input = list(units_dict[battlefield_role].keys())[int(user_input)-1]
                self.units[battlefield_role].append(unit(user_input, battlefield_role))

class unit():
    def __init__(self, unit_type, battlefield_role):
        self.type = unit_type
        self.battlefield_role = battlefield_role
        self.name = self.type
        self.default_name = True
        #catch any characters being added
        try:
            base_unit = units_dict[self.battlefield_role][self.type]
        except:
            base_unit = units_dict["Named Characters"][self.type]

        self.wargear = base_unit.wargear
        self.options = base_unit.options
        self.wargear_pts = base_unit.wargear_pts
        self.no_models   = base_unit.size[0]
        self.size_range  = base_unit.size
        self.pts_per_mod = base_unit.pts
        self.pts = self.pts_per_mod*self.no_models
        print(self.name + " added to detachment")
        return

    def __repr__(self):
        output = self.name
        if not self.default_name:
            output += "(" + self.type + ")"

        output += "\t\t{}pts\n".format(self.pts)
        if self.wargear != None:
            for i in self.wargear:
                output += "\t" + i + "\n"

        return output


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
            self.options = props[3].split(',')

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
                temp = i.split('*')
                #check to see if first item is a number i.e. that the li

                no_of = int(temp[0])
                temp = temp[1]
            else:
                temp = i
                no_of = 1

            if temp in armoury_dict["Range"]:
                self.wargear_pts += no_of*armoury_dict["Range"][temp]
            elif temp in armoury_dict["Melee"]:
                self.wargear_pts += no_of*armoury_dict["Melee"][temp]
            elif temp in armoury_dict["Other Wargear"]:
                self.wargear_pts += no_of*armoury_dict["Other Wargear"][temp]
            else:
                raise KeyError("{} for {} not found in _armoury.xlsx file".format(temp, self.name))

        self.pts += self.wargear_pts

    def __repr__(self):
        output = self.name + "\t" + str(self.pts) + "pts per model\t"
        if self.wargear != None:
            for i in self.wargear:
                output += i +", "
        return output

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

if __name__ == "__main__":
    print("Army Builder Version 1.0")
#    print("Which army are you using?")
#    faction = input(">> ")
    faction = "Necron"
    init(faction)
