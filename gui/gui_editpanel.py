import wx
import sys
from wx.lib.scrolledpanel import ScrolledPanel

sys.path.append('../')
import squad


class EditPanel(ScrolledPanel):
    """
    Class inherited from wx.lib.scrolledpanel.ScrolledPanel to generate all
    parameters and options associated with a selected unit.

    *args : wx.Panel arguments
    **kw : wx.Panel keyword arguments

    Parameters
    ----------
    *args : wx.lib.scrolledpanel.ScrolledPanel arguments
    **kw : wx.lib.scrolledpanel.ScrolledPanel keyword arguments

    Attributes
    ----------
    unit : squad.Unit
        Unit for which the panel is generated.

    Public Methods
    --------------
    set_unit(self, unit): Sets the unit for the panel and re-generates widgets.
    on_choice(self, evt): Event handler for wx.CheckBoxList choice.
    on_size(self, evt): Event handler for wx.SpinCtrl change.
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.unit = None
        self.__InitUI()
        self.SetScrollRate(0, 10)
        self.SetSizer(self.sizer)
        self.Fit()

    def __InitUI(self):
        if self.unit is None:
            return

        self.title = wx.StaticText(self, wx.ID_ANY, self.unit.name)
        self.sizer.Add(self.title)

        # create sizing box
        if len(self.unit.size_range) != 1:
            self.models_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Models")
            if self.unit.mod_str is not None:
                self.modList = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
                for model in self.unit.mod_str:
                    txt = wx.StaticText(self, wx.ID_any, model)
                    size = 0
                    for i in self.unit.models:
                        if i.label == model:
                            size = i.no_models
                            break

                    size_ctrl = wx.SpinCtrl(self, wx.ID_ANY, str(size),
                                            name=model)

                    self.modList.Add(txt, 1, wx.ALL, 1)
                    self.modList.Add(size_ctrl, 1, wx.ALL, 1)

            elif self.unit.mod_str is None:
                self.models_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Models")
                self.modList = wx.BoxSizer(wx.HORIZONTAL)
                model_txt = wx.StaticText(self, wx.ID_ANY, self.unit.type)
                size_ctrl = wx.SpinCtrl(self, wx.ID_ANY,
                                        str(self.unit.get_size()),
                                        name=self.unit.type)
                size_ctrl.SetRange(*self.unit.size_range)
                self.modList.Add(model_txt, 1, wx.ALL, 1)
                self.modList.Add(size_ctrl, 1, wx.ALL, 1)

            self.Bind(wx.EVT_SPINCTRL, self.on_size)
            self.models_box.Add(self.modList)
            self.sizer.Add(self.models_box)

        # create options box
        if self.unit.options is not None:
            self.options_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Options")
            if self.unit.parser.options_list == []:
                for option in self.unit.options:
                    self.unit.parser.parse2(option)

            name = 0
            for option in self.unit.parser.options_list:
                option_txt = wx.StaticText(self, wx.ID_ANY,
                                           "Pick {} from:".format(option.no_picks))
                option_chkbx = OptionCheckBox(option, self.unit.wargear, self,
                                              name=str(name))
                self.options_box.Add(option_txt, 0, wx.ALL, 0)
                self.options_box.Add(option_chkbx, 0, wx.FIXED_MINSIZE, 0)
                self.Bind(wx.EVT_CHECKLISTBOX, self.on_choice)
                name += 1

            self.sizer.Add(self.options_box, 0, wx.EXPAND, 0)
        self.Fit()
        self.Layout()
        return

    def set_unit(self, unit):
        """Sets the unit for the panel and re-generates widgets."""
        self.unit = unit
        self.__InitUI()
        return

    def on_choice(self, evt):
        """Event handler for wx.CheckBoxList choice."""
        option = int(evt.GetEventObject().GetName())
        option = self.unit.parser.options_list[option]
        selections = evt.GetEventObject().GetCheckedItems()

        for i in selections:
            option.select(i)
        self.unit.change_wargear([option])
        print(self.unit)
        evt.Skip()

    def on_size(self, evt):
        """Event handler for wx.SpinCtrl change."""
        size = evt.GetEventObject().GetValue()
        self.unit.re_size(size)  # will need updating when multiple models are available
        print(self.unit)
        evt.Skip()
        return


class OptionCheckBox(wx.CheckListBox):
    """
    Custom wx.CheckListBox for generating unit/model options.

    Parameters
    ----------
    option : option_parser.Option
        Option for which the CheckBox has been created
    *args : wx.CheckListBox arguments
    **kw : wx.CheckListBox keyword arguments

    Attributes
    ----------
    selected : List (int)
        List of currently selected item indexes.
    option : option_parser.Option
        Option for which the CheckBox has been created
    """
    def __init__(self, option, wargear, *args, **kw):
        chk_list = [i.__repr__(tidy=True) for i in option.items_involved]

        super(OptionCheckBox, self).__init__(*args, choices=chk_list, **kw)
        self.option = option
        self.Bind(wx.EVT_CHECKLISTBOX, self.__on_choice)
        self.selected = []
        chkd_str = []
        for item in wargear:
            if item in self.option.items_involved:
                chkd_str.append(item.__repr__(tidy=True))
        self.__handle_evt = False
        self.SetCheckedStrings(chkd_str)
        self.__handle_evt = True
        return

    def SetCheckedStrings(self, strings):
        super().SetCheckedStrings(strings)
        self.selected = list(super().GetCheckedItems())
        return

    def SetCheckedItems(self, items):
        super().SetCheckedItems(items)
        self.selected = list(super().GetCheckedItems())
        return

    def __on_choice(self, evt):
        if self.__handle_evt:
            new_selection = super().GetCheckedItems()
            if len(new_selection) > len(self.selected) and len(new_selection) > self.option.no_picks:
                added = list(set(new_selection) - set(self.selected))
                self.selected.pop()
                self.selected += added
                self.SetCheckedItems(self.selected)
            evt.Skip()
        return
