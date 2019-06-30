import init
import squad


class ArmyList:
    """
    Overarching class to collect together all the detachments and keep track
    of the army's factions and properties
    """

    def __init__(self, faction):
        self.faction = faction
        self.detachments = []
        self.cp = 0

        # define list of names to make searching and labelling easier
        self.detachment_names = []
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

    def add_detachment(self, detach):
        """Adds a detachment to the army list"""
        if not isinstance(detach, Detachment):
            raise ValueError("Invalid unit input")

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
    """

    def __init__(self, detachment_type):
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

        self.re_calc_points()
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

    def re_calc_points(self):
        """Updates any points values after changes to the unit"""
        self.pts = 0
        for key, unit in self.units_dict.items():
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

    def add_unit(self, unit):
        if not isinstance(unit, squad.Unit):
            raise ValueError("Invalid unit input")

        self.units_dict[unit.battlefield_role].append(unit)
        self.re_calc_points()
        return
