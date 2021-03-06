import wx
import wx.lib.agw.aui as aui
import sys
from . import gui_armytree, gui_editpanel

sys.path.append('../')
import init
import squad
import army_list


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
    close_add_unit(self, unit): Event handler when the AddUnitDialog is closed.
    add_unit_from_tree(self, unit):
        Called by gui_armytree.AddTreePane to add a unit to the army.
    add_detach(self, evt): Event Handler for when a new detachment is added.
    delete(self, evt): Event Handler for when a detachment or unit is deleted.
    """

    def __init__(self, army, *args, **kwds):
        self.army = army

        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((800, 600))
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
        add_detach_icon = wx.Bitmap("./gui/icons/add_detach.png")
        add_detach = self.toolbar.AddTool(wx.ID_ANY, 'Add Detachment',
                                          add_detach_icon)
        delete_icon = wx.Bitmap("./gui/icons/delete.png")
        delete = self.toolbar.AddTool(wx.ID_ANY, 'Delete',
                                      delete_icon)
        copy_icon = wx.Bitmap("./gui/icons/copy.png")
        copy = self.toolbar.AddTool(wx.ID_ANY, 'Copy',
                                    copy_icon)
        save_icon = wx.Bitmap("./gui/icons/save.png")
        save = self.toolbar.AddTool(wx.ID_ANY, 'Save',
                                    save_icon)
        self.Bind(wx.EVT_TOOL, self.add_unit, add_unit)
        self.Bind(wx.EVT_TOOL, self.add_detach, add_detach)
        self.Bind(wx.EVT_TOOL, self.delete, delete)
        self.Bind(wx.EVT_TOOL, self.copy, copy)
        self.Bind(wx.EVT_TOOL, self.save, save)
        self.toolbar.Realize()

        # Main panels
        self.treePane = gui_armytree.TreePane(self.army, self, wx.ID_ANY)
        self.addPane = gui_armytree.AddTreePane(self)

        self.mgr = aui.AuiManager(self)
        info = aui.AuiPaneInfo().Center().Floatable(False)
        info.BestSize(wx.Size(100, -1))
        self.mgr.AddPane(self.treePane, info)

        info = aui.AuiPaneInfo().Left().Floatable(False)
        info.BestSize(wx.Size(300, -1))
        self.mgr.AddPane(self.addPane, info)

        self.mgr.Update()
        self.Centre()

        self.Bind(wx.EVT_CHECKLISTBOX, self.on_edit)
        self.Bind(wx.EVT_SPINCTRL, self.on_edit)
        self.Bind(wx.EVT_CHECKBOX, self.on_edit)

    def reset_edit(self, unit=None):
        """Re-loads the edit panel when a new item is selected."""
        if unit is not None:
            try:
                self.editPane.set_unit(unit)
            except AttributeError:
                self.editPane = gui_editpanel.EditPanel(self, wx.ID_ANY)
                self.editPane.set_unit(unit)
                info = aui.AuiPaneInfo().Right().Floatable(False)
                info.BestSize(wx.Size(500, -1))
                self.mgr.AddPane(self.editPane, info)
                self.mgr.Update()

        self.Layout()

    def on_edit(self, evt):
        """Event Handler for when selected item is edited."""
        changed_unit = self.editPane.unit
        self.treePane.tree.DeleteChildren(changed_unit.treeid)
        self.treePane.update_unit(changed_unit)
        return

    def add_unit(self, evt):
        """Event Handler for when a new unit is added."""
        cdDialog = AddUnitDialog(self.army, parent=self, title='Create Unit')
        cdDialog.ShowModal()

    def close_add_unit(self, unit):
        """Event handler when the AddUnitDialog is closed."""
        self.treePane.add_unit(unit)
        return

    def add_unit_from_tree(self, unit):
        """Called by gui_armytree.AddTreePane to add a unit to the army."""
        detach = self.treePane.detach # last chosen detachment
        battlefield_role = unit.battlefield_role
        if detach.foc[battlefield_role][1] <= len(detach.units_dict[battlefield_role]):
            msg = "Unable to add unit to {} \n".format(detach.name)
            msg += "as {} slots are full.".format(battlefield_role)
            infoDialog = wx.MessageDialog(self, msg)
            infoDialog.ShowModal()
            return
        self.treePane.detach.add_unit(unit)
        self.treePane.add_unit(unit)
        return

    def add_detach(self, evt):
        """Event Handler for when a new detachment is added."""
        print("Add detachment")

    def delete(self, evt):
        """Event Handler for when a detachment or unit is deleted."""
        selected = self.treePane.tree.GetFocusedItem()
        item = self.treePane.tree.GetItemData(selected)
        # reset edit panel if unit is currently selected
        if isinstance(item, squad.Unit):
            try:
                if self.editPane.unit == item:
                    self.reset_edit()
            except:
                pass

        # delete the selected item from the tree and army
        self.treePane.delete()
        return

    def copy(self, evt):
        """Event Handler for when a detachment or unit is copied."""
        print("Copy")
        return

    def save(self, evt):
        """Event Handler for saving the the army"""
        print("Save")
        return


class AddDialog(wx.Dialog):
    """
    Custom wx.Dialog template class for adding to the army.

    Parameters
    ----------
    army : army_list.ArmyList

    *args : wx.Dialog arguments
    **kw : wx.Dialog keyword arguments

    Public Methods
    -----------
    InitButtons(self, vbox): Adds Cancel and Add buttons to the supplied sizer.

    on_close(self, event):
        Event Handler for when the user closes the window by pressing either of
        the buttons.
    """

    def __init__(self, army, *args, **kw):
        super(AddDialog, self).__init__(*args, **kw)
        self.army = army

    def InitButtons(self, vbox):
        """Adds Cancel and Add buttons to the supplied sizer."""
        # add box for close buttom
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        createButton = wx.Button(self, label='Add')
        cancelButton = wx.Button(self, label='Cancel')
        hbox2.Add(createButton)
        hbox2.Add(cancelButton, flag=wx.LEFT, border=5)

        vbox.Add(hbox2, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=5)

        self.SetSizer(vbox)
        self.Fit()
        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.on_close)

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
            battlefield_role = self.foc_combo.GetString(self.foc_combo.GetSelection())
            unit_string = self.unit_choice.GetString(self.unit_choice.GetSelection())
            unit = squad.Unit(unit_string, battlefield_role)
            detachment.add_unit(unit)
            self.GetParent().close_add_unit(unit)
        self.Destroy()


class AddUnitDialog(AddDialog):
    """
    Dialog inherited from AddDialog to add units to the army.

    Parameters
    ----------
    army : army_list.ArmyList

    *args : wx.Dialog arguments
    **kw : wx.Dialog keyword arguments

    Public Methods
    --------------
    on_foc_choice(self, event):
        Event Handler to populate unit options when battlefield role is
        selected.

    on_detach_choice(self, event):
        Event Handler to populate foc options when detachment is chosen based on
        the slots left in the detachment.

    on_close(self, event):
        Event Handler for when the user closes the window by pressing either of
        the buttons.
    """

    def __init__(self, army, *args, **kw):
        super(AddUnitDialog, self).__init__(army, *args, **kw)
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
        foc = ["HQ", "Troops", "Elites", "Fast Attack", "Heavy Support"]
        self.foc_combo = wx.Choice(self, wx.ID_ANY, choices=foc,
                                   style=wx.CB_READONLY)

        txt3 = wx.StaticText(self, wx.ID_ANY, "Unit:")
        self.unit_choice = wx.ListBox(self, choices=[])

        vbox1.Add(txt1, border=5)
        vbox1.Add(self.detach_combo, 0, wx.EXPAND | wx.ALL, 5)
        vbox1.Add(txt2, border=5)
        vbox1.Add(self.foc_combo, 0, wx.EXPAND | wx.ALL, 5)

        self.warntxt = wx.StaticText(self, wx.ID_ANY, '')

        vbox.Add(vbox1, flag=wx.EXPAND, border=5)
        vbox.Add(txt3, border=5)
        vbox.Add(self.unit_choice, 1, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self.warntxt, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=5)
        self.Bind(wx.EVT_CHOICE, self.on_detach_choice, self.detach_combo)
        self.Bind(wx.EVT_CHOICE, self.on_foc_choice, self.foc_combo)

        # create Cancel and create buttons
        self.InitButtons(vbox)
        return

    def on_foc_choice(self, event):
        """
        Event Handler to populate unit options when battlefield role is
        selected.
        """
        battlefield_role = self.foc_combo.GetSelection()
        battlefield_role = self.foc_combo.GetString(battlefield_role)
        units_list = list(init.units_dict[battlefield_role].keys())
        if battlefield_role == "HQ":
            units_list = list(init.units_dict["Named Characters"].keys()) + units_list

        self.unit_choice.Clear()
        self.unit_choice.Append(units_list)
        return

    def on_detach_choice(self, event):
        """
        Event Handler to populate foc options when detachment is chosen based on
        the slots left in the detachment.
        """
        detachment = self.detach_combo.GetSelection()
        detachment = self.army.detachments[detachment]
        # create list of battlefield roles that still have slots left
        foc = [key for key, item in detachment.units_dict.items() if len(item) <
               detachment.foc[key][1]]

        # get current selection if choice has been made
        choice = self.foc_combo.GetSelection()
        if not choice == wx.NOT_FOUND:  # stops backend Critical warning
            choice = self.foc_combo.GetString(choice)
        self.foc_combo.Clear()
        self.foc_combo.Append(foc)

        # reinstate the choice or clear the unit_choice box
        if not choice == wx.NOT_FOUND:  # stops backend Critical warning
            if choice in foc:
                self.foc_combo.SetSelection(foc.index(choice))
            else:
                self.unit_choice.Clear()
        return


class AddDetachDialog(AddDialog):
    """
    Dialog inherited from AddDialog to add detachments to the army.

    Parameters
    ----------
    army : army_list.ArmyList

    *args : wx.Dialog arguments
    **kw : wx.Dialog keyword arguments

    Public Methods
    -------------
    """

    def __init__(self, army, *args, **kw):
        super(AddDetachDialog, self).__init__(army, *args, **kw)
        self.InitUI()
        self.SetSize((300, 400))
        return

    def InitUI(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        # add main panel
        ctrl_sizer = wx.BoxSizer(wx.VERTICAL)
        txt1 = wx.StaticText(self, wx.ID_ANY, "Detachment type:")
        self.detach_combo = wx.Choice(self, wx.ID_ANY,
                                      choices=list(init.detachments_dict.keys()),
                                      style=wx.CB_READONLY)
        txt2 = wx.StaticText(self, wx.ID_ANY, "Detachment name:")
        self.name_ctrl = wx.TextCtrl(self)

        ctrl_sizer.Add(txt1, border=5)
        ctrl_sizer.Add(self.detach_combo, 0, wx.EXPAND | wx.ALL, 5)
        ctrl_sizer.Add(txt2, border=5)
        ctrl_sizer.Add(self.name_ctrl, 0, wx.EXPAND | wx.ALL, 5)

        # create sizer to be populated with unit choices once a type has been
        # selected
        self.choice_sizer = wx.BoxSizer(wx.VERTICAL)

        self.warntxt = wx.StaticText(self, wx.ID_ANY, '')

        vbox.Add(ctrl_sizer, flag=wx.EXPAND, border=5)
        vbox.Add(self.choice_sizer, 1, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self.warntxt, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=5)

        self.Bind(wx.EVT_CHOICE, self.on_detach_choice, self.detach_combo)

        # create Cancel and create buttons
        self.InitButtons(vbox)
        return

    def on_detach_choice(self, event):
        """
        Event Handler to populate foc options when detachment is chosen based on
        the slots left in the detachment.
        """
        detachment = self.detach_combo.GetSelection()
        detachment = self.detach_combo.GetString(detachment)

        # create list of battlefield roles that still have slots left
        foc = [key for key, item in init.detachments_dict[detachment]["foc"].items() if item[0] > 0]
        print(foc)

        # get current selection if choice has been made
        # choice = self.foc_combo.GetSelection()
        # if not choice == wx.NOT_FOUND:  # stops backend Critical warning
        #     choice = self.foc_combo.GetString(choice)
        # self.foc_combo.Clear()
        # self.foc_combo.Append(foc)
        #
        # # reinstate the choice or clear the unit_choice box
        # if not choice == wx.NOT_FOUND:  # stops backend Critical warning
        #     if choice in foc:
        #         self.foc_combo.SetSelection(foc.index(choice))
        #     else:
        #         self.unit_choice.Clear()
        return
