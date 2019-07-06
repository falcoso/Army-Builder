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
        self.models_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Models")
        if self.unit.mod_str is None:
            self.modList = wx.BoxSizer(wx.HORIZONTAL)
            model_txt = wx.StaticText(self, wx.ID_ANY, self.unit.type)
            size_ctrl = wx.SpinCtrl(self, wx.ID_ANY, str(self.unit.get_size()),
                                    name=self.unit.type)
            self.modList.Add(model_txt, 1, wx.ALL, 1)
            self.modList.Add(size_ctrl, 1, wx.ALL, 1)

        else:
            self.modList = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
            for model in self.unit.mod_str:
                txt = wx.StaticText(self, wx.ID_any, model)
                size = 0
                for i in self.unit.models:
                    if i.label == model:
                        size = i.no_models
                        break

                size_ctrl = wx.SpinCtrl(self, wx.ID_ANY, str(size), name=model)

                self.modList.Add(txt, 1, wx.ALL, 1)
                self.modList.Add(size_ctrl, 1, wx.ALL, 1)

        self.models_box.Add(self.modList)
        self.sizer.Add(self.title)
        self.sizer.Add(self.models_box)
        self.Fit()
        self.Layout()
        return

    def set_unit(self, unit):
        self.unit = unit
        self.InitUI()
        return
