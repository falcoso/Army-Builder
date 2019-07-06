"""
Initialisation classes and functions to start the army builder. Loads up the
data files for the given faction.

Functions:
----------
wargear_search_base(item):
    Searches for a given wargear item in the armoury dictionary

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

UnitTypes:
    Template class to group together the information in the <faction>/Units.json
    for easy access in other modules
"""

import json


def wargear_search_base(item):
    """
    Searches for a given wargear item in the armoury dictionary
    """
    for key, obj in armoury_dict.items():
        if item in obj:
            return obj[item]
    raise KeyError("{} not found in Armoury.json file".format(item))
    return

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

    global units_dict
    units_dict = {}
    with open("./resources/{}/Units.json".format(faction), 'r') as file:
        units = json.load(file)
    for key in units.keys():
        units_dict[key] = {}
        for index, rows in units[key].items():
            units_dict[key][index] = UnitTypes(rows)

    global models_dict
    with open("./resources/{}/Models.json".format(faction), 'r') as file:
        models_dict = json.load(file)

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
    points : int
        Points value of the collection of wargear.

    Public Methods
    --------------
    set_no_of(self, no_of): Set no_of and updates points value.

    wargear_search(self, item):
        Searches for a given wargear item in the armoury dictionary
    """
    def __init__(self, item):
        self.item = item
        self.no_of = 1
        if '*' in item:
            self.no_of = int(item.split('*')[0])
            self.item = item.split('*')[1]
        self.points = self.no_of * self.wargear_search(self.item)
        return

    def set_no_of(self, no_of):
        """Set no_of and updates points value."""
        self.no_of = no_of
        self.points = self.no_of * self.wargear_search(self.item)
        return

    def wargear_search(self, item):
        return wargear_search_base(item)

    def __repr__(self, comparison=None, tidy=False):
        if self.no_of == 1:
            ret = self.item
        else:
            ret = str(self.no_of) + ' ' + self.item + 's'

        if tidy:
            ret = ret.ljust(28)
        if comparison:
            ret += " (net {}pts per model)".format(self.points - comparison.points)
        elif self.points != 0:
            ret += " ({}pts)".format(self.points)
        return ret

    def __mul__(self, integer):
        self.points = self.points * integer
        self.no_of = self.no_of * integer
        return self

    def __add__(self, other_item):
        if type(other_item) == MultipleItem:
            other_item.item.append(self.item)
            other_item.points += self.points
            return other_item

        elif type(other_item) == WargearItem:
            ret = MultipleItem(self, other_item)
            return ret

        else:
            raise TypeError(
                "Addition between init.WargearItem and {} not defined".format(type(other_item)))

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
    points : int
        Points value of the collection of wargear.

    """
    def __init__(self, *args):
        if type(args[0]) == str:
            args = (WargearItem(i) for i in args)
        self.item = list(map(lambda s: s.item, args))
        self.points = 0
        self.no_of = 1
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
            ret += " \t(net {}pts per model)".format(self.points - comparison.points)
        else:
            ret += " ({}pts)".format(self.points)
        return ret


class UnitTypes:
    """
    Template class to group together the information in the <faction>/Units.json
    for easy access in other modules

    Parameters
    ----------
    root_data : dict
        Dictionary generated from the <faction>/Units.json

    Attributes
    ----------
    name : str
        Default name of the unit.
    base_pts : int
        The points per model without wargear
    pts : int
        The default points for the unit
    options : list (str)
        List of all the option strings for the unit.
    models : list (str)
        List of all the possible models in the unit.
    limits : dict
        Dictionary of {Model: int} that gives the max number of a given model
        allowed in the unit. Does not exist if there are no limits.
    size : tuple (int)
        The min and max size of the unit.
    wargear : list (WargearItem)
        The default wargear the unit has.
    """
    def __init__(self, root_data):
        self.name = root_data["name"]
        try:
            self.base_pts = root_data["base_pts"]
        except:
            raise ValueError("Unable to load base_pts from {} for {}".format(root_data[1], self.name))
        self.pts = self.base_pts
        self.options = root_data["options"]
        self.models = root_data["models"]
        try:
            self.limits = root_data["limits"]
        except KeyError:
            pass

        # if range of unit size, save as array, otherwise single number
        self.size = root_data["size"]

        if root_data["wargear"] is not None:
            wargear_temp = root_data["wargear"]
            self.wargear = []
            for i in wargear_temp:
                try:
                    self.wargear.append(WargearItem(i))
                except KeyError:
                    try:
                        self.wargear.append(MultipleItem(*i.split('/')))
                    except:
                        raise KeyError(
                            "{} for {} not found in Armoury.json file".format(i, self.name))
        else:
            self.wargear = None
        # find default wargear costs
        self.wargear_pts = 0
        if self.wargear is None:
            return
        else:
            for i in self.wargear:
                if type(i) == MultipleItem:
                    self.wargear_pts += i.wargear_search(i.item[0])
                else:
                    self.wargear_pts += i.points

        self.pts += self.wargear_pts
        return

    def wargear_search(self, item):
        try:
            return wargear_search_base(item)
        except KeyError:
            raise KeyError("{} for {} not found in Armoury.json file".format(item, self.name))
        return

    def __repr__(self):
        output = self.name + "\t" + str(self.pts) + "pts per model\t"
        if self.wargear is not None:
            for i in self.wargear:
                output += i.__repr__() + ", "
        return output
