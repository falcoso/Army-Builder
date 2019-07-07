import wx
import sys
from wx.lib.scrolledpanel import ScrolledPanel

sys.path.append('../')
import squad


class EditPanel(ScrolledPanel):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.unit = None
        self.InitUI()
        self.SetScrollRate(0, 10)
        self.SetSizer(self.sizer)
        self.Fit()

    def InitUI(self):
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
                self.modList.Add(model_txt, 1, wx.ALL, 1)
                self.modList.Add(size_ctrl, 1, wx.ALL, 1)

            self.models_box.Add(self.modList)
            self.sizer.Add(self.models_box)

        # create options box
        if self.unit.options is not None:
            self.options_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Options")
            if self.unit.parser.options_list == []:
                for option in self.unit.options:
                    self.unit.parser.parse2(option)

            for option in self.unit.parser.options_list:
                chk_list = [i.__repr__(tidy=True) for i in option.items_involved]
                option_chkbx = wx.CheckListBox(self, choices=chk_list)
                self.options_box.Add(option_chkbx, 0, wx.FIXED_MINSIZE, 0)

            self.sizer.Add(self.options_box, 0, wx.EXPAND, 0)
        self.Fit()
        self.Layout()
        return

    def set_unit(self, unit):
        self.unit = unit
        self.InitUI()
        return
