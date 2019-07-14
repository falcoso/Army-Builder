"""
Initialisation classes and functions to start the army builder. Loads up the
data files for the given faction.

Functions:
----------
init(faction):
    Initialises the global variables for the chosen faction:
    detachments_dict - dict containing the data in Detachments.json
    armoury_dict - dict containing the data in <faction>/Armoury.json
    units_dict - dict of UnitTypes containing the data in <faction>/Units.json

Classes
-------
WargearItem: Collection of Wargear items for assignment to a unit.

MultipleItem(WargearItem):
    Created for when several independant items are grouped together within an
    option i.e. Stormshield and Thunderhammer.
"""

import json
import numpy as np


def init(faction):
    """
    Initialises the global variables for the chosen faction:
    detachments_dict - dict containing the data in Detachments.json
    armoury_dict - dict containing the data in <faction>/Armoury.json
    units_dict - dict of UnitTypes containing the data in <faction>/Units.json
    """
    # Open list of possible detachments and generate object for each one
    global detachments_dict
    with open('./resources/Detachments.json', 'r') as file:
        detachments_dict = json.load(file)

    # determine faction of armylist and open units and wargear data
    global armoury_dict
    with open("./resources/{}/Armoury.json".format(faction), 'r') as file:
        armoury_dict = json.load(file)

    global models_dict
    with open("./resources/{}/Models.json".format(faction), 'r') as file:
        models_dict = json.load(file)

    global units_dict
    units_dict = {}
    with open("./resources/{}/Units.json".format(faction), 'r') as file:
        units_dict = json.load(file)
    for key in units_dict.keys():
        for index, rows in units_dict[key].items():
            # generate the default unit pts value
            pts = 0
            if rows["wargear"] is not None:
                pts += np.sum([MultipleItem(i).pts if '+' in i else WargearItem(i)
                               .pts for i in rows["wargear"]])*rows["size"][0]
            if rows["models"] is not None:
                for model in rows["models"]:
                    if models_dict[model]["no_per_unit"] is None:
                        break
                if models_dict[model]["wargear"] is not None:
                    pts += np.sum([MultipleItem(i).pts if '+' in i else WargearItem(i).pts
                                   for i in models_dict[model]["wargear"]])*rows["size"][0]

            units_dict[key][index]["pts"] = pts

    return detachments_dict, armoury_dict, units_dict


class WargearItem:
    """
    Collection of Wargear items for assignment to a unit.

    Parameters
    ----------
    item : str
        Name of the Wargear to be initialised.

    Public Attributes
    -----------------
    item : str
        Name of the Wargear
    no_of : int
        Number of the Wargear in the collection.
    pts : int
        Points value of the collection of wargear.

    Public Methods
    --------------
    set_no_of(self, no_of): Set no_of and updates pts value.

    wargear_search(self, item):
        Searches for a given wargear item in the armoury dictionary
    """

    def __init__(self, item):
        self.item = item
        self.no_of = 1
        if '*' in item:
            self.no_of = int(item.split('*')[0])
            self.item = item.split('*')[1]
        self.pts = self.no_of * self.wargear_search(self.item)
        # get the wargear type
        for key, obj in armoury_dict.items():
            if item in obj:
                self.type = key
        return

    def save(self):
        """Generates a string to be stored in a file for saving."""
        save = ''
        if self.no_of != 1:
            save += str(self.no_of) + '*'
        save += self.item
        return save

    def set_no_of(self, no_of):
        """Set no_of and updates points value."""
        self.no_of = no_of
        self.pts = self.no_of * self.wargear_search(self.item)
        return

    def wargear_search(self, item):
        """Searches for a given wargear item in the armoury dictionary."""
        for key, obj in armoury_dict.items():
            if item in obj:
                return obj[item]
        raise KeyError("{} not found in Armoury.json file".format(item))
        return

    def __repr__(self, comparison=None, tidy=False):
        if self.no_of == 1:
            ret = self.item
        else:
            ret = str(self.no_of) + ' ' + self.item + 's'

        if tidy:
            ret = ret.ljust(28)
        if comparison:
            ret += " (net {}pts per model)".format(self.pts - comparison.pts)
        elif self.pts != 0:
            ret += " ({}pts)".format(self.pts)
        return ret

    def __mul__(self, integer):
        self.pts = self.pts * integer
        self.no_of = self.no_of * integer
        return self

    def __add__(self, other_item):
        if type(other_item) == MultipleItem:
            other_item.item.append(self.item)
            other_item.pts += self.pts
            return other_item

        elif type(other_item) == WargearItem:
            ret = MultipleItem(self, other_item)
            return ret

        else:
            raise TypeError(
                "Addition between init.WargearItem and {} not defined".format(type(other_item)))

    def __eq__(self, other):
        try:
            if self.item != other.item or self.no_of != self.no_of or self.pts != self.pts:
                return False
            return True
        except:
            return False

    def __hash__(self):
        return hash((tuple(self.item), self.no_of, self.pts))


class MultipleItem(WargearItem):
    """
    Inherited class from WargearItem. Created for when several independant items
    are grouped together within an option i.e. Stormshield and Thunderhammer.

    Parameters
    ----------
    *args :
        Arguments for WargearItem.

    Attributes
    ----------
    item : str
        Name of the Wargear
    no_of : int
        Number of the Wargear in the collection.
    pts : int
        Points value of the collection of wargear.

    """

    def __init__(self, *args):
        # check all items exist
        if type(args[0]) == str:
            args = [WargearItem(i) for i in args]
        self.item = list(map(lambda s: s.item, args))

        # set type in given priority order
        types = [i.type for i in args]
        if "Melee" in types:
            self.type = "Melee"
        elif "Range" in types:
            self.type = "Range"
        else:
            self.type = "Other Wargear"

        # set points
        self.pts = 0
        self.no_of = 1
        for i in args:
            print(i.pts)
            self.pts += i.pts
        return

    def save(self):
        """Generates a string to be stored in a file for saving."""
        return '+'.join(self.item)

    def __mul__(self, other):
        print(self)
        print(other)
        raise TypeError("Multiplication of MultiplItem types not yet defined")
        return

    def __add__(self, other_item):
        if type(other_item) == MultipleItem:
            self.item += other_item.item
        else:
            self.item.append(other_item.item)
        self.pts += other_item.pts
        return self

    def __repr__(self, comparison=None, tidy=False):
        ret = ''
        for i in range(len(self.item)):
            ret += self.item[i]
            if i == len(self.item) - 1:
                pass
            elif i == len(self.item) - 2:
                ret += ' & '
            else:
                ret += ', '

        if tidy:
            ret = ret.ljust(28)
        if comparison:
            ret += " \t(net {}pts per model)".format(self.pts - comparison.pts)
        else:
            ret += " ({}pts)".format(self.pts)
        return ret
