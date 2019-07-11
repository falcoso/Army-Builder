"""
Implements the Unit level objects for the army builder.

Classes
-------
Unit(init.UnitTypes):
    Keeps track of the attributes of an individual unit in an army list.

Model(Unit):
    Used to keep track of the attributes of individual groups of models within
    the same unit.
"""

import copy
import numpy as np

import init
import option_parser
from collections import Counter


class Unit(init.UnitTypes):
    """
    Keeps track of the attributes of an individual unit in an army list.

    Parameters
    ----------
    unit_type : str
        Name of the unit template to be created.
    battlefield_role : str
        Battlefield role of the unit that is being created.

    Public Attributes
    -----------------
    parent : army_list.Detachment
        Detachment to which the unit belongs.
    treeid : wx.TreeItemID
        ID for wx.TreeCtrl in GUI
    type : str
        Name of unit template.
    name : str
        Name of the unit.
    default_name : bool
        True if the unit name has not been changed by the user.
    battlefield_role : str
        Battlefield role of the unit that is being created.
    size_range: tuple (int)
        The upper and lower limits to the number of models in the unit.
    size : int
        Total number of models in the unit.
    options : list (str)
        List of strings that contains each option available to the unit.
    mod_str : list (str)
        List of strings naming the model types that can be in the unit. If
        mod_str is None then there is only one type of model in the unit.
    wargear : list (init.WargearItem)
        List of base wargear that every model in the unit has.
    models : list (Model)
        List of models that are in the unit.
    parser : option_parser.OptionParser
        Parser for all the options available to the unit.
    pts : int
        Total points for the group of models.

    Public Methods
    --------------
    reset(self): Returns the unit back to its initialised state.

    re_size(self, *args):
        Re-sizes the unit. An int must be provided for every possible type of
        model.

    change_wargear(self, wargear_to_add):
        Changes the wargear options for the unit. wargear_to_add is a list of
        option_parser.Option with an init.WargearItem selected for each item.
    """

    def __init__(self, unit_type, battlefield_role):
        self.__parent = None
        self.__treeid = None
        self.__type = unit_type
        self.__name = self.type
        self.__default_name = True
        self.__battlefield_role = battlefield_role

        self.__wargear = copy.deepcopy(self.base_unit.wargear)
        self.__models = []
        self.parser = option_parser.OptionParser(current_wargear=self.wargear)
        self.parser.build()
        if self.mod_str is None:
            self.__models = [Model(self, no_models=self.size_range[0],
                                   base_pts=self.base_unit.base_pts)]
            self.base_unit.models = [self.type]  # might break here from getter
        else:
            # get first model without size-limits
            for model in self.mod_str:
                if init.models_dict[model]["no_per_unit"] is None:
                    self.__models.append(Model(self, model, self.size_range[0]))
                    break

        # check that the unit can be found in the base dictionary
        self.base_unit
        return

    @property
    def parent(self): return self.__parent

    @parent.setter
    def parent(self, parent):
        """Sets the parent army of the detachment."""
        self.__parent = parent
        return

    @property
    def treeid(self): return self.__treeid

    @treeid.setter
    def treeid(self, id):
        """Sets the treeid from the GUI for this detachment."""
        self.__treeid = id
        return

    @property
    def battlefield_role(self): return self.__battlefield_role

    @property
    def type(self): return self.__type

    @property
    def name(self): return self.__name

    @property
    def wargear(self): return self.__wargear

    @property
    def size_range(self): return self.base_unit.size

    @property
    def options(self): return self.base_unit.options

    @property
    def mod_str(self): return self.base_unit.models

    @property
    def models(self): return self.__models

    @property
    def size(self): return np.sum([i.size for i in self.models])

    @name.setter
    def name(self, new_name):
        """
        Changes the name of the detachment to the given new_name string.
        """
        self.__name = new_name
        self.__default_name = False

    @property
    def base_unit(self):
        # catch any characters being added
        try:
            base_unit = init.units_dict[self.battlefield_role][self.type]
        except KeyError:
            base_unit = init.units_dict["Named Characters"][self.type]
        return base_unit

    @property
    def pts(self):
        """Updates any points values after changes to the unit"""
        pts = 0
        for i in self.models:
            pts += i.pts

        if self.wargear is not None:
            wargear_pts = 0
            for i in self.wargear:
                wargear_pts += i.points

            pts += wargear_pts * self.size
        return pts

    def reset(self):
        """
        Returns the unit back to its initialised state. This may be useful if
        there are a lot of changes that need to be undone at once.
        """
        self.__init__(self.type, self.battlefield_role)
        return

    def get_all_wargear(self):
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
        # check sizes
        size = self.size
        valid = True
        if size < self.size_range[0] or size > self.size_range[1]:
            valid = False
            print("{} has invalid size:\nsize range:{}-{}\tcurrent size:{}".format(self.name,
                                                                                   *self.size_range,
                                                                                   size))
        # count instances of each model
        count_dict = {}
        for i in self.models:
            if i.label in count_dict.keys():
                count_dict[i.label] += i.size
            else:
                count_dict[i.label] = i.size

        print(count_dict)

        # check model has a sufficient number
        for name, no_of in count_dict.items():
            if init.models_dict[name]["no_per_unit"] is not None:
                if init.models_dict[name]["no_per_unit"] < no_of:
                    valid = False
                    print("{} has too many of {}:\nmax allowed:{}\tcurrent amount:{}".format(self.name,
                                                                                             name,
                                                                                             init.models_dict[name]["no_per_unit"],
                                                                                             no_of))
        return valid

    def re_size(self, *args):
        """
        Re-sizes the unit. An int must be provided for every possible type of
        model in the unit.
        """
        # check if the model is already in the list
        if len(args) != len(self.mod_str):
            raise TypeError("Got {} sizes for {} models".format(len(args),
                                                                len(self.mod_str)))
        for model, no_of in zip(self.mod_str, args):
            if init.models_dict[model]["indep"]:
                counter = 0
                for i in self.models:
                    # count how many instances of model and add difference
                    if i.label == model:
                        counter += 1
                if no_of - counter < 0:
                    print("Unable to remove models as each is independant")
                    continue
                else:
                    for i in range(no_of - counter):
                        self.__models.append(Model(self, model))

            else:
                # check to see if model exists already
                flag = True
                for i in self.__models:
                    if i.label == model:
                        i.size = no_of
                        if no_of == 0:
                            self.__models.remove(i)
                        flag = False
                        break
                # otherwise append to models list
                if flag and no_of != 0:
                    self.__models.append(Model(self, model, no_of))
        return

    def change_wargear(self, wargear_to_add):
        """
        Changes the wargear options for the unit. wargear_to_add is a list of
        option_parser.Option with an init.WargearItem selected for each item.
        """
        if not wargear_to_add:  # user selected a quit option
            return
        for new_wargear in wargear_to_add:
            for i in new_wargear.items_involved:
                if i in self.__wargear:
                    self.__wargear.remove(i)

            self.__wargear += new_wargear.selected
        return

    def __repr__(self):
        ret = self.name + '\t({}pts)'.format(self.pts)
        if self.mod_str is None:
            size = self.size
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

    def __eq__(self, other):
        if not isinstance(other, Unit):
            return False

        try:
            if self.name == other.name and set(self.wargear) == set(other.wargear) and self.models == other.models:
                return True
            else:
                return False
        except TypeError:
            if self.wargear is None and other.wargear is None:
                return True
            else:
                return False

        except:
            return False


