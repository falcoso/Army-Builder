import wx
import sys
import numpy as np
from wx.lib.scrolledpanel import ScrolledPanel

sys.path.append('../')
import init


class EditPanel(ScrolledPanel):
    """
    Class inherited from wx.lib.scrolledpanel.ScrolledPanel to generate all
    parameters and options associated with a selected unit.

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
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.unit = None
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
            self.sizing_box = SizingBox(self.unit, parent=self)
            self.sizer.Add(self.sizing_box)

        # create options box
        if self.unit.options is not None:
            self.option_pane = OptionBox(self.unit, parent=self)
            self.sizer.Add(self.option_pane)

        self.Layout()
        return

    def set_unit(self, unit):
        """Sets the unit for the panel and re-generates widgets."""
        self.unit = unit
        self.DestroyChildren()
        self.__InitUI()
        return


class OptionBox(wx.Panel):
    def __init__(self, unit, *args, **kw):
        super(OptionBox, self).__init__(*args, **kw)
        self.unit = unit
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
            self.options_box.Add(option_txt, 0, wx.ALL, 5)
            self.options_box.Add(option_chkbx, 0, wx.EXPAND, 5)
            name += 1
        self.Bind(wx.EVT_CHECKLISTBOX, self.on_choice)
        self.SetSizer(self.options_box)
        self.Fit()


    def on_choice(self, evt):
        """Event handler for wx.CheckBoxList choice."""
        option = evt.GetEventObject().option
        self.unit.change_wargear([option])
        evt.Skip()


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
    option : option_parser.Option
        Option for which the CheckBox has been created
    """

    def __init__(self, option, wargear, *args, **kw):
        chk_list = [i.__repr__(tidy=True) for i in option.items_involved]

        super(OptionCheckBox, self).__init__(*args, choices=chk_list, **kw)
        self.option = option
        self.Bind(wx.EVT_CHECKLISTBOX, self.__on_choice)
        self.SetCheckedOptions(wargear)
        return

    def SetCheckedStrings(self, strings):
        super().SetCheckedStrings(strings)
        self.option.select_list(list(super().GetCheckedItems()))
        return

    def SetCheckedItems(self, items):
        super().SetCheckedItems(items)
        self.option.select_list(list(super().GetCheckedItems()))
        return

    def SetCheckedOptions(self, wargear):
        chkd_str = []
        for item in wargear:
            if item in self.option.items_involved:
                chkd_str.append(item.__repr__(tidy=True))
        self.__handle_evt = False
        self.SetCheckedStrings(chkd_str)
        self.__handle_evt = True

    def __on_choice(self, evt):
        if self.__handle_evt:
            self.__handle_evt = False
            new_selection = super().GetCheckedItems()
            new_selection = [self.option.items_involved[i] for i in new_selection]

            # more than allowed choices chosen
            if len(new_selection) > self.option.no_picks:
                new_selection = list(set(new_selection) - set(self.option.selected))
                # remove oldest added and add new one
                self.option.selected.pop(0)
                self.option.select(new_selection[0])
                # update selections to max number of choices
                self.SetCheckedOptions(self.option.selected)
            else:
                self.SetCheckedOptions(new_selection)
            self.__handle_evt = True
            evt.Skip()
        return


class SizingBox(wx.Panel):
    """
    Class inherited from wx.Panel to generate all sizing options for the given
    unit.

    Parameters
    ----------
    unit : squad.Unit
        Unit for which the panel is generated.

    *args : wx.Panel arguments
    **kw : wx.Panel keyword arguments

    Attributes
    ----------
    unit : squad.Unit
        Unit for which the panel is generated.
    model_ctrls : list (wx.<>Ctrl)
        List of controls for each model in the unit
    models_box : wx.StaticBoxSizer
        Main sizer for the Panel
    modList : wx.FlexGridSizer

    Public Methods
    --------------
    on_size(self, evt): Event handler for wx.SpinCtrl change.
    """

    def __init__(self, unit, *args, **kw):
        super(SizingBox, self).__init__(*args, **kw)
        self.unit = unit
        self.model_ctrls = []

        self.models_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Models")
        self.modList = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)

        # create widgets for each possible model
        for model in self.unit.mod_str:
            txt = wx.StaticText(self, wx.ID_ANY, model)

            # get the no of models if the exist in the unit already
            size = 0
            for i in self.unit.models:
                # search through the models for the size if they exist
                if i.label == model:
                    size = i.size
                    break

            # if only 1 allowed per unit, make a checkbox, otherwise spinctrl
            if init.models_dict[model]["no_per_unit"] == 1:
                size_ctrl = wx.CheckBox(self)
                size_ctrl.SetValue(size)
            else:
                size_ctrl = wx.SpinCtrl(self, wx.ID_ANY, str(size),
                                        name=model)

                # set limits on spinctrl
                if init.models_dict[model]["no_per_unit"] is None:
                    size_ctrl.SetRange(*self.unit.size_range)
                else:
                    size_ctrl.SetRange(0, init.models_dict[model]["no_per_unit"])

            self.model_ctrls.append(size_ctrl)

            self.modList.Add(txt, 1, wx.ALL, 1)
            self.modList.Add(size_ctrl, 1, wx.ALL, 1)

        self.Bind(wx.EVT_CHECKBOX, self.on_size)
        self.Bind(wx.EVT_SPINCTRL, self.on_size)
        self.models_box.Add(self.modList)
        self.SetSizer(self.models_box)
        self.Fit()

    def on_size(self, evt):
        """Event handler for wx.SpinCtrl change."""
        size = np.array([int(i.GetValue()) for i in self.model_ctrls])

        # change the spin limits on the default model
        self.model_ctrls[0].SetMax(self.unit.size_range[1]-size[1:].sum())
        self.model_ctrls[0].SetMin(self.unit.size_range[0]-size[1:].sum())

        # update again incase the sizes are reduced
        size = np.array([int(i.GetValue()) for i in self.model_ctrls])

        self.unit.re_size(*size)
        evt.Skip()
        return
