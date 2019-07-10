import wx
import sys

sys.path.append('../')
import squad


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

    add_unit(self, unit): Adds the given unit to the tree.

    on_selection(self, evt):
        Event Handler to update the gui_editpanel.EditPanel in the parent
        window.
    """
    def __init__(self, army, *args, **kwargs):
        super(TreePane, self).__init__(*args, **kwargs)
        self.army = army
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
            detach.set_treeid(self.tree.AppendItem(self.root, detach.name))

            self.tree.SetItemData(detach.treeid, detach)
            self.foc_node[detach.treeid] = {}
            for battlefield_role, units in detach.units_dict.items():
                if units != []:
                    foc_node = self.tree.AppendItem(detach.treeid,
                                                    battlefield_role)
                    self.foc_node[detach.treeid][battlefield_role] = foc_node

                for unit in units:
                    unit.set_treeid(self.tree.AppendItem(foc_node, unit.name))
                    self.tree.SetItemData(unit.treeid, unit)
                    self.update_unit(unit)
        self.tree.ExpandAll()
        return

    def update_unit(self, unit):
        """
        Refreshes the wargear on the unit and the pts displayed on itself and
        all parents of the unit.
        """
        self.tree.SetItemText(unit.treeid,
                              "{} ({}pts)".format(unit.name, unit.pts))
        detach = unit.parent
        self.tree.SetItemText(detach.treeid,
                              "{} ({}pts)".format(detach.name, detach.get_pts()))
        self.tree.SetItemText(self.root,
                              "Army ({}pts)".format(self.army.get_pts()))
        for wargear in unit.wargear:
            self.tree.AppendItem(unit.treeid, wargear.__repr__())

    def add_unit(self, unit):
        """Adds the given unit to the tree."""
        parent_node = unit.parent.treeid
        try:
            foc_node = self.foc_node[parent_node][unit.battlefield_role]
        except KeyError:
            foc_node = self.tree.AppendItem(parent_node, unit.battlefield_role)
            self.foc_node[parent_node][unit.battlefield_role] = foc_node

        unit.set_treeid(self.tree.AppendItem(foc_node, unit.name))
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
        if not isinstance(unit, squad.Unit):
            return
        main_window = self.GetParent()
        main_window.reset_edit(unit)
        return
