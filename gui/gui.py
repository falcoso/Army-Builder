import wx
from . import gui_armytree


class HomeFrame(wx.Frame):
    def __init__(self, army, *args, **kwds):
        self.army = army

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

        # Main panels
        self.splitWindow = wx.SplitterWindow(self, wx.ID_ANY)
        self.treePane = gui_armytree.TreePane(self.army, self.splitWindow, wx.ID_ANY)
        self.editPane = wx.Panel(self.splitWindow, wx.ID_ANY)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("Army Builder v1.0")
        self.toolBar.Realize()
        self.splitWindow.SetMinimumPaneSize(20)

    def __do_layout(self):
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add((0, 0), 0, 0, 0)
        self.editPane.SetSizer(sizer_3)
        self.splitWindow.SplitVertically(self.treePane, self.editPane)
        mainSizer.Add(self.splitWindow, 1, wx.EXPAND, 0)
        self.SetSizer(mainSizer)
        self.Layout()
