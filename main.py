import wx

import army_list
import squad
import init

from gui.gui import HomeFrame

if __name__ == "__main__":
    init.init("Necron")
    army = army_list.ArmyList("./test_army.army", True)

    # fire up the gui
    app = wx.App()
    gui = HomeFrame(army, None, wx.ID_ANY, "")
    gui.Show(True)
    app.MainLoop()
