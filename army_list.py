"""
Implements the top level collections of units for the army builder.

Classes:
--------
ArmyList:
    Overarching class to collect together all the detachments and keep track
    of the army's factions and properties.
Detachment:
    Collects together all the units within a detachment, making sure that
    minimum requirements are met and keeping track of points.
"""

import numpy as np
import json

import init
import squad


class ArmyList:
    """
    Overarching class to collect together all the detachments and keep track
    of the army's factions and properties.

    Parameters
    ----------
    faction : str
        The faction of the Army list being made.
    load : bool (default=False)
        If true the faction parameter is a filepath to a json from which the
        army is to be loaded.

    Public Attributes
    -----------------
    detachments : list (Detachment)
        List of all the detachments in the army.
    detachment_names: list (str)
        List of names of each of the detachments for quick reference.
    cp : int
        Total number of command points in the army.
    pts : int
        Total points in the army.
    faction : str
        The faction of the Army list being made.

    Public Methods
    --------------
    save(self, file_path): Saves the army as a json to the given file_path.

    load(self, file_path): Loads the army from the specified filepath.

    add_detachment(self, detach): Adds a detachment to the army list.

    del_detachment(self, name): Deletes the detachment with the supplied name.
    """

    def __init__(self, faction, load=False):
        if load:
            self.load(faction)
        else:
            self.faction = faction
            self.detachments = []
        return

    @property
    def cp(self): return np.sum([i.cp for i in self.detachments], dtype=int)

    @property
    def pts(self): return np.sum([i.pts for i in self.detachments], dtype=int)

    @property
    def detachment_names(self): return [i.name for i in self.detachments]

    def save(self, file_path):
        """Saves the army as a json to the given file_path."""
        save = {}
        save["faction"] = self.faction
        save["detachments"] = [i.save() for i in self.detachments]
        with open(file_path, 'w') as fp:
            json.dump(save, fp, indent=4)
        return save

    def load(self, file_path):
        """Loads the army from the specified filepath."""
        with open(file_path, 'r') as file:
            army = json.load(file)

        self.faction = army["faction"]
        self.detachments = [Detachment(i) for i in army["detachments"]]
        for i in self.detachments:
            i.parent = self
        return

    def add_detachment(self, detach):
        """Adds a detachment to the army list"""
        self.detachments.append(detach)
        detach.parent = self
        return

    def del_detachment(self, name):
        """Deletes the detachment with the supplied name"""
        if name not in self.detachment_names:
            raise ValueError("Detachment name {} doesn't exist.".format(name))

        for detach in self.detachment_names:
            if detach == name:
                self.detachments.pop(self.detachment_names.index(detach))
                self.detachment_names.remove(detach)
                break
        return

    def __repr__(self):
        ret = self.faction + '\n'
        for i in self.detachments:
            ret += i.__repr__()
        return ret

    def print_army(self):
        print(self)
        return


class Detachment:
    """
    Collects together all the units within a detachment, making sure that
    minimum requirements are met and keeping track of points.

    Parameters
    ----------
    detachment_type : str/ dict
        Type of detachment to be created, or dictionary from which to generate
        a pre-made army.

    Public Attributes
    -----------------
    parent : ArmyList
        Army to which the detachment belongs.
    treeid : wx.TreeItemID
        ID for wx.TreeCtrl in GUI
    foc : dict
        Force organisation chart for the detachment.
    cp : int
        Command points of the detachment.
    type : str
        Type of detachment.
    name : str
        Name of the detachment.
    default_name : bool
        True if the name has not been changed by the user.
    units_dict : dict
        Dictionary split up intol battlefield roles containing lists of
        squad.Unit.
    pts: int
        Total points for the detachment.

    Public Methods
    --------------
    save(self): Creates a dictionary to save the current detachment.

    load(self): Loads the detachment from a pre-made dictionary.

    add_unit(self, unit): Adds the given unit to the detachment.

    del_unit(self, unit): Deletes the given unit from the detachment.
    """

    def __init__(self, detachment_type):
        self.treeid = None
        self.__parent = None
        self.__default_name = True
        self.__units_dict = {"HQ": [],
                             "Troops": [],
                             "Elites": [],
                             "Fast Attack": [],
                             "Heavy Support": [],
                             "Dedicated Transports": []}
        if type(detachment_type) == dict:
            self.load(detachment_type)
        elif type(detachment_type) == str:
            self.type = detachment_type
            self.__name = self.type
            # will raise an error if the detachment doesn't exist:
            init.detachments_dict[self.type]
        else:
            raise TypeError("detachment type must be a dict or string got {}".format(
                type(detachment_type)))
        return

    @property
    def foc(self): return init.detachments_dict[self.type]["foc"]

    @property
    def cp(self): return init.detachments_dict[self.type]["cp"]

    @property
    def units_dict(self): return self.__units_dict

    @property
    def parent(self): return self.__parent

    @parent.setter
    def parent(self, parent):
        self.__parent = parent

        # number name if same detachment already exists
        if self.__default_name:
            counter = 0
            for i in self.parent.detachment_names:
                if self.type in i:
                    counter += 1
            self.__name = self.type + ' ' + str(counter)

    @property
    def name(self): return self.__name

    @name.setter
    def name(self, new_name):
        """Changes the name of the detachment to the given new_name string."""
        self.__name = new_name
        self.__default_name = False

    @property
    def pts(self): return np.sum([np.sum([i.pts for i in unit])
                                  for key, unit in self.units_dict.items()],
                                 dtype=int)

    def __repr__(self):
        output = "***" + self.name + "\t\t" + "Total:{}pts".format(self.pts) + "***\n"
        for key, value in self.units_dict.items():
            if len(value) != 0:
                output += "*" + key + "*\n"
                for i in value:
                    output += i.__repr__() + "\n"
                output += "\n"

        return output

    def save(self):
        """Creates a dictionary to save the current detachment."""
        save = {}
        # name can be saved in the upper level
        save["type"] = self.type
        if self.__default_name:
            save["name"] = None
        else:
            save["name"] = self.name
        unit_saves = {}
        for foc_role, unit_list in self.__units_dict.items():
            unit_saves[foc_role] = [i.save() for i in unit_list]
        save["units"] = unit_saves
        return save

    def load(self, loaded_dict):
        """
        Loads the detachment from a pre-made dictionary.

        Parameters
        ----------
        loaded_dict: dict
            {"type": str, "name": str, "units_dict":{"HQ": [unit_saves...]...}}
            dictionary of the base data required to re-construct the detachment.
        """
        self.type = loaded_dict["type"]
        if loaded_dict["name"] is None:
            self.__name = self.type
        else:
            self.__name = loaded_dict["name"]
            self.__default_name = False

        for foc_role, unit_list in self.__units_dict.items():
            self.__units_dict[foc_role] = [squad.Unit(i, foc_role)
                                           for i in loaded_dict["units"][foc_role]]
            for unit in self.__units_dict[foc_role]:
                unit.parent = self
        return

    def add_unit(self, unit):
        """Adds the given unit to the detachment."""
        if not isinstance(unit, squad.Unit):
            raise ValueError("Invalid unit input")
        unit.parent = self
        self.__units_dict[unit.battlefield_role].append(unit)
        return

    def del_unit(self, unit):
        """Deletes the given unit from the detachment."""
        self.__units_dict[unit.battlefield_role].remove(unit)
        return

    def __eq__(self, other):
        if type(other) != Detachment:
            return False

        if self.name == other.name and self.type == other.type and self.units_dict == other.units_dict:
            return True

        else:
            return False
