# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 22:45:30 2018

@author: jones
"""
import init
import unit_class
import re

class ArmyList():
    """
    Overarching class to collect together all the detachments and keep track
    of the army's factions and properties
    """
    def __init__(self, faction):
        self.faction = faction
        self.detachments = []
        self.cp = 0

        #define list of names to make searching and labelling easier
        self.detachment_names = []
        self.add_detachment()
        return

    def get_pts(self):
        """Calculates the total poins of the army"""
        pts = 0
        for i in self.detachments:
            pts += i.pts
        return pts

    def re_calc_cp(self):
        self.cp = 0
        for i in self.detachments:
            self.cp += i.cp

    def add_detachment(self, user_input=None):
        """Adds a detachment to the army list"""

        if user_input == None:

            print("Which detachment would you like to add?")
            for index, keys in enumerate(init.detachments_dict.keys()):
                print(str(index +1)+'. ' + keys)

            #get input to decide which detachments to add
            user_input = input(">> ")

        #allows users to add multiple detachments at once
        user_input = re.findall(r'[0-9]+|[a-zA-Z]+', user_input)
        for i in user_input:
            if i.isdigit():
                i = list(init.detachments_dict.keys())[int(i)-1]
            print("Adding {} to army".format(i))
            self.detachments.append(Detachment(i))
            self.detachment_names.append(i)
            self.cp += self.detachments[-1].cp

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

    def add_unit(self):
        """Wrapper to add unit to detachment in the army list"""
        def get_user_input():
            print("Which Detachment would you like to add the unit to?")
            for index, i in self.detachments:
                print("{}. {}".format(index+1, i.name))

            user_input = input(">> ")
            #FILTER OUT ANY PUNCTUATION
            if user_input.isdigit():
                if int(user_input) < len(self.detachments):
                    return user_input-1
                else:
                    print("{} is an invalid index".format(user_input))
            else:
                for index, i in self.detachment_names:
                    if i == user_input:
                        return index
                print("{} is not a valid option".format(user_input))

            return get_user_input()

        if len(self.detachments) == 1:
            self.detachments[0].add_unit()
        else:
            self.detachments[get_user_input].add_unit()

    def __repr__(self):
        ret = self.faction + '\n'
        for i in self.detachments:
            ret += i.__repr__()
        return ret

    def print_army(self):
        print(self)
        return

class Detachment():
    """
    Collects together all the units within a detachment, making sure that
    minimum requirements are met and keeping track of points.
    """
    def __init__(self, detachment_type, instance_no=None):
        self.foc = init.detachments_dict[detachment_type]["foc"]
        self.cp  = init.detachments_dict[detachment_type]["cp"]
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
                if success == False:
                    print("Exiting addition of compulsory units, note detachment may not be legal")
                    break
            if success == False:
                break
        self.re_calc_points()
        return

    def __repr__(self):
        output = "***" + self.name + "\t\t" + "Total:{}pts".format(self.pts) + "***\n"
        for key, value in self.units.items():
            if len(value) != 0:
                output += "*" + key + "*\n"
                for i in value:
                    output += i.__repr__() + "\n"
                output += "\n"

        return output

    def re_calc_points(self):
        """Updates any points values after changes to the unit"""
        self.pts = 0
        for key, unit in self.units.items():
            for i in unit:
                self.pts += i.pts
        return

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

                self.units[battlefield_role].append(unit_class.Unit(user_input, battlefield_role))
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

if __name__ == "__main__":
    print("Army Builder Version 1.0")
    print("Please enter the faction of the army you are creating:")
    faction = input(">> ")
    init.init(faction)
    army = ArmyList(faction)
    user_input = ''
    commands = {"add unit": army.add_unit,
                "add detachment": army.add_detachment,
                "print army": army.print_army}

    while user_input not in {'quit', 'exit'}:
        user_input = input(">> ")
        try:
            user_command = re.findall(r'[a-z][a-z ]*[a-z]', user_input)[0]
        except IndexError:
            continue

        tags = [i[1:] for i in re.findall(r'\-[A-Za-z0-9]*', user_input)]
        try:
            commands[user_command](*tags)
        except KeyError:
            print("{} command not found, try:".format(user_command))
            for i in commands:
                print('\t' + i)
