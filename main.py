import wx
import copy

import army_list
import squad
import init

from gui.gui import HomeFrame

if __name__ == "__main__":
    # mock army for initial testing
    init.init("Necron")
    army = army_list.ArmyList("Necron")
    detach = army_list.Detachment("Patrol")
    unit = squad.Unit("Necron Warriors", "Troops")
    detach.add_unit(unit)
    unit1 = squad.Unit("Immortals", "Troops")
    detach.add_unit(unit1)
    unit2 = squad.Unit("Overlord", "HQ")
    detach.add_unit(unit2)
    army.add_detachment(detach)
    print(army)

    # fire up the gui
    app = wx.App()
    gui = HomeFrame(army, None, wx.ID_ANY, "")
    gui.Show(True)
    app.MainLoop()
