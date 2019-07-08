import wx
import sys

sys.path.append('../')
import squad


class TreePane(wx.Panel):
    def __init__(self, army, *args, **kwargs):
        super(TreePane, self).__init__(*args, **kwargs)
        self.army = army
        self.treeSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.treeSizer)
        self.build_tree()
        return

    def build_tree(self):
        self.tree = wx.TreeCtrl(self, wx.ID_ANY)
        self.treeSizer.Add(self.tree, 1, wx.EXPAND, 0)

        self.root = self.tree.AddRoot("Army")
        self.tree.SetItemData(self.root, self.army)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_selection)
        self.detach_nodes = {}  # dictionary to keep track of detachment nodes

        # construct tree
        for detach in self.army.detachments:
            self.detach_nodes[detach.name] = self.tree.AppendItem(self.root,
                                                                  detach.name)
            self.tree.SetItemData(self.detach_nodes[detach.name], detach)
            for battlefield_role, units in detach.units_dict.items():
                if units != []:
                    foc_node = self.tree.AppendItem(self.detach_nodes[detach.name],
                                                    battlefield_role)

                for unit in units:
                    unit.set_treeid(self.tree.AppendItem(foc_node, unit.name))
                    self.tree.SetItemData(unit.treeid, unit)
                    self.update_unit(unit)
        return

    def update_unit(self, unit):
        for wargear in unit.wargear:
            self.tree.AppendItem(unit.treeid, wargear.__repr__())


    def on_selection(self, evt):
        # changes to the unit will change the reference in the whole army
        unit = self.tree.GetItemData(evt.GetItem())
        if not isinstance(unit, squad.Unit):
            return
        print(unit)
        main_window = self.GetParent()
        main_window.reset_edit(unit)
        return
