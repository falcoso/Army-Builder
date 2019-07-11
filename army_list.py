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
import init
import squad


class ArmyList:
    """
    Overarching class to collect together all the detachments and keep track
    of the army's factions and properties.

    Parameters
    ----------
    faction : str
        The faction of the Army list being made

    Public Attributes
    -----------------
    detachments : list (Detachment)
        List of all the detachments in the army.
    detachment_names: list (str)
        List of names of each of the detachments for quick reference.
    cp : int
        Total number of command points in the army.
    faction : str
        The faction of the Army list being made

    Public Methods
    --------------
    add_detachment(self, detach): Adds a detachment to the army list.

    del_detachment(self, name): Deletes the detachment with the supplied name.
    """

    def __init__(self, faction):
        self.faction = faction
        self.detachments = []
        self.cp = 0

        # define list of names to make searching and labelling easier
        self.detachment_names = []
        return

    @property
    def pts(self): return np.sum([i.pts for i in self.detachments], dtype=int)

    def add_detachment(self, detach):
        """Adds a detachment to the army list"""
        if not isinstance(detach, Detachment):
            raise ValueError("Invalid unit input")

        detach.parent = self
        self.detachments.append(detach)
        self.detachment_names.append(detach.name)
        self.cp += self.detachments[-1].cp

        # number repeated detachment types
        counter = 0
        for i in range(len(self.detachments)):
            detachment = self.detachments[i]
            if detachment.type == detach.type:
                counter += 1
                if detachment.name in self.detachment_names[i]:
                    detachment.name = detachment.type + ' ' + str(counter)
                    self.detachment_names[i] = detachment.name
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
        self.__re_calc_cp()
        return

    def __re_calc_cp(self):
        self.cp = 0
        for i in self.detachments:
            self.cp += i.cp

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
    parent: ArmyList
        ArmyList to which the detachment belongs.
    detachment_type : str
        Type of detachment to be created.


    Public Attributes
    -----------------
    parent : Unit
        Unit to which the model belongs.
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
    add_unit(self, unit): Adds the given unit to the detachment.

    del_unit(self, unit): Deletes the given unit from the detachment.
    """

    def __init__(self, detachment_type):
        self.type = detachment_type
        self.__parent = None
        self.__name = self.type
        self.__default_name = True
        self.__units_dict = {"HQ": [],
                             "Troops": [],
                             "Elites": [],
                             "Fast Attack": [],
                             "Heavy Support": []}
        # will raise an error if the detachment doesn't exist:
        init.detachments_dict[self.type]
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
    def parent(self, parent): self.__parent = parent

    @property
    def treeid(self): return self.__treeid

    @treeid.setter
    def treeid(self, id): self.__treeid = id

    @property
    def name(self): return self.__name

    @property
    def pts(self): return np.sum([np.sum([i.pts for i in unit]) for key, unit in self.units_dict.items()], dtype=int)

    @name.setter
    def name(self, new_name):
        """Changes the name of the detachment to the given new_name string."""
        self.__name = new_name
        self.__default_name = False

    def __repr__(self):
        output = "***" + self.name + "\t\t" + "Total:{}pts".format(self.pts) + "***\n"
        for key, value in self.units_dict.items():
            if len(value) != 0:
                output += "*" + key + "*\n"
                for i in value:
                    output += i.__repr__() + "\n"
                output += "\n"

        return output

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
