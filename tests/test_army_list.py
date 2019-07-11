import army_list
import init
import squad

init.init("Necron")


def test_army_list():
    """
    Checks adding of simple detachments and minimum requirement units in
    different formats
    """
    army = army_list.ArmyList("Necron")
    assert army.faction == "Necron"
    army = army_list.ArmyList("Tau")
    assert army.faction == "Tau"
    return


def test_add_detachment():
    """Checks that combinations of inputs create valid detachments"""
    detach = army_list.Detachment("Patrol")
    army = army_list.ArmyList("Necron")
    army.add_detachment(detach)
    assert army.cp == 0

    detach = army_list.Detachment("Battalion")
    army.add_detachment(detach)
    assert army.cp == 5

    for detach, type in zip(army.detachments, ["Patrol", "Battalion"]):
        assert detach.type == type

    try:
        detach = army_list.Detachment("ERROR")
        raise RuntimeError("Should have raised an error by this point")
    except KeyError:
        pass
    return


def test_auto_naming():
    """Checks the automatic numbering of repeated detachment types"""
    army = army_list.ArmyList("Necron")
    detach1 = army_list.Detachment("Patrol")
    detach2 = army_list.Detachment("Patrol")
    detach3 = army_list.Detachment("Patrol")
    army.add_detachment(detach1)
    army.add_detachment(detach2)
    army.add_detachment(detach3)
    for i in range(len(army.detachments)):
        print(army.detachments[i])
        assert army.detachments[i].name == "Patrol {}".format(i + 1)
    assert army.detachment_names == ['Patrol 1', 'Patrol 2', 'Patrol 3']
    return


def test_add_unit_prog_input():
    """Checks adding a unit from programmers input for default option"""
    detach = army_list.Detachment("Patrol")
    unit = squad.Unit("Triarch Stalker", "Elites")
    detach.add_unit(unit)
    stalker = detach.units_dict["Elites"][0]
    assert stalker.name == "Triarch Stalker"
    assert stalker.pts == 171
    assert set(stalker.wargear) == set([init.WargearItem("Heat ray"),
                                        init.WargearItem("Massive forelimbs")])
    return
