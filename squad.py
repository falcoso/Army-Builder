"""
Implements the Unit level objects for the army builder.

Classes
-------
BoardObj:
    Template class for creating wargaming objects. Not to be used directly.
    root_data and size need to be set in the subclasses for the methods to work.

Unit(BoardObj):
    Keeps track of the attributes of an individual unit in an army list.

Model(BoardObj):
    Used to keep track of the attributes of individual groups of models within
    the same unit.
"""

import copy
import numpy as np

import init
import option_parser
from collections import Counter


class BoardObj:
    """
    Template class for creating wargaming objects. Not to be used directly.
    root_data and size need to be set in the subclasses for the methods to work.

    Parameters
    ----------
    type : str
        Reference to the type of BoardObj being created to search in resource
        data.

    Public Attributes
    -----------------
    parent : ?
        Parent to which the BoardObj belongs
    treeid : wx.TreeItemID
        ID for wx.TreeCtrl in GUI
    type : str
        Reference to the type of BoardObj being created to search in resource
        data.
    name : str
        Name of the BoardObj for displaying.
    size : int
        Total number of models in the BoardObj.
    options : list (str)
        List of strings that contains each option available to the unit.
    wargear : list (init.WargearItem)
        List of wargear in the BoardObj.
    pts : int
        Total points for the BoardObj.

    Public Methods
    --------------
    change_wargear(self, wargear_to_add):
        Changes the wargear options for the BoardObj.

    save(self): Creates a dictionary of the BoardObj's data.

    load(self, loaded_dict): Loads the unit from a pre-made dictionary.
    """

    def __init__(self, type):
        self.parent = None
        self.treeid = None
        self.__name = None
        self.__parsed = False
        if isinstance(type, dict): #data is being loaded
            self.__type = type["type"]
            source = type["wargear"]
        else:
            self.__type = type
            source = self.root_data["wargear"]

        if source is not None:
            self.__wargear = list(map(lambda x: init.MultipleItem(x.split('+'))
                                      if '+' in x else init.WargearItem(x),
                                      source))
        else:
            self.__wargear = None
        return

    @property
    def type(self): return self.__type

    @property
    def name(self): return self.__name

    @property
    def wargear(self): return self.__wargear

    @property
    def options(self):
        if self.root_data["options"] is None:
            return None
        elif not self.__parsed and self.root_data["options"]:
            self.__parsed = True
            self.__options = option_parser.main_parser.parse2(self.root_data["options"])
        return self.__options

    @property
    def pts(self):
        pts = 0
        if self.wargear is not None:
            wargear_pts = np.sum([i.pts for i in self.wargear])
            pts = wargear_pts * self.size
        return pts

    def change_wargear(self, wargear_to_add):
        """
        Changes the wargear options for the BoardObj.

        Parameters
        ----------
        *wargear_to_add : option_parser.Option/ init.WargearItem
            Option will add the items selected in the option to the current
            wargear. WargearItem will replace the current wargear with all the
            items provided.
        """
        if isinstance(wargear_to_add[0], option_parser.Option):
            for new_wargear in wargear_to_add:
                for i in new_wargear.items_involved:
                    if i in self.__wargear:
                        self.__wargear.remove(i)

                self.__wargear += new_wargear.selected
        elif type(wargear_to_add[0]) in {init.WargearItem, init.MultipleItem}:
            self.__wargear = wargear_to_add
        else:
            raise TypeError("wargear_to_add must be an Option or WargearItem")
        return

    def save(self):
        """Creates a dictionary of the unit's data."""
        save = {}
        save["type"] = self.type
        save["size"] = int(self.size)
        if self.wargear is not None:
            save["wargear"] = [i.save() for i in self.wargear]
        else:
            save["wargear"] = None

        return save

    # def load(self, loaded_dict):
    #     """
    #     Loads the unit from a pre-made dictionary.
    #
    #     Parameters
    #     ----------
    #     loaded_dict: dict
    #         {"type": str, "name": str, "size": int, "wargear":[str, ...]}
    #         dictionary of the base data required to re-construct the detachment.
    #     """
    #     self.__type = loaded_dict["type"]
    #     if loaded_dict["wargear"] is None:
    #         self.__wargear = None
    #     else:
    #         self.__wargear = list(map(lambda x: init.MultipleItem(x.split('+')) if '+' in x else init.WargearItem(x),
    #                                   loaded_dict["wargear"]))

    def __eq__(self, other):
        try:
            if self.name == other.name and set(self.wargear) == set(other.wargear):
                return True
            else:
                return False
        except TypeError:  # set(None) will throw a TypeError
            if self.wargear is None and other.wargear is None \
                    and self.name == other.name:
                return True
            else:
                return False
        except:
            return False


