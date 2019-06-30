import wx


class HomeFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: HomeFrame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((630, 560))

        # Menu Bar
        self.menuBar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        self.menuBar.Append(wxglade_tmp_menu, "File")
        wxglade_tmp_menu = wx.Menu()
        self.menuBar.Append(wxglade_tmp_menu, "Edit")
        self.SetMenuBar(self.menuBar)
        # Menu Bar end

        # Tool Bar
        self.toolBar = wx.ToolBar(self, -1, style=wx.TB_DOCKABLE | wx.TB_HORIZONTAL)
        self.SetToolBar(self.toolBar)
        # Tool Bar end
        self.splitWindow = wx.SplitterWindow(self, wx.ID_ANY)
        self.treePane = wx.Panel(self.splitWindow, wx.ID_ANY)
        self.editPane = wx.Panel(self.splitWindow, wx.ID_ANY)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: HomeFrame.__set_properties
        self.SetTitle("Army Builde v1.0")
        self.toolBar.Realize()
        self.splitWindow.SetMinimumPaneSize(20)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: HomeFrame.__do_layout
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        treeSizer = wx.BoxSizer(wx.HORIZONTAL)
        treeSizer.Add(self.ArmyTree, 1, wx.EXPAND, 0)
        self.treePane.SetSizer(treeSizer)
        sizer_3.Add((0, 0), 0, 0, 0)
        self.editPane.SetSizer(sizer_3)
        self.splitWindow.SplitVertically(self.treePane, self.editPane)
        mainSizer.Add(self.splitWindow, 1, wx.EXPAND, 0)
        self.SetSizer(mainSizer)
        self.Layout()

class MyApp(wx.App):
    def OnInit(self):
        self.frame = HomeFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
