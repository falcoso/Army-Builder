import main
import init
import unit_class

init.init("Necron")

def test_army_list():
    """
    Checks adding of simple detachments and minimum requirement units in
    different formats
    """
    army = main.ArmyList("Necron")
    assert army.faction == "Necron"
    army = main.ArmyList("Tau")
    assert army.faction == "Tau"
    return


def test_add_detachment():
    """Checks that combinations of inputs create valid detachments"""
    detach = main.Detachment("Patrol")
    army = main.ArmyList("Necron")
    army.add_detachment(detach)
    assert army.cp == 0

    detach = main.Detachment("Battalion")
    army.add_detachment(detach)
    assert army.cp == 5

    for detach, type in zip(army.detachments, ["Patrol", "Battalion"]):
        assert detach.type == type

    try:
        detach = main.Detachment("ERROR")
        raise RuntimeError("Should have raised an error by this point")
    except KeyError:
        pass
    return


def test_auto_naming():
    """Checks the automatic numbering of repeated detachment types"""
    army = main.ArmyList("Necron")
    detach1 = main.Detachment("Patrol")
    detach2 = main.Detachment("Patrol")
    detach3 = main.Detachment("Patrol")
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
    detach = main.Detachment("Patrol")
    unit = unit_class.Unit("Triarch Stalker", "Elites")
    detach.add_unit(unit)
    stalker = detach.units_dict["Elites"][0]
    assert stalker.name == "Triarch Stalker"
    assert stalker.pts == 171
    assert stalker.get_wargear() == set([init.WargearItem("Heat ray"),
                                         init.WargearItem("Massive forelimbs")])
    return


# def test_detachment_rename():
#     """Checks renaming method for detachment"""
#     mock_input = ["A1", "1"]
#     main.input = lambda s: mock_input.pop(0)
#     detach = main.Detachment("Patrol")
#     detach.rename("Test Name", True)
#     assert detach.name != detach.type
#     assert detach.default_name is False
#     assert detach.name == "Test Name"
#     return
