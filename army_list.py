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

    get_pts(self): Calculates the total points of the army.
    """

    def __init__(self, faction):
        self.faction = faction
        self.detachments = []
        self.cp = 0

        # define list of names to make searching and labelling easier
        self.detachment_names = []
        return

    def get_pts(self):
        """Calculates the total points of the army"""
        pts = 0
        for i in self.detachments:
            pts += i.get_pts()
        return pts

    def add_detachment(self, detach):
        """Adds a detachment to the army list"""
        if not isinstance(detach, Detachment):
            raise ValueError("Invalid unit input")

        detach.set_parent(self)
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

    Public Methods
    --------------
    rename(self, new_name):
        Changes the name of the detachment to the given new_name string.

    add_unit(self, unit): Adds the given unit to the detachment.

    get_pts(self): Calculates the total points of the detachment.
    """

    def __init__(self, detachment_type):
        self.parent = None
        self.foc = init.detachments_dict[detachment_type]["foc"]
        self.cp = init.detachments_dict[detachment_type]["cp"]
        self.type = detachment_type
        self.name = self.type
        self.default_name = True
        self.units_dict = {"HQ": [],
                           "Troops": [],
                           "Elites": [],
                           "Fast Attack": [],
                           "Heavy Support": []}

        self.__re_calc_points()
        return

    def __repr__(self):
        output = "***" + self.name + "\t\t" + "Total:{}pts".format(self.pts) + "***\n"
        for key, value in self.units_dict.items():
            if len(value) != 0:
                output += "*" + key + "*\n"
                for i in value:
                    output += i.__repr__() + "\n"
                output += "\n"

        return output

    def __re_calc_points(self):
        """Updates any points values after changes to the unit"""
        self.pts = 0
        for key, unit in self.units_dict.items():
            for i in unit:
                self.pts += i.pts
        return

    def set_parent(self, parent):
        """Sets the parent detachment of the unit."""
        self.parent = parent
        return

    def get_pts(self):
        """Calculates the total points of the army"""
        self.__re_calc_points()
        return self.pts

    def rename(self, new_name):
        """
        Changes the name of the detachment to the given new_name string.
        """
        self.name = new_name
        self.default_name = False

    def add_unit(self, unit):
        """Adds the given unit to the detachment."""
        if not isinstance(unit, squad.Unit):
            raise ValueError("Invalid unit input")

        unit.set_parent(self)
        self.units_dict[unit.battlefield_role].append(unit)
        self.__re_calc_points()
        return
