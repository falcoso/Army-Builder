import wx

class TreePane(wx.Panel):
    def __init__(self, army, *args, **kwargs):
        super(TreePane, self).__init__(*args, **kwargs)
        self.army = army
        self.tree  = wx.TreeCtrl(self, wx.ID_ANY)
        treeSizer = wx.BoxSizer(wx.HORIZONTAL)
        treeSizer.Add(self.tree, 1, wx.EXPAND, 0)
        self.SetSizer(treeSizer)

        self.root = self.tree.AddRoot("Army")
        self.detach_nodes = {}
        for detach in army.detachments:
            self.detach_nodes[detach.name] = self.tree.AppendItem(self.root,
                                                                  detach.name)
            for battlefield_role, units in detach.units_dict.items():
                foc_node = self.tree.AppendItem(self.detach_nodes[detach.name],
                                                battlefield_role)

                for unit in units:
                    self.tree.AppendItem(foc_node, unit.name)