class Unit(BoardObj):
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

    get_all_wargear(self):
        Returns a set containing all the wargear present across all models in
        the unit.

    check_validity(self):
        Checks that the unit is legal by looking at the size of the unit and
        the number of each type of model

    save(self): Creates a dictionary of the unit's data.

    load(self, loaded_dict): Loads the unit from a pre-made dictionary.
    """

    def __init__(self, unit_type, battlefield_role):
        self.__default_name = True
        self.__battlefield_role = battlefield_role
        super().__init__(unit_type)
        self.__models = []
        self._BoardObj__name = self.type

        self.parser = option_parser.OptionParser(current_wargear=self.wargear)
        self.parser.build()
        if self.mod_str is None:
            self.__models = [Model(self, no_models=self.size_range[0],
                                   base_pts=self.root_data["base_pts"])]
        else:
            # get first model without size-limits
            for model in self.mod_str:
                if init.models_dict[model]["no_per_unit"] is None:
                    self.__models.append(Model(self, model, self.size_range[0]))
                    break

        # check that the unit can be found in the base dictionary
        self.root_data
        return

    @property
    def battlefield_role(self): return self.__battlefield_role

    @property
    def size_range(self): return self.root_data["size"]

    @property
    def mod_str(self): return self.root_data["models"]

    @property
    def models(self): return self.__models

    @property
    def size(self): return np.sum([i.size for i in self.models], dtype=int)

    @BoardObj.name.setter
    def name(self, new_name):
        """Changes the name of the detachment to the given new_name string."""
        self._BoardObj__name = new_name
        self.__default_name = False

    @property
    def root_data(self):
        # catch any characters being added
        try:
            root_data = init.units_dict[self.battlefield_role][self.type]
        except KeyError:
            root_data = init.units_dict["Named Characters"][self.type]
        return root_data

    @property
    def pts(self):
        """Updates any points values after changes to the unit"""
        pts = super(Unit, self).pts
        pts += np.sum([i.pts for i in self.models])
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
            if i.type in count_dict.keys():
                count_dict[i.type] += i.size
            else:
                count_dict[i.type] = i.size

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
        # if default model has been made just set that to the value
        if self.mod_str is None:
            self.models[0].size = args[0]
            return

        # validate corrrect number of args otherwise
        elif len(args) != len(self.mod_str):
            raise TypeError("Got {} sizes for {} models".format(len(args),
                                                                len(self.mod_str)))

        # check if the model is already in the list
        for model, no_of in zip(self.mod_str, args):
            if init.models_dict[model]["indep"]:
                counter = 0
                for i in self.models:
                    # count how many instances of model and add difference
                    if i.type == model:
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
                    if i.type == model:
                        i.size = no_of
                        if no_of == 0:
                            self.__models.remove(i)
                        flag = False
                        break
                # otherwise append to models list
                if flag and no_of != 0:
                    self.__models.append(Model(self, model, no_of))
        return

    def save(self):
        """Creates a dictionary of the unit's data."""
        save = super(Unit, self).save()
        if self.mod_str is None:
            model_saves = None
        else:
            model_saves = [i.save() for i in self.models]

        save["models"] = model_saves
        if self.__default_name:
            save["name"] = None
        else:
            save["name"] = self.name
        return save

    def load(self, loaded_dict):
        """Loads the unit from a pre-made dictionary."""
        self.__type = loaded_dict["type"]
        if loaded_dict["wargear"] is None:
            self.__wargear = None
        else:
            self.__wargear = list(map(lambda x: init.MultipleItem(x.split('+')) if '+' in x else init.WargearItem(x),
                                      loaded_dict["wargear"]))

        try:
            # first condition will raise KeyError for models
            if loaded_dict["models"] is not None:
                self.__models = [Model(self, i) for i in loaded_dict["models"]]
            if loaded_dict["name"] is None:
                self.__name = self.type
            else:
                self.__name = loaded_dict["name"]
                self.__default_name = False

        except KeyError:
            pass

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
        try:
            if super().__eq__(other) and self.models == other.models:
                return True
            else:
                return False
        except:
            return False


class Model(BoardObj):
    """
    Inherits from Unit. Used to keep track of the attributes of individual
    groups of models within the same unit.

    Parameters
    ----------
    type : str
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
    type : str
        Type of model.
    name : str
        String that will be displayed in GUI, may be the same as models with
        different types.
    wargear : list (init.WargearItem)
        List of base wargear that every model in the unit has.
    options : list (str)
        List of strings that contains each option available to the unit.
    limit : int
        Limit to the number of this type of model allowed in the unit
    parser: option_parser.OptionParser
        Parser for all the options available to the unit.
    pts: int
        Total points for the group of models.
    size: int
        Number of models of this type.
    """

    def __init__(self, parent, type=None, no_models=1, base_pts=None):
        self.size = no_models
        if type is None:
            # add default model to the models_dict
            init.models_dict[parent.type] = {"name": None,
                                             "no_per_unit": None,
                                             "wargear": None,
                                             "options": None,
                                             "indep": False,
                                             "pts": base_pts}
            super().__init__(parent.type)
        else:
            super().__init__(type)

        self._BoardObj__name = self.type
        return

    @property
    def root_data(self): return init.models_dict[self.type]

    @property
    def limit(self): return self.root_data["no_per_unit"]

    @property
    def pts(self): return super(Model, self).pts + self.size*self.root_data["pts"]

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

    def __hash__(self):
        ret = hash(self.name) + hash(self.type)
        if self.wargear is not None:
            ret += hash(tuple(self.wargear))
        return ret
