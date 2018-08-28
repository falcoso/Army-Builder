# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 22:45:30 2018

@author: jones
"""
import numpy as np
import string
import re

import init
import option_parser

class ArmyList():
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
            for index, keys in enumerate(init.detachments_dict.keys()):
                print(str(index +1)+'. ' + keys)

            #get input to decide which detachments to add
            user_input = input(">> ")

        #allows users to add multiple detachments at once
        for i in user_input.split(','):
            i = i.replace(' ','')   #remove any extra spaces added by user
            try:
                self.detachments.append(Detachment(i))
            except KeyError:
                i = list(init.detachments_dict.keys())[int(i)-1]
                self.detachments.append(Detachment(i))
            self.detachment_names.append(i)

        #number repeated detachment types
        for keys in init.detachments_dict.keys():
            if self.detachment_names.count(keys) > 1:
                counter = 1
                for i in range(len(self.detachment_names)):
                    if self.detachments[i].type == keys and self.detachments[i].default_name:
                        self.detachments[i].rename(keys + ' ' + str(counter))
                        self.detachment_names[i] = keys + ' ' + str(counter)
                        counter += 1
        return

class Detachment():
    """
    Collects together all the units within a detachment, making sure that
    minimum requirements are met and keeping track of points.
    """
    def __init__(self, detachment_type, instance_no=None):
        self.foc = init.detachments_dict[detachment_type]["foc"]
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
                success = self.add_unit(keys)
                if not success:
                    print("Exiting addition of compulsory units, note detachment may not be legal")
                    return

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
        def get_battlefield_role():
            """Helper function to get battlefield role as user input"""
            roles = ["HQ", "Troops", "Elites", "Fast Attack", "Heavy Support"]
            print("Which Battlefield Role would you like to add?")
            for index, role in enumerate(roles):
                print(str(index+1)+'. '+role)
            battlefield_role = input(">> ")
            battlefield_role = battlefield_role.replace(' ', '')

            if battlefield_role.isdigit():
                try:
                    battlefield_role = roles[int(battlefield_role)-1]
                except IndexError:
                    print("{} is invalid, please enter the index or name of the battlefield role you wish to add".format(battlefield_role))
                    battlefield_role = get_battlefield_role()
            #sanitise inputs
            elif battlefield_role.lower() == "hq":
                battlefield_role = "HQ"
            elif battlefield_role.lower() == "troops":
                battlefield_role = "Troops"
            elif battlefield_role.lower() == "elites":
                battlefield_role = "Elites"
            elif battlefield_role.lower() in {'hs', 'heavysupport'}:
                battlefield_role = "Heavy Support"
            elif battlefield_role.lower() in {'fa', 'fastattack'}:
                battlefield_role = "Fast Attack"
            elif battlefield_role.lower() in {'q', 'exit', 'cancel', 'quit', 'return', ''}:
                return False
            else:
                print("{} is invalid, please enter the index or name of the battlefield role you wish to add".format(battlefield_role))
                battlefield_role = get_battlefield_role()

            return battlefield_role

        def get_unit(battlefield_role):
            print("\nWhich {} unit would you like to add?".format(battlefield_role))
            #if HQ add named characters as well
            if battlefield_role == "HQ":
                print("Named Characters (Including Wargear):")
                keys = list(init.units_dict["Named Characters"].keys())
                top_len = len(max(keys, key=len))
                for index, [keys, value] in enumerate(init.units_dict["Named Characters"].items()):
                    print("A" + str(index+1)+". " + keys.ljust(top_len) + "\t({}pts)".format(value.pts))
                print('') #create space between set of options

                print("Other Characters (Including base Wargear):")
                units = list(init.units_dict[battlefield_role].keys())
                top_len = len(max(units, key=len))
                for index, [keys, value] in enumerate(init.units_dict[battlefield_role].items()):
                    print("B" + str(index+1) + ". " + keys.ljust(top_len) + "\t({}pts)".format(value.pts))
            else:
                #print available models and their points with the points value
                #left adjusted so they are in the same column
                print("Available Models (Including base Wargear):")
                units = list(init.units_dict[battlefield_role].keys())
                top_len = len(max(units, key=len))
                for index, [keys, value] in enumerate(init.units_dict[battlefield_role].items()):
                    print(str(index+1) + ". " + keys.ljust(top_len) + "\t({}pts for {} models)".format(value.pts*value.size[0], value.size[0]))

            user_input = input(">> ")
            try:
                if user_input.lower() in {'q', 'exit', 'cancel', 'quit', 'return'}:
                    return False
                elif len(user_input) < 4:
                    if user_input[0].isdigit():
                        user_input = list(init.units_dict[battlefield_role].keys())[int(user_input)-1]
                    elif user_input[0] in {'A','a'}:
                        user_input = list(init.units_dict["Named Characters"].keys())[int(user_input[1:])-1]
                    elif user_input[0] in {'B','b'}:
                        user_input = list(init.units_dict["HQ"].keys())[int(user_input[1:])-1]

                self.units[battlefield_role].append(Unit(user_input, battlefield_role))
            except (KeyError, IndexError):
                print("{} is not a valid option, please select the unit by name or input".format(user_input))
                print("To quit please enter 'q'")
                get_unit(battlefield_role)
            return

        if battlefield_role == None:
            battlefield_role = get_battlefield_role()

        #in case user chooses to exit
        if not battlefield_role:
            return False
        #check if user decides to exit
        return get_unit(battlefield_role)



class Unit(init.UnitTypes):
    def __init__(self, unit_type, battlefield_role):
        self.type = unit_type
        self.battlefield_role = battlefield_role
        self.name = self.type
        self.default_name = True
        #catch any characters being added
        try:
            base_unit = init.units_dict[self.battlefield_role][self.type]
        except KeyError:
            base_unit = init.units_dict["Named Characters"][self.type]

        self.wargear  = base_unit.wargear #init.WargearItem
        self.options  = base_unit.options #str
        self.base_pts = base_unit.base_pts
        self.no_models   = base_unit.size[0]
        self.size_range  = base_unit.size
        self.re_calc_points()
        print(self.name + " added to detachment")
        return

    def re_size(self, size=None):
        """Changes the size of the unit"""

        def get_size():
            print("Enter the new size of the unit ({}-{})".format(*self.size_range))
            try:
                size = int(input(">>"))
            except ValueError:
                print("Please enter integer number for unit size")
                size = get_size()

            #check valid int is within size range
            if size < self.size_range[0] or size > self.size_range[1]:
                print("Invalid size. Unit must be between {} and {} models".format(*self.size_range))
                size = get_size()
            return size

        if size == None:
            size = get_size()
        elif type(size) != int:
            raise TypeError("Invalid direct input for resize of {}. Size must be an integer".format(size))
        elif size < self.size_range[0] or size > self.size_range[1]:
            raise ValueError("Invalid size. Unit must be between {} and {} models".format(*self.size_range))

        self.no_models = size
        self.re_calc_points()
        return

    def re_calc_points(self):
        """Updates any points values after changes to the unit"""
        self.wargear_pts = 0
        if self.wargear != None:
            for i in self.wargear:
                self.wargear_pts += i.points
        self.pts_per_model = self.base_pts + self.wargear_pts
        self.pts = self.pts_per_model*self.no_models
        return

    def change_wargear(self, split_only=False):
        """Change the wargear options for the unit"""

        def get_user_options():
            """Helper to get user input option"""
            #show options available
            print("Options available:")
            if self.options == None:
                print("There are no wargear options available for this unit.")
                return

            self.parser.options_list = []
            for index, option in enumerate(self.options):
                output = "{}.".format(index+1)
                self.parser.parse2(option)
                output += self.parser.ret
                print(output)

            #get user input
            if not split_only:
                print("Input format <index>[<sub_index>]")
#                user_input = input(">> ")
                user_input = '1.b'
                #santise and create list of options
                user_input = user_input.lower()
                user_input = user_input.translate(str.maketrans('','',string.punctuation))
                user_input = re.findall(r'[0-9][a-zA-Z]?', user_input)

                wargear_to_add = []
                #find the item each user input refers to
                for choice in user_input:
                    try:
                        #convert the choice number into the index to select the item
                        index = np.zeros(2, dtype=np.int8)
                        index[0] = int(choice[0]) -1
                        sel_option = self.parser.options_list[index[0]]

                        if len(choice) == 2:
                            #find the index corresponding to the lowercase letter
                            for index[1], i in enumerate(string.ascii_lowercase):
                                if i == choice[1]:
                                    break #index[1] will save as the last enumerate
                            sel_option.select(index[1])

                        elif len(choice) == 1:
                            pass
                        else:
                            raise ValueError("{} is not valid, input should be of format <index><sub-index>".format(choice))

                        wargear_to_add.append(sel_option)

                    except ValueError:
                        print('{} is not a valid option please input options in format <index><sub-index>'.format(choice))
                        wargear_to_add = get_user_options()

                return wargear_to_add

        #show initial unit state
        print("Current loadout for {}".format(self.name))
        print(self)
        self.parser = option_parser.OptionParser(self.wargear)
        self.parser.build()

        wargear_to_add = get_user_options()
        if not split_only:
            for wargear in wargear_to_add:
                if type(wargear) == option_parser.Option:
                    if wargear.no_required > self.no_models:
                        if not wargear.selected in self.wargear:
                            print("Unable to add {} as {} models are required. The unit size is currently {}".format(wargear.selected,
                                  wargear.no_required,
                                  self.no_models))
                        continue
                    for i in wargear.items_involved:
                        if i in self.wargear:
                            self.wargear.remove(i)
                            #may need to check if there are cases when multiple options need to be replaced
                            break
                    self.wargear.append(wargear.selected)
                else:
                    self.wargear.append(wargear)
        self.re_calc_points()


        return

    def __repr__(self):
        output = self.name
        if not self.default_name:
            output += "(" + self.type + ")"

        output += "\t\t{}pts\n".format(self.pts)
        if self.wargear != None:
            for i in self.wargear:
                output += "\t" + i.__repr__() + '\n'

        return output

class Model():
    """Keeps track of variations in the model makeup of a unit"""
    def __init__(self, parent_unit, wargear=None):
        self.base_pts = parent_unit.base_pts
        if wargear:
            self.wargear = wargear
        else:
            self.wargear = parent_unit.wargear


if __name__ == "__main__":
    print("Army Builder Version 1.0")
    faction = "Necron"
    init.init(faction)
    immortals = Unit("Lychguard", "Elites")
    immortals.change_wargear(split_only=False)
    print(immortals)
