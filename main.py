import wx

import army_list
import squad
import init

from gui.gui import HomeFrame

if __name__ == "__main__":
    init.init("Necron")
    # army = army_list.ArmyList("./test_army.army", True)
    army = army_list.ArmyList("Necron")
    detach = army_list.Detachment("Patrol")

    units = [("Necron Warriors", "Troops"),
             ("Immortals", "Troops"),
             ("Overlord", "HQ")]
    for unit in units:
        unit = squad.Unit(*unit)
        detach.add_unit(unit)

    army.add_detachment(detach)
    print(army.save("./test_army.army"))

    # fire up the gui
    app = wx.App()
    gui = HomeFrame(army, None, wx.ID_ANY, "")
    gui.Show(True)
    app.MainLoop()
