import wx
from . import gui_armytree, gui_editpanel


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
        self.treePane = gui_armytree.TreePane(self.army, self, wx.ID_ANY)
        self.editPane = gui_editpanel.EditPanel(self, wx.ID_ANY)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("Army Builder v1.0")
        self.toolBar.Realize()

    def __do_layout(self):
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer.Add(self.treePane, 1, wx.EXPAND, 0)
        self.mainSizer.Add(self.editPane, 1, wx.EXPAND, 0)
        self.SetSizer(self.mainSizer)
        self.Layout()

    def reset_edit(self, unit):
        self.editPane.Destroy()
        self.editPane = gui_editpanel.EditPanel(self, wx.ID_ANY)
        self.mainSizer.Add(self.editPane, 1, wx.EXPAND, 0)
        self.editPane.set_unit(unit)
        self.Layout()
