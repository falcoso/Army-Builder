import wx
import sys
from . import gui_armytree, gui_editpanel

sys.path.append('../')
import init
import squad


class HomeFrame(wx.Frame):
    """
    Main Frame for ArmyBuilder

    Parameters
    ----------
    army : army_list.ArmyList

    *args : wx.Frame arguments
    **kwds : wx.Frame keyword arguments

    Attributes
    ----------
    army : army_list.ArmyList
    menuBar : wx.MenuBar
    toolbar : wx.ToolBar
    treePane : gui_armytree.TreePane
        Panel displaying the Army Tree.
    editPane : guit_editpanel.EditPanel
        Panel displaying the edit widgets for the selected item.

    Public Methods
    --------------
    reset_edit(self, unit): Re-loads the edit panel when a new item is selected.
    on_edit(self, evt): Event Handler for when selected item is editted.
    add_unit(self, evt): Event Handler for when a new unit is added.
    del_unit(self, evt): Event Handler for when a unit is deleted.
    add_detach(self, evt): Event Handler for when a new detachment is added.
    del_detach(self, evt): Event Handler for when a detachment is deleted.
    """

    def __init__(self, army, *args, **kwds):
        self.army = army

        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((630, 560))
        self.SetTitle("Army Builder v1.0")

        # Menu Bar
        self.menuBar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        self.menuBar.Append(wxglade_tmp_menu, "File")
        wxglade_tmp_menu = wx.Menu()
        self.menuBar.Append(wxglade_tmp_menu, "Edit")
        self.SetMenuBar(self.menuBar)
        # Menu Bar end

        # Tool Bar
        self.toolbar = self.CreateToolBar()
        add_unit_icon = wx.Bitmap("./gui/icons/add_unit.png")
        add_unit = self.toolbar.AddTool(wx.ID_ANY, 'Add Unit', add_unit_icon)
        del_unit_icon = wx.Bitmap("./gui/icons/del_unit.png")
        del_unit = self.toolbar.AddTool(wx.ID_ANY, 'Delete Unit', del_unit_icon)

        add_detach_icon = wx.Bitmap("./gui/icons/add_detach.png")
        add_detach = self.toolbar.AddTool(wx.ID_ANY, 'Add Detachment',
                                          add_detach_icon)
        del_detach_icon = wx.Bitmap("./gui/icons/del_detach.png")
        del_detach = self.toolbar.AddTool(wx.ID_ANY, 'Delete Detachment',
                                          del_detach_icon)
        self.Bind(wx.EVT_TOOL, self.add_unit, add_unit)
        self.Bind(wx.EVT_TOOL, self.del_unit, del_unit)
        self.Bind(wx.EVT_TOOL, self.add_detach, add_detach)
        self.Bind(wx.EVT_TOOL, self.del_detach, del_detach)
        self.toolbar.Realize()

        # Main panels
        self.treePane = gui_armytree.TreePane(self.army, self, wx.ID_ANY)
        self.editPane = gui_editpanel.EditPanel(self, wx.ID_ANY)

        self.__do_layout()
        self.Bind(wx.EVT_CHECKLISTBOX, self.on_edit)
        self.Bind(wx.EVT_SPINCTRL, self.on_edit)
        self.Bind(wx.EVT_CHECKBOX, self.on_edit)

    def __do_layout(self):
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer.Add(self.treePane, 1, wx.EXPAND, 0)
        self.mainSizer.Add(self.editPane, 0, wx.EXPAND, 0)
        self.SetSizer(self.mainSizer)
        self.Layout()

    def reset_edit(self, unit):
        """Re-loads the edit panel when a new item is selected."""
        self.editPane.Destroy()
        self.editPane = gui_editpanel.EditPanel(self, wx.ID_ANY)
        self.mainSizer.Add(self.editPane, 0, wx.EXPAND, 0)
        self.editPane.set_unit(unit)
        self.Layout()

    def on_edit(self, evt):
        """Event Handler for when selected item is edited."""
        changed_unit = self.editPane.unit
        self.treePane.tree.DeleteChildren(changed_unit.treeid)
        self.treePane.update_unit(changed_unit)
        return

    def add_unit(self, evt):
        """Event Handler for when a new unit is added"""
        cdDialog = AddUnitDialog(self.army, parent=self, title='Create Unit')
        cdDialog.ShowModal()

    def close_add_unit(self, unit):
        """Event handler when the AddUnitDialog is closed"""
        self.treePane.add_unit(unit)
        return

    def del_unit(self, evt):
        """Event Handler for when a unit is deleted"""
        print("Delete unit")

    def add_detach(self, evt):
        """Event Handler for when a new detachment is added"""
        print("Add detachment")

    def del_detach(self, evt):
        """Event Handler for when a detachment is deleted"""
        print("Delete detachment")


