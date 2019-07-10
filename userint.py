"""
All Text-based UI functionality.

Classes:
--------
UI: Text-based user interface for the Army Builder.
"""

import re
import string
import numpy as np

import init
from army_list import ArmyList, Detachment
import squad


class UI:
    """
    Text-based user interface for the Army Builder.

    Public Attributes
    ----------
    army : army_list.ArmyList
        Overarching army list to be built.

    Public Methods
    --------------
    add_detachment(self):
        Gets the user choice of detchment, adds it to the army list and
        populates it with the minimum unit requirements.

    add_unit(self):
        Gets the user choice of unit and adds it to a user-chosen detachment.

    change_unit_wargear(self): Changes the wargear for a user-chosen unit.

    re_size_unit(self): Re-sizes the user-chosen unit to the desired size.

    print_army(self): Prints the current army.
    """
    def __init__(self):
        print("Army Builder Version 1.0")
        print("Please enter the faction of the army you are creating:")
        faction = input(">> ")
        init.init(faction)
        self.army = ArmyList(faction)  # create empty army list
        self.add_detachment()
        print(self.army)
        return

    def add_detachment(self):
        """
        Gets the user choice of detchment, adds it to the army list and
        populates it with the minimum unit requirements.
        """
        print("Which detachment would you like to add?")
        for index, keys in enumerate(init.detachments_dict.keys()):
            print(str(index + 1) + '. ' + keys)
        # get input to decide which detachments to add
        user_input = input(">> ")

        # allows users to add multiple detachments at once
        user_input = re.findall(r'[0-9]+|[a-zA-Z]+', user_input)
        for i in user_input:
            if i.isdigit():
                i = list(init.detachments_dict.keys())[int(i) - 1]
            print("Adding {} to army".format(i))
            detach = Detachment(i)

            # populate compulsory slots
            for keys, values in detach.units_dict.items():
                while len(values) < detach.foc[keys][0]:
                    print("***Adding compulsory units from " + keys + "***")
                    unit = self._create_user_unit(keys)
                    self._add_unit(detach, unit)

            self.army.add_detachment(detach)
        return

    def add_unit(self):
        """
        Gets the user choice of unit and adds it to a user-chosen detachment.
        """
        detach = self.army.detachments[self._get_user_detachment()]
        battlefield_role = self._get_user_battlefield_role()
        unit = self._create_user_unit(battlefield_role)
        self._add_unit(detach, unit)
        return

    def change_unit_wargear(self):
        """Changes the wargear for a user-chosen unit."""
        detach = self.army.detachments[self._get_user_detachment()]
        battlefield_role = self._get_user_battlefield_role()
        unit = self._get_user_unit(detach, battlefield_role)
        if unit.options is None:
            print("{} has no options".format(self.name))
            return
        wargear_to_add = self._get_user_options(unit)
        for i in wargear_to_add:
            print(i)
            print(i.selected)
        unit.change_wargear(wargear_to_add)
        return

    def re_size_unit(self):
        """Re-sizes the user-chosen unit to the desired size."""
        detach = self.army.detachments[self._get_user_detachment()]
        battlefield_role = self._get_user_battlefield_role()
        unit = self._get_user_unit(detach, battlefield_role)
        size = self._get_user_size(unit)
        unit.re_size(*size)
        return

    def print_army(self):
        """Prints the current army."""
        print(self.army)

    def _get_user_options(self, unit):
        """Gets the user-chosen option for a supplied unit."""
        print(unit)
        print("Options:")
        unit.parser.options_list = []
        for option in unit.options:
            unit.parser.parse2(option)

        print(unit.parser)
        user_input = input(">> ")

        # santise and create list of options
        user_input2 = user_input.lower()
        user_input2 = user_input2.translate(str.maketrans('', '', string.punctuation))
        if user_input in {'q', 'quit', 'cancel', 'exit'}:
            print("Cancelling change wargear")
            return False
        user_input2 = re.findall(r'[0-9][a-zA-Z]?', user_input2)

        if len(user_input2) == 0:  # no suitable regexes found
            print('{} is not a valid option please input options in format <index><sub-index>'.format(user_input))
            wargear_to_add = self._get_user_options(unit)
            return wargear_to_add

        wargear_to_add = []

        for choice in user_input2:
            try:
                # convert the choice number into the index to select the item
                index = np.zeros(2, dtype=np.uint8)
                index[0] = int(choice[0]) - 1
                sel_option = unit.parser.options_list[index[0]]

                if len(choice) == 2:
                    # find the index corresponding to the lowercase letter
                    for index[1], i in enumerate(string.ascii_lowercase):
                        if i == choice[1]:
                            break  # index[1] will save as the last enumerate
                    sel_option.select(index[1])

                elif len(choice) == 1:
                    sel_option.select(0)  # there will only eveer be one item to select
                else:
                    raise IndexError(
                        "{} is not valid, input should be of format <index><sub-index>".format(choice))
                wargear_to_add.append(sel_option)
            except IndexError:
                print(
                    '{} is not a valid option please input options in format <index><sub-index>'.format(choice))
                wargear_to_add = self._get_user_options(unit)
        return wargear_to_add

    def _get_user_size(self, unit):
        """Gets and validates the used-chosen size"""
        # print options if no user input
        if unit.mod_str is None:  # only one type of model in the unit
            print("Enter size of unit ({}-{}):".format(*unit.size_range))
        else:
            print("How many of each model would you like to add? ({}-{})".format(*unit.size_range))
            for index, i in enumerate(unit.mod_str):
                print(str(index + 1) + '. ' + i)
        size = input(">> ")

        size2 = [int(i) for i in re.findall(r'[1-9][0-9]*|0', size)]  # find all input numbers
        if size2 == []:  # no user input
            print("{} is invalid, please enter a number".format(size))
            size2 = self._get_user_size(unit)
        if unit.mod_str is None:  # more than one number or not in unit size range
            if len(size2) != 1 or size2[0] < unit.size_range[0] or size2[0] > unit.size_range[1]:
                print("{} is invalid, please enter a single number in the range {}-{}".format(size,
                                                                                              *unit.size_range))
                size2 = self._get_user_size(unit)
        else:
            if len(size2) != len(unit.mod_str):
                print("{} is invalid, please enter a number for each available model".format(size))
                size2 = self._get_user_size(unit)
        return size2



    def _get_user_unit(self, detach, battlefield_role):
        """Gets the user-chosen unit."""
        print("Which unit would you like to edit?")
        for index, i in enumerate(detach.units_dict[battlefield_role]):
            print("{}. {}".format(index+1, i))

        user_input = input(">> ")
        # FILTER OUT ANY PUNCTUATION
        if user_input.isdigit():
            if int(user_input) <= len(detach.units_dict[battlefield_role]) and int(user_input) > 0:
                return detach.units_dict[battlefield_role][int(user_input) - 1]
            else:
                print("{} is an invalid index".format(user_input))

        else:
            for index, i in enumerate(detach.units_dict[battlefield_role]):
                if i.name == user_input:
                    return index
            print("{} is not a valid option".format(user_input))

        return self._get_user_unit(detach, battlefield_role)

    def _get_user_detachment(self):
        """Gets the user-chosen detachment to edit and returns its index"""
        print("Which Detachment would you like to edit the unit to?")
        for index, i in enumerate(self.army.detachments):
            print("{}. {}".format(index + 1, i.name))

        user_input = input(">> ")
        # FILTER OUT ANY PUNCTUATION
        if user_input.isdigit():
            if int(user_input) <= len(self.army.detachments) and int(user_input) > 0:
                return int(user_input) - 1
            else:
                print("{} is an invalid index".format(user_input))
        else:
            for index, i in enumerate(self.army.detachment_names):
                if i == user_input:
                    return index
            print("{} is not a valid option".format(user_input))

        return self._get_user_detachment()

    def _create_user_unit(self, battlefield_role):
        """Gets the user-chosen unit to create for the given battlefield_role"""
        print("\nWhich {} unit would you like to add?".format(battlefield_role))
        # if HQ add named characters as well
        if battlefield_role == "HQ":
            print("Named Characters (Including Wargear):")
            keys = list(init.units_dict["Named Characters"].keys())
            top_len = len(max(keys, key=len))
            for index, [keys, value] in enumerate(init.units_dict["Named Characters"].items()):
                print("A" + str(index + 1) + ". " +
                      keys.ljust(top_len) + "\t({}pts)".format(value.pts))
            print('')  # create space between set of options

            print("Other Characters (Including base Wargear):")
            units = list(init.units_dict[battlefield_role].keys())
            top_len = len(max(units, key=len))
            for index, [keys, value] in enumerate(init.units_dict[battlefield_role].items()):
                print("B" + str(index + 1) + ". " + keys.ljust(top_len) +
                      "\t({}pts)".format(value.pts))
        else:
            # print available models and their points with the points value
            # left adjusted so they are in the same column
            print("Available Models (Including base Wargear):")
            units = list(init.units_dict[battlefield_role].keys())
            top_len = len(max(units, key=len))
            for index, [keys, value] in enumerate(init.units_dict[battlefield_role].items()):
                print(str(index + 1) + ". " + keys.ljust(top_len) +
                      "\t({}pts for {} models)".format(value.pts * value.size[0], value.size[0]))

        user_input = input(">> ")
        try:
            if user_input.lower() in {'q', 'exit', 'cancel', 'quit', 'return'}:
                return False
            elif re.match('([aAbB][1-9][0-9]*)|([1-9][0-9]*)', user_input):
                if battlefield_role == "HQ":
                    if user_input[0] in {'A', 'a'}:
                        user_input = list(init.units_dict["Named Characters"].keys())[
                            int(user_input[1:]) - 1]
                    elif user_input[0] in {'B', 'b'}:
                        user_input = list(init.units_dict["HQ"].keys())[int(user_input[1:]) - 1]
                elif user_input[0].isdigit():
                    user_input = list(init.units_dict[battlefield_role].keys())[int(user_input) - 1]

            return squad.Unit(user_input, battlefield_role)
        except (KeyError, IndexError):
            print("{} is not a valid option, please select the unit by name or input".format(user_input))
            print("To quit please enter 'q'")
            unit = self._create_user_unit(battlefield_role)
            return unit

    def _get_user_battlefield_role(self):
        """Gets the user-chosen battlefield_role"""
        roles = ["HQ", "Troops", "Elites", "Fast Attack", "Heavy Support"]
        print("Which Battlefield Role would you like to add?")
        for index, role in enumerate(roles):
            print(str(index + 1) + '. ' + role)
        battlefield_role = input(">> ")
        battlefield_role = battlefield_role.replace(' ', '')

        if battlefield_role.isdigit():
            try:
                if int(battlefield_role) <= 0:
                    raise IndexError("Not valid index for battlefield role")
                battlefield_role = roles[int(battlefield_role) - 1]
            except IndexError:
                print("{} is invalid, please enter the index or name of the battlefield role you wish to add".format(
                    battlefield_role))
                battlefield_role = self._get_user_battlefield_role()
        # sanitise inputs
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
            print("{} is invalid, please enter the index or name of the battlefield role you wish to add".format(
                battlefield_role))
            battlefield_role = self._get_user_battlefield_role()

        return battlefield_role

    def _add_unit(self, detach, unit):
        detach.add_unit(unit)


if __name__ == "__main__":
    interface = UI()
    user_input = ''
    commands = {"add unit": interface.add_unit,
                "add detachment": interface.add_detachment,
                "print army": interface.print_army,
                "change wargear": interface.change_unit_wargear}

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
            if user_command not in {'quit', 'exit'}:
                print("{} command not found, try:".format(user_command))
                for i in commands:
                    print('\t' + i)
        except TypeError as e:
            if "positional argument" in str(e):
                print(e)
            else:
                raise e
