import wx
import sys

sys.path.append('../')
import squad


class TreePane(wx.Panel):
    def __init__(self, army, *args, **kwargs):
        super(TreePane, self).__init__(*args, **kwargs)
        self.army = army
        self.tree = wx.TreeCtrl(self, wx.ID_ANY)
        self.treeSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.treeSizer.Add(self.tree, 1, wx.EXPAND, 0)
        self.SetSizer(self.treeSizer)

        self.build_tree()
        return

    def build_tree(self):
        self.root = self.tree.AddRoot("Army")
        self.tree.SetItemData(self.root, self.army)
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_selection)
        self.detach_nodes = {}  # dictionary to keep track of detachment nodes

        # construct tree
        for detach in self.army.detachments:
            self.detach_nodes[detach.name] = self.tree.AppendItem(self.root,
                                                                  detach.name)
            self.tree.SetItemData(self.detach_nodes[detach.name], detach)
            for battlefield_role, units in detach.units_dict.items():
                foc_node = self.tree.AppendItem(self.detach_nodes[detach.name],
                                                battlefield_role)

                for unit in units:
                    unit_node = self.tree.AppendItem(foc_node, unit.name)
                    self.tree.SetItemData(unit_node, unit)
        return


    def on_selection(self, evt):
        # changes to the unit will change the reference in the whole army
        unit = self.tree.GetPyData(evt.GetItem())
        if not isinstance(unit, squad.Unit):
            return
        print(unit)
        return
