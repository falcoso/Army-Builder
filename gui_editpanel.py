import wx
from wx.lib.scrolledpanel import ScrolledPanel

class EditPanel(ScrolledPanel):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.unit = None
        self.InitUI()
        self.SetScrollRate(0, 10)

    def InitUI(self):
        if self.unit is None:
            return

        return
