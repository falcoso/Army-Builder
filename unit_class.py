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
from collections import Counter

class Unit(init.UnitTypes):
    def __init__(self, unit_type, battlefield_role, size=None):
        self.type = unit_type
        self.name = self.type
        self.battlefield_role = battlefield_role
        self.default_name = True
        #catch any characters being added
        try:
            base_unit = init.units_dict[self.battlefield_role][self.type]
        except KeyError:
            base_unit = init.units_dict["Named Characters"][self.type]

        self.size_range  = base_unit.size
        self.options  = base_unit.options #list of str
        self.mod_str = base_unit.models
        self.wargear = copy.deepcopy(base_unit.wargear)
        self.models  = []
        if self.mod_str == None:
            self.models = [Model(no_models=self.size_range[0], base_pts=base_unit.base_pts)]
        else:
            self.re_size(size)

        self.re_calc_points()
        self.parser = option_parser.OptionParser(current_wargear=self.wargear)
        self.parser.build()
        return

    def re_calc_points(self):
        """Updates any points values after changes to the unit"""
        self.pts = 0
        for i in self.models:
            i.re_calc_points()
            try:
                self.pts += i.pts
            except AttributeError:
                continue

        if self.wargear != None:
            self.wargear_pts = 0
            for i in self.wargear:
                self.wargear_pts += i.points
            self.pts += self.wargear_pts*self.get_size()
        return self.pts

    def reset(self, user_call=True):
        """
        Returns the unit back to its initialised state. This may be useful if
        there are a lot of changes that need to be undone at once.
        """
        if user_call:
            print("Are you sure you wish to return {} back to default? [y]/n".format(self.name))
            user_input = input(">> ")
            if user_input != 'y' or '':
                return
        self.__init__(self.type, self.battlefield_role)
        return

    def get_size(self):
        """Get function to sum all the model sizes in the unit"""
        size = 0
        for i in self.models:
            size += i.no_models
        return size

    def get_wargear(self):
        """
        Returns a set containing all the wargear present across all models in
        the unit.
        """
        ret = set(copy.deepcopy(self.wargear))
        for i in self.models:
            if i.wargear is not None:
                for j in i.wargear:
                    ret.add(j)
        return ret

    def check_validity(self):
        """
        Checks that the unit is legal by looking at the size of the unit and
        the number of each type of model
        """
        #check sizes
        size = self.get_size()
        valid = True
        if size < self.size_range[0] or size > self.size_range[1]:
            valid = False
            print("{} has invalid size:\nsize range:{}-{}\tcurrent size:{}".format(self.name,
                                                                             *self.size_range,
                                                                             size))
        #count instances of each model
        count_dict = {}
        for i in self.models:
            if i.label in count_dict.keys():
                count_dict[i.label] += i.no_models
            else:
                count_dict[i.label] = i.no_models

        print(count_dict)

        #check model has a sufficient number
        for name, no_of in count_dict.items():
            if init.models_dict[name]["no_per_unit"] is not None:
                if init.models_dict[name]["no_per_unit"] < no_of:
                    valid = False
                    print("{} has too many of {}:\nmax allowed:{}\tcurrent amount:{}".format(self.name,
                                                                                      name,
                                                                                      init.models_dict[name]["no_per_unit"],
                                                                                      no_of))
        return valid

    def re_size(self, size=None):
        """Changes the number of models in the unit"""
        def get_user_size(size=None, prog_call=False):
            """Helper function to validate size input"""
            #print options if no user input
            if size is None:
                if self.mod_str is None:
                    print("Enter size of unit ({}-{}):".format(*self.size_range))
                else:
                    print("How many of each model would you like to add? ({}-{})".format(*self.size_range))
                    for index, i in enumerate(self.mod_str):
                        print(str(index+1) + '. ' + i)
                size = input(">> ")

            size2 = [int(i) for i in re.findall(r'[1-9][0-9]*|0', size)] #find all input numbers
            if size2 == []:
                print("{} is invalid, please enter a number".format(size))
                if prog_call:
                    raise ValueError("{} is invalid, please enter a number".format(size))
                size2 = get_user_size()
            if self.mod_str == None:
                if len(size2) != 1 or size2[0] < self.size_range[0] or size2[0] > self.size_range[1]:
                    print("{} is invalid, please enter a single number in the range {}-{}".format(size, *self.size_range))
                    if prog_call:
                        raise ValueError("{} is invalid, please enter a single number".format(size))
                    size2 = get_user_size()
            else:
                if len(size2) != len(self.mod_str):
                    print("{} is invalid, please enter a number for each available model".format(size))
                    if prog_call:
                        raise ValueError("{} is invalid, please enter a number for each available model. size2={}".format(size,size2))
                    size2 = get_user_size()
            return size2

        #initialising the unit
        if type(size) == int:
            size = str(size) #so that int does not raise error in the findall

        if size is not None:
            size = get_user_size(size, prog_call=True)
        else:
            size = get_user_size()


        if self.mod_str == None:
            self.models[0].no_models = size[0]
            self.re_calc_points()
            return

        if self.models == []:
            for model, no_of in zip(self.mod_str, size):
                if init.models_dict[model]["indep"]:
                    for i in range(no_of):
                        self.models.append(Model(model))
                else:
                    self.models.append(Model(model, no_of))

        else:
            #check if the model is already in the list
            for model, no_of in zip(self.mod_str, size):
                no_of = int(no_of)
                if init.models_dict[model]["indep"]:
                    counter = 0
                    for i in self.models:
                        #count how many instances of model and add difference
                        if i.label == model:
                            counter += 1
                    if no_of - counter < 0:
                        print("Unable to remove models as each is independant")
                        continue
                    else:
                        for i in range(no_of-counter):
                            self.models.append(Model(model))

                else:
                    #check to see if model exitsts already
                    flag = True
                    for i in self.models:
                        if i.label == model:
                            i.no_models = no_of
                            flag = False
                            break
                    #otherwise append to models list
                    if flag:
                        self.models.append(Model(model,no_of))
        self.re_calc_points()
        return

    def change_all_wargear(self, user_input=None):
        """
        Calls change_wargear on all models in the unit and the unit as a whole
        """
        if user_input is None:
            user_input = [None]*(len(self.models)+1)

        self.change_wargear(user_input=user_input.pop(0))
        for i in self.models:
            i.change_wargear(user_input=user_input.pop(0))

        self.re_calc_points()
        return

    def change_wargear(self, user_input=None):
        """
        Change the wargear options for the unit. split_only=True will only
        parse the option strings and a user_input can be submitted by
        programmer or left up to the user.
        """
        if self.options == None:
            print("{} has no options".format(self.name))
            return

        self.parser.current_wargear = self.wargear
        def get_user_options(user_input=None):
            """Helper function to validate and format user_input"""
            if user_input == None:
                print(self)
                print("Options:")
            self.parser.options_list = []
            for index, option in enumerate(self.options):
                self.parser.parse2(option)

            if user_input == None:
                print(self.parser)

            if user_input == None:
                user_input = input(">> ")

            #santise and create list of options
            user_input2 = user_input.lower()
            user_input2 = user_input2.translate(str.maketrans('','',string.punctuation))
            if user_input in {'q', 'quit', 'cancel', 'exit'}:
                print("Cancelling change wargear")
                return False
            user_input2 = re.findall(r'[0-9][a-zA-Z]?', user_input2)

            if len(user_input2) == 0: #no suitable regexes found
                print('{} is not a valid option please input options in format <index><sub-index>'.format(user_input))
                wargear_to_add = get_user_options()
                return wargear_to_add

            wargear_to_add = []

            for choice in user_input2:
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
                        raise IndexError("{} is not valid, input should be of format <index><sub-index>".format(choice))
                    wargear_to_add.append(sel_option)
                except IndexError:
                    print('{} is not a valid option please input options in format <index><sub-index>'.format(choice))
                    wargear_to_add = get_user_options()
            return wargear_to_add
        #######################################################################


        wargear_to_add = get_user_options(user_input) #-> list of option_parser.Option
        if not wargear_to_add: #user selected a quit option
            return
        for new_wargear in wargear_to_add:
            for i in new_wargear.items_involved:
                if i in self.wargear:
                    self.wargear.remove(i)

            if type(new_wargear.selected) == list:
                for j in new_wargear.selected:
                    self.wargear.append(j)
            else:
                self.wargear.append(new_wargear.selected)

        self.re_calc_points()
        return


    def __repr__(self):
        ret = self.name + '\t({}pts)'.format(self.pts)
        if self.mod_str is None:
            size = self.get_size()
            if size != 1:
                ret = str(size) + ' ' + ret

            if self.wargear is not None:
                for i in self.wargear:
                    ret += '\n\t' + i.__repr__()
            return ret

        for models, no_of in Counter(self.models).items():
            ret += '\n\t'
            if no_of != 1:
                ret += str(no_of) + ' '
            ret += models.__repr__(indent='\t')
        return ret