class Model(Unit):
    """
    Inherits from Unit. Used to keep track of the attributes of individual
    groups of models within the same unit.

    Parameters
    ----------
    label : str
        Type of model to be initialised.
    no_models : int (default=1)
        Number of that type of model.
    base_pts : int
        Points value per model. Only used when a unit has all models of the same
        type.

    Public Attributes
    -----------------
    parent: Unit
        Unit to which the model belongs.
    treeid: wx.TreeItemID
        ID for wx.TreeCtrl in GUI
    size : int
        Number of the type of model.
    label : str
        Type of model.
    name : str
        String that will be displayed in GUI, may be the same as models with
        different labels.
    wargear : list (init.WargearItem)
        List of base wargear that every model in the unit has.
    options : type
        Description of attribute `options`.
    limit : int
        Limit to the number of this type of model allowed in the unit
    parser: option_parser.OptionParser
        Parser for all the options available to the unit.
    pts: int
        Total points for the group of models.
    size: int
        Number of models of this label.
    """

    def __init__(self, parent, label=None, no_models=1, base_pts=None):
        self.__parent = parent
        self.__size = no_models
        self.label = label
        if label is None:
            self.label = parent.type

            # add default model to the models_dict
            init.models_dict[self.label] = {"name": None,
                                            "no_per_unit": None,
                                            "wargear": None,
                                            "options": None,
                                            "indep": False,
                                            "pts": base_pts}

        if self.root_data["wargear"] is not None:
            self.__wargear = list(map(lambda s: init.WargearItem(s), self.root_data["wargear"]))
        else:
            self.__wargear = None

        if self.root_data["name"] is None:
            self.name = self.label
        else:
            self.name = self.root_data["name"]
        if self.options is not None:
            self.parser = option_parser.OptionParser(self.wargear, unit=False)
            self.parser.build()
        print(self.pts)
        return

    @property
    def root_data(self): return init.models_dict[self.label]

    @property
    def options(self): return self.root_data["options"]

    @property
    def wargear(self): return self.__wargear

    @property
    def limit(self): return self.root_data["no_per_unit"]

    @property
    def size(self): return self.__size

    @size.setter
    def size(self, new_size): self.__size = new_size

    @property
    def pts(self):
        """Updates any points values after changes to the unit"""
        wargear_pts = 0
        if self.wargear is not None:
            for i in self.wargear:
                wargear_pts += i.points
        pts_per_model = self.root_data["pts"] + wargear_pts
        pts = pts_per_model * self.size
        return pts

    def __repr__(self, indent=''):
        if self.size == 1:
            ret = self.name
        else:
            ret = '{} {}'.format(self.size, self.name)
            if self.name[-1] != 's':
                ret += 's'
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
        except TypeError:
            if self.wargear is None and other.wargear is None:
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