class AddUnitDialog(wx.Dialog):
    """
    Custom wx.Dialog that allows the user to create a new unit.

    Parameters
    ----------
    army : army_list.ArmyList

    *args : wx.Dialog arguments
    **kw : wx.Dialog keyword arguments

    Public Methods
    ----------
    on_foc_choice(self, event):
        Event Handler to populate unit options when battlefield role is
        selected.

    on_close(self, event):
        Event Handler for when the user closes the window by pressing either of
        the buttons.
    """

    def __init__(self, army, *args, **kw):
        super(AddUnitDialog, self).__init__(*args, **kw)
        self.army = army
        self.InitUI()
        self.SetSize((300, 400))

    def InitUI(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        # add main panel
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        txt1 = wx.StaticText(self, wx.ID_ANY, "Detachment:")
        self.detach_combo = wx.Choice(self, wx.ID_ANY,
                                      choices=self.army.detachment_names,
                                      style=wx.CB_READONLY)

        txt2 = wx.StaticText(self, wx.ID_ANY, "Battlefield Role:")
        self.foc = ["HQ", "Troops", "Elites", "Fast Attack", "Heavy Support"]
        self.foc_combo = wx.Choice(self, wx.ID_ANY, choices=self.foc,
                                   style=wx.CB_READONLY)

        txt3 = wx.StaticText(self, wx.ID_ANY, "Unit:")
        self.unit_choice = wx.ListBox(self, choices=[])

        vbox1.Add(txt1, border=5)
        vbox1.Add(self.detach_combo, 0, wx.EXPAND | wx.ALL, 5)
        vbox1.Add(txt2, border=5)
        vbox1.Add(self.foc_combo, 0, wx.EXPAND | wx.ALL, 5)

        self.warntxt = wx.StaticText(self, wx.ID_ANY, '')

        # add box for close buttom
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        createButton = wx.Button(self, label='Add')
        cancelButton = wx.Button(self, label='Cancel')
        hbox2.Add(createButton)
        hbox2.Add(cancelButton, flag=wx.LEFT, border=5)

        vbox.Add(vbox1, flag=wx.EXPAND, border=5)
        vbox.Add(txt3, border=5)
        vbox.Add(self.unit_choice, 1, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self.warntxt, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=5)
        vbox.Add(hbox2, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=5)

        self.SetSizer(vbox)
        self.Fit()
        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.on_close)
        self.Bind(wx.EVT_CHOICE, self.on_foc_choice, self.foc_combo)

    def on_foc_choice(self, event):
        """
        Event Handler to populate unit options when battlefield role is
        selected.
        """
        battlefield_role = self.foc_combo.GetSelection()
        battlefield_role = self.foc[battlefield_role]
        units_list = list(init.units_dict[battlefield_role].keys())
        if battlefield_role == "HQ":
            units_list = list(init.units_dict["Named Characters"].keys()) + units_list

        self.unit_choice.Clear()
        self.unit_choice.Append(units_list)

    def on_close(self, event):
        """
        Event Handler for when the user closes the window by pressing either of
        the buttons.
        """
        evt = event.GetEventObject().GetLabel()
        if evt == "Add":
            if wx.NOT_FOUND in {self.detach_combo.GetSelection(),
                                self.foc_combo.GetSelection(),
                                self.unit_choice.GetSelection()}:

                self.warntxt.SetLabel("Fill in all the fields")
                self.Layout()
                return
            detachment = self.army.detachments[self.detach_combo.GetSelection()]
            battlefield_role = self.foc[self.foc_combo.GetSelection()]
            unit_string = self.unit_choice.GetString(self.unit_choice.GetSelection())
            unit = squad.Unit(unit_string, battlefield_role)
            detachment.add_unit(unit)
            self.GetParent().close_add_unit(unit)
        self.Destroy()