class Model(Unit):
    def __init__(self, name=None, no_models=1, base_pts=None):
        self.no_models = no_models
        self.label = name
        if name == None:
            self.base_pts = base_pts
            self.wargear  = None
            self.name = None
            self.re_calc_points()
            return

        root_data = init.models_dict[name]

        if root_data["wargear"] != None:
            self.wargear = list(map(lambda s: init.WargearItem(s), root_data["wargear"]))
        else:
            self.wargear = None

        self.options     = root_data["options"]
        self.base_pts    = root_data["pts"]
        self.no_per_unit = root_data["no_per_unit"]
        if root_data["name"] == None:
            self.name = self.label
        else:
            self.name = root_data["name"]
        self.parser = option_parser.OptionParser(self.wargear, unit=False)
        self.parser.build()
        self.re_calc_points()
        return

    def get_size(self):
        return self.no_models

    def re_calc_points(self):
        """Updates any points values after changes to the unit"""
        self.wargear_pts = 0
        if self.wargear is not None:
            for i in self.wargear:
                self.wargear_pts += i.points
        self.pts_per_model = self.base_pts + self.wargear_pts
        self.pts = self.pts_per_model*self.no_models
        return

    def __repr__(self, indent=''):
        if self.no_models == 0:
            return ''
        elif self.no_models == 1:
            ret = self.name
        else:
            ret = '{} {}s'.format(self.no_models, self.name)
        if self.wargear is not None:
            for i in self.wargear:
                ret += '\n\t' + indent + i.__repr__()
        return ret

    def __eq__(self, other):
        try:
            if self.name == other.name and set(self.wargear) == set(other.wargear):
                return True
            else:
                return False
        except:
            return False

    def __hash__(self):
        ret = hash(self.name) + hash(self.label)
        if self.wargear is not None:
            ret += hash(tuple(self.wargear))
        return ret

if __name__ == "__main__":
    init.init("Necron")
    dest = Unit("Anrakyr the Traveller", "HQ")
    print(dest)
    dest.change_all_wargear()

    print(dest)

