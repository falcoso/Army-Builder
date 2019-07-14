import init
import option_parser

import pytest
import json


def test_units_dict():
    """Checks the points calculations for the units dict"""
    detachments_dict, armoury_dict, units_dict = init.init("Necron")
    with open("./resources/Necron/Units.json", 'r') as file:
        units = json.load(file)

    # check that points for wargear are being added
    assert units["Elites"]["Lychguard"]["base_pts"] != units_dict["Elites"]["Lychguard"]["pts"]
    return


def test_units_dict_wargear():
    """
    Checks spelling of the options in the units_dict by creating a unit for
    each one.
    """
    parser = option_parser.OptionParser()
    parser.build()
    for faction in ["Tau", "Necron"]:
        detachments_dict, armoury_dict, units_dict = init.init(faction)
        for foc, units in units_dict.items():
            for key, unit in units.items():
                if unit["options"] is not None:
                    for i in unit["options"]:
                        parser.parse2(i)
    return


def test_init_WargearItem():
    """Checks that items can be created properly"""
    for cat, wargear_list in init.armoury_dict.items():
        for i in wargear_list:
            item = init.WargearItem(i)

def test_mult_WargearItem():
    """Checks multiplication and set_no_of() work."""
    item = init.WargearItem("Gauss blaster")
    assert item.pts == 9
    item *= 2
    assert item.pts == 18
    assert item.no_of == 2

    item.set_no_of(5)
    assert item.pts == 5*9
    assert item.no_of == 5
    try:
        item = item*item
        raise AssertionError("Error should have raised by now")
    except TypeError:
        pass
    return

def test_init_MultipleItem():
    """Checks that init.MultipleItem can be created."""
    item_labels = ["Hyperphase sword", "Dispersion shield"]
    item = init.MultipleItem(*item_labels)
    assert item.pts == 15
    assert item.item == item_labels
    assert item.no_of == 1
    return

def test_add_WargearItem():
    """Checks add functionality between wargear items behaves as desired."""
    sword = init.WargearItem("Hyperphase sword")
    shield = init.WargearItem("Dispersion shield")
    combined = sword + shield

    assert combined.pts == 15
    assert combined.item == ["Hyperphase sword", "Dispersion shield"]
    assert combined.no_of == 1

    blaster = init.WargearItem("Gauss blaster")
    combined += blaster
    assert combined.pts == 15 +9
    assert combined.item == ["Hyperphase sword", "Dispersion shield",
                             "Gauss blaster"]
    assert combined.no_of == 1
    return

def test_save_WargearItem():
    item = init.WargearItem("Gauss blaster")
    item *= 2
    assert item.save() == "2*Gauss blaster"
    return

def test_save_MultiplItem():
    item_labels = ["Hyperphase sword", "Dispersion shield"]
    item = init.MultipleItem(*item_labels)
    assert item.save() ==  "Hyperphase sword+Dispersion shield"
    return
