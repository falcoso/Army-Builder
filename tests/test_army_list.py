import pytest

import army_list
import init
import squad

init.init("Necron")


@pytest.fixture
def detach():
    detach = army_list.Detachment("Patrol")

    units = [("Necron Warriors", "Troops"),
             ("Immortals", "Troops"),
             ("Overlord", "HQ")]
    for unit in units:
        unit = squad.Unit(*unit)
        detach.add_unit(unit)
    return detach


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

def test_save_army(detach):
    army = army_list.ArmyList("Necron")
    army.add_detachment(detach)
    save = army.save("./test_army.army")
    assert save == {"faction": "Necron",
                    "detachments": [i.save() for i in army.detachments]}
    return


def test_detachment(detach):
    assert detach.pts == 299
    assert len(detach.units_dict["HQ"]) == 1
    assert len(detach.units_dict["Troops"]) == 2
    assert detach.name == "Patrol"


def test_add_unit(detach):
    """Checks adding a unit ."""
    unit = squad.Unit("Triarch Stalker", "Elites")
    detach.add_unit(unit)
    stalker = detach.units_dict["Elites"][0]
    assert stalker.name == "Triarch Stalker"
    assert stalker.pts == 171
    assert set(stalker.wargear) == set([init.WargearItem("Heat ray"),
                                        init.WargearItem("Massive forelimbs")])

    assert detach.pts == 299 + 171
    return


def test_save_detachment(detach):
    save = detach.save()
    assert save == {"type": "Patrol",
                    "name": None,
                    "units": {"HQ": [i.save() for i in detach.units_dict["HQ"]],
                              "Troops": [i.save() for i in detach.units_dict["Troops"]],
                              "Elites": [],
                              "Fast Attack": [],
                              "Heavy Support": [],
                              "Dedicated Transports": []}}
    pass
