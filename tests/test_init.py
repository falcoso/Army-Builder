import init
import option_parser

import pytest
import json


def test_units_dict():
    """Checks the points calculations for the units dict"""
    detachments_dict, armoury_dict, units_dict = init.init("Necron")
    with open("Necron/Units.json", 'r') as file:
        units = json.load(file)

    # check that points for wargear are being added
    assert units["Elites"]["Lychguard"]["base_pts"] != units_dict["Elites"]["Lychguard"].pts
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
                if unit.options is not None:
                    for i in unit.options:
                        parser.parse2(i)
    return


def test_WargearItem():
    """Checks that items can be created properly"""
    for cat, wargear_list in init.armoury_dict.items():
        for i in wargear_list:
            item = init.WargearItem(i)
