import wx

class TreePane(wx.Panel):
    def __init__(self, army, *args, **kwargs):
        super(TreePane, self).__init__(*args, **kwargs)
        self.army = army
        self.tree  = wx.TreeCtrl(self.treePane, wx.ID_ANY)
        treeSizer = wx.BoxSizer(wx.HORIZONTAL)
        treeSizer.Add(self.tree, 1, wx.EXPAND, 0)
        self.SetSizer(treeSizer)
