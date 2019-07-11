import wx
import sys

sys.path.append('../')
import squad
import army_list
import init


class TreePane(wx.Panel):
    """
    Class inherited from wx.Panel to display the tree for the army

    Parameters
    ----------
    army : army_list.ArmyList
        Army to be displayed.

    *args : wx.Panel arguments
    **kwargs : wx.Panel keyword arguments

    Attributes
    ----------
    army : army_list.ArmyList
        Army to be displayed.
    detach : army_list.Detachment
        Last Detachment selected or interacted with.
    tree: wx.TreeCtrl
        Tree object displaying the army.
    treeSizer : wx.TreeCtrl
        Main panel sizer.
    root: wx.TreeID
        Tree root node.
    foc_node: dict {detachment.treeid: {battlefield_role: wx.TreeID}}
        Dictionary to keep track of the battlefield_role nodes for each
        detachment.

    Public Methods
    --------------
    build_tree(self): Constructs Tree.

    update_unit(self, unit):
        Refreshes the wargear on the unit and the pts displayed on itself and
        all parents of the unit.

    update_headers(self, treeid):
        Updates the points values on the item's parent's headers.

    add_unit(self, unit): Adds the given unit to the tree.

    on_selection(self, evt):
        Event Handler to update the gui_editpanel.EditPanel in the parent
        window.
    """

    def __init__(self, army, *args, **kwargs):
        super(TreePane, self).__init__(*args, **kwargs)
        self.army = army
        if len(army.detachments) == 1:
            self.detach = army.detachments[-1]
        else:
            self.detach = None
        self.treeSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.treeSizer)
        self.build_tree()
        return

    def build_tree(self):
        """Constructs Tree."""
        self.tree = wx.TreeCtrl(self, wx.ID_ANY)
        self.treeSizer.Add(self.tree, 1, wx.EXPAND, 0)

        self.root = self.tree.AddRoot("Army")
        self.tree.SetItemData(self.root, self.army)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_selection)
        self.foc_node = {}  # dictionary to keep track of detachment no

        # construct tree
        for detach in self.army.detachments:
            detach.treeid = self.tree.AppendItem(self.root, detach.name)

            self.tree.SetItemData(detach.treeid, detach)
            self.foc_node[detach.treeid] = {}
            for battlefield_role, units in detach.units_dict.items():
                if units != []:
                    foc_node = self.tree.AppendItem(detach.treeid,
                                                    battlefield_role)
                    self.foc_node[detach.treeid][battlefield_role] = foc_node

                for unit in units:
                    unit.treeid = self.tree.AppendItem(foc_node, unit.name)
                    self.tree.SetItemData(unit.treeid, unit)
                    self.update_unit(unit)
        self.tree.ExpandAll()
        return

    def update_unit(self, unit):
        """
        Refreshes the wargear on the unit and the pts displayed on itself and
        all parents of the unit.
        """
        # update points labels on all parent nodes
        self.update_headers(unit.treeid)

        # if only single model just list all wargear
        if unit.size == 1:
            model = unit.models[0]
            if unit.wargear is not None:
                for wargear in unit.wargear:
                    self.tree.AppendItem(unit.treeid, wargear.__repr__())
            if model.wargear is not None:
                for wargear in model.wargear:
                    self.tree.AppendItem(unit.treeid, wargear.__repr__())

        # create node for each model and list individual wargear
        else:
            for model in unit.models:
                model_id = self.tree.AppendItem(unit.treeid,
                                                model.__repr__().split("\n")[0])
                model.treeid = model_id
                if unit.wargear is not None:
                    for wargear in unit.wargear:
                        self.tree.AppendItem(model_id, wargear.__repr__())
                if model.wargear is not None:
                    for wargear in model.wargear:
                        self.tree.AppendItem(model_id, wargear.__repr__())

        self.tree.ExpandAllChildren(unit.treeid)
        return

    def update_headers(self, treeid):
        """Updates the points values on the item's parent's headers."""
        treeid = self.tree.GetItemParent(treeid)
        while treeid.IsOk():
            if treeid == self.root:
                self.tree.SetItemText(self.root,
                                      "Army ({}pts)".format(self.army.pts))
                break
            try:
                item = self.tree.GetItemData(treeid)
                self.tree.SetItemText(item.treeid,
                                      "{} ({}pts)".format(item.name, item.pts))
            except AttributeError:
                pass
            treeid = self.tree.GetItemParent(treeid)
        return

    def add_unit(self, unit):
        """Adds the given unit to the tree."""
        parent_node = unit.parent.treeid
        try:
            foc_node = self.foc_node[parent_node][unit.battlefield_role]
        except KeyError:  # foc role is not yet on the tree
            foc_node = self.tree.AppendItem(parent_node, unit.battlefield_role)
            self.foc_node[parent_node][unit.battlefield_role] = foc_node

        unit.treeid = self.tree.AppendItem(foc_node, unit.name)
        self.tree.SetItemData(unit.treeid, unit)
        self.update_unit(unit)
        self.tree.Expand(foc_node)
        self.tree.Expand(unit.treeid)
        return

    def on_selection(self, evt):
        """
        Event Handler to update the gui_editpanel.EditPanel in the parent
        window.
        """
        # changes to the unit will change the reference in the whole army
        unit = self.tree.GetItemData(evt.GetItem())
        if isinstance(unit, squad.Unit):
            main_window = self.GetParent()
            main_window.reset_edit(unit)
            self.detach = unit.parent
        elif isinstance(unit, army_list.Detachment):
            self.detach = unit
        return


class AddTreePane(wx.Panel):
    """
    Class inherited from wx.Panel to to display all the models that can be added
    to the army.

    Parameters
    ----------
    *args : wx.Panel arguments
    **kwargs : wx.Panel keyword arguments

    Attributes
    ----------
    treeSizer : wx.TreeCtrl
        Main panel sizer.
    root: wx.TreeID
        Tree root node.

    Public Methods
    --------------
    build_tree(self): Constructs Tree.
    on_selection(self, evt): Event Handler to add the selected unit to the army.
    """
    def __init__(self, *args, **kwargs):
        super(AddTreePane, self).__init__(*args, **kwargs)
        self.treeSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.treeSizer)
        self.build_tree()
        return

    def build_tree(self):
        self.tree = wx.TreeCtrl(self, wx.ID_ANY, style=wx.TR_HIDE_ROOT)
        self.treeSizer.Add(self.tree, 1, wx.EXPAND, 0)

        self.root = self.tree.AddRoot("Army")
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_selection)

        for role in init.units_dict.keys():
            role_node = self.tree.AppendItem(self.root, role)
            for unit in init.units_dict[role]:
                unit = init.units_dict[role][unit]
                unit_node = self.tree.AppendItem(role_node,
                                                 unit.name + "({}pts)".format(unit.pts))
                self.tree.SetItemData(unit_node, unit)

        self.tree.ExpandAll()

    def on_selection(self, evt):
        """
        Event Handler to add the selected unit to the army.
        """
        # changes to the unit will change the reference in the whole army
        unit = self.tree.GetItemData(evt.GetItem())
        if not isinstance(unit, init.UnitTypes):
            return
        battlefield_role = self.tree.GetItemParent(evt.GetItem())
        battlefield_role = self.tree.GetItemText(battlefield_role)
        unit = squad.Unit(unit.name, battlefield_role)
        main_window = self.GetParent()
        main_window.add_unit_from_tree(unit)
        return
