# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 17:52:37 2018

@author: jones
"""
import string
import re
import numpy as np
import copy

import init
import option_parser

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

        self.options  = base_unit.options #list of str
        self.size_range  = base_unit.size
        self.default_model = Model(base_unit, no_models=self.size_range[0]) #standard model to be added on resize
        self.ex_models = []              #any variation in the standard model as a list CONVERT TO SET WHEN SEARCHED
        self.re_calc_points()
        print(self.name + " added to detachment")
        return

    def re_calc_points(self):
        """Updates any points values after changes to the unit"""
        self.default_model.re_calc_points()
        self.pts = self.default_model.pts
        for i in self.ex_models:
            i.re_calc_points()
            self.pts += i.pts
        return

    def reset(self, user_call=True):
        """
        Returns the unit back to its initialised state. This may be useful if
        there are a lot of changes that need to be undone at once.
        """
        if user_call:
            print("Are you sure you wish to return {} back to default? [y]/n".format(self.name))
            user_input = input(">>")
            if user_input != 'y' or '':
                return
        self.__init__(self.type, self.battlefield_role)
        return

    def get_size(self):
        """Get function to sum all the model sizes in the unit"""
        size = self.default_model.no_models
        for i in self.ex_models:
            size += i.no_models
        return size

    def get_wargear(self):
        return self.default_model.wargear

    def re_size(self, size=None):
        """
        Changes the size of the unit by increasing the number of deafult models
        """

        def get_user_input():
            print("Enter the new size of the unit ({}-{})".format(*self.size_range))
            try:
                size = int(input(">>"))
            except ValueError:
                print("Please enter integer number for unit size")
                size = get_user_input()

            #check valid int is within size range
            if size < self.size_range[0] or size > self.size_range[1]:
                print("Invalid size. Unit must be between {} and {} models".format(*self.size_range))
                size = get_user_input()
            return size

        if size == None:
            size = get_user_input()
        elif type(size) != int:
            raise TypeError("Invalid direct input for resize of {}. Size must be an integer".format(size))
        elif size < self.size_range[0] or size > self.size_range[1]:
            raise ValueError("Invalid size. Unit must be between {} and {} models".format(*self.size_range))

        size_change = size - self.get_size()
        self.default_model.no_models += size_change
        self.re_calc_points()
        return

    def change_wargear(self, user_input=None, split_only=False):
        """
        Change the wargear options for the unit. split_only=True will only
        parse the option strings and a user_input can be submitted by
        programmer or left up to the user.
        """

        def get_user_options(user_input=None):
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
                print("Input format <index>[<sub_index>][-<no_of(default:max)>]")
                if user_input is None:
                    user_input = input(">> ")
                #santise and create list of options
                user_input = user_input.lower()
                user_input = user_input.translate(str.maketrans('','',string.punctuation))
                user_input = set(re.findall(r'[0-9][a-zA-Z]?', user_input))

                wargear_to_add = []
                #find the item each user input refers to
                if user_input == set(): #if user just hit enter giving empty input
                    wargear_to_add = get_user_options()

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
                            sel_option.select(0) #there will only eveer be one item to select
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
        self.parser = option_parser.OptionParser(self.default_model.wargear)
        self.parser.build()

        wargear_to_add = get_user_options(user_input) #get the list of wargear to modify the unit with
        if not split_only:
            for wargear in wargear_to_add:
                #check there are the correct amount of models in the unit to be legal
                if wargear.no_required == 1:
                    for i in wargear.items_involved:
                        if i in self.default_model.wargear:
                            self.default_model.wargear.remove(i)
                            #may need to check if there are cases when multiple options need to be replaced
                            break
                    self.default_model.wargear.append(wargear.selected)

                else:
                    if wargear.no_required > self.get_size():
                        if not wargear.selected in self.default_model.wargear:
                            print("Unable to add {} as {} models are required. The unit size is currently {}".format(wargear.selected,
                                  wargear.no_required,
                                  self.get_size()))
                            print("Would you like to re-size the unit to add this option?")
                            print("Input y to increase the unit size to {} for {}pts".format(wargear.no_required,
                                  self.pts_per_model*(wargear.no_required - self.get_size())))
                            re_size = input('>>')
                            if re_size == 'y':
                                pass
                        continue
                    else:
                        #create new model to be added
                        new_mod = copy.deepcopy(self.default_model)
                        current_size = self.get_size()
                        for i in wargear.items_involved:
                            if i in new_mod.wargear:
                                new_mod.wargear.remove(i)
                                #may need to check if there are cases when multiple options need to be replaced
                                break
                        new_mod.wargear.append(wargear.selected)
                        if new_mod in self.ex_models:
                            for index, mod in enumerate(self.ex_models):
                                if new_mod == mod:
                                    break
                            self.ex_models[index].no_models = current_size//wargear.no_required
                        elif new_mod == self.default_model:
                            continue
                        else:
                            new_mod.no_models = self.get_size()//wargear.no_required
                            self.ex_models.append(new_mod)

                        #change the no of default models
                        size_change = self.get_size() - current_size
                        self.default_model.no_models -= size_change
        self.re_calc_points()
        print(self)
        return

    def __repr__(self):
        output = self.name
        if not self.default_name:
            output += "(" + self.type + ")"

        no_of = self.get_size() != 1
        output = output.ljust(28) + "\t\t{}pts".format(self.pts)
        if len(self.ex_models) == 0:
            output += '\n\t' + self.default_model.__repr__(indent='\t', pts_footer=False, no_of=no_of)
        else:
            output += '\n\t' + self.default_model.__repr__(indent='\t', no_of=no_of)

        for i in self.ex_models:
            output += '\n\t' + i.__repr__(indent='\t')

        return output


class Model():
    """Keeps track of variations in the model makeup of a unit"""
    def __init__(self, parent_unit, no_models=1, wargear=None):
        self.base_pts = parent_unit.base_pts
        self.no_models = no_models
        if wargear is not None:
            self.wargear = wargear
        else:
            self.wargear = parent_unit.wargear
        self.re_calc_points

    def re_calc_points(self):
        """Updates any points values after changes to the unit"""
        self.wargear_pts = 0
        if self.wargear is not None:
            for i in self.wargear:
                self.wargear_pts += i.points
        self.pts_per_model = self.base_pts + self.wargear_pts
        self.pts = self.pts_per_model*self.no_models
        return

    def __eq__(self, other_model):
        try:
            if self.wargear == other_model.wargear:
                return True
            else:
                False
        except:
            return False

    def __repr__(self, indent='', pts_footer=True, no_of=True):
        if no_of:
            ret = "No. of: {}\n".format(self.no_models)
        else:
            ret = '\b'
        if self.wargear is not None:
            for i in self.wargear:
                ret += indent + i.__repr__() +'\n'
        if pts_footer:
            ret += "\t\t{}pts".format(self.pts)
        return ret