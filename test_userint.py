import pytest

import userint
import unit_class
import init


@pytest.fixture
def ui_setup():
    mock_input = ["Tau", "Patrol", "A1", "1", "1 5"]
    userint.input = lambda x: mock_input.pop(0)
    interface = userint.UI()
    return interface


def test_ui_init(ui_setup):
    """Tests the initialisation of the User Interface"""
    interface = ui_setup
    detach = interface.army.detachments[0]
    assert detach.type == "Patrol"
    breachers = unit_class.Unit("Breacher Team", "Troops")
    assert detach.units_dict["HQ"][0] == unit_class.Unit("Aun'Shi", "HQ")
    breachers.re_size((1, 5))
    assert detach.units_dict["Troops"][0] == breachers


def test_add_detachment(ui_setup):
    """Tests that a single detachment can be added to the army"""
    interface = ui_setup
    mock_input = ["2",
                  "Longstrike",  # HQ 1
                  "3",  # False input
                  "Hello",  # False Input
                  "B2",  # Crisis Commander
                  "2",  # Strike Team
                  "bip",  # size strike team
                  "1,9 0",
                  "b2",  # False Input
                  "1",  # Breacher Team
                  "1 5",  # Sizing Breacher Team
                  "Kroot Carnivores"]

    userint.input = lambda x: mock_input.pop(0)
    interface.add_detachment()
    detach = interface.army.detachments[1]
    assert detach.units_dict["HQ"][0] == unit_class.Unit("Longstrike", "HQ")
    assert detach.units_dict["HQ"][1] == unit_class.Unit("Commander in XV8 Crisis Battlesuit", "HQ")
    breachers = unit_class.Unit("Strike Team", "Troops")
    breachers.re_size((1, 9, 0))
    assert detach.units_dict["Troops"][0] == breachers
    breachers = unit_class.Unit("Breacher Team", "Troops")
    breachers.re_size((1, 5))
    assert detach.units_dict["Troops"][1] == breachers
    breachers = unit_class.Unit("Kroot Carnivores", "Troops")
    assert detach.units_dict["Troops"][2] == breachers
    return


def test_add_multiplte_detachments(ui_setup):
    """Tests that multiple detachments can be added at once to the army"""
    interface = ui_setup
    mock_input = ["2, 1",
                  "Longstrike",  # HQ 1
                  "B2",  # Crisis Commander
                  "2",  # Strike Team
                  "bip",  # size strike team
                  "1,9 0",
                  "1",  # Breacher Team
                  "1 5",  # Sizing Breacher Team
                  "Kroot Carnivores",
                  "Commander in XV85 Enforcer Battlesuit",
                  "Kroot Carnivores"]

    userint.input = lambda x: mock_input.pop(0)
    interface.add_detachment()
    print(interface.army)
    detach = interface.army.detachments[1]
    assert detach.units_dict["HQ"][0] == unit_class.Unit("Longstrike", "HQ")
    assert detach.units_dict["HQ"][1] == unit_class.Unit("Commander in XV8 Crisis Battlesuit", "HQ")
    breachers = unit_class.Unit("Strike Team", "Troops")
    breachers.re_size((1, 9, 0))
    assert detach.units_dict["Troops"][0] == breachers
    breachers = unit_class.Unit("Breacher Team", "Troops")
    breachers.re_size((1, 5))
    assert detach.units_dict["Troops"][1] == breachers
    breachers = unit_class.Unit("Kroot Carnivores", "Troops")
    assert detach.units_dict["Troops"][2] == breachers

    detach = interface.army.detachments[2]
    assert detach.units_dict["HQ"][0] == unit_class.Unit(
        "Commander in XV85 Enforcer Battlesuit", "HQ")
    assert detach.units_dict["Troops"] == [unit_class.Unit("Kroot Carnivores", "Troops")]
    return


def test_add_unit(ui_setup):
    """Tests that a single unit can be added to an existing detachment"""
    interface = ui_setup
    mock_input = ["0",  # False inputs
                  "Hello",  # False inputs
                  "1",  # Select Patrol
                  "Elites",
                  "8",  # Stealth Suits
                  "1.3"]  # Size Stealth Suits
    userint.input = lambda x: mock_input.pop(0)
    interface.add_unit()
    suits = unit_class.Unit("XV25 Stealth Battlesuit", "Elites")
    suits.re_size((1, 3))
    assert interface.army.detachments[0].units_dict["Elites"][0] == suits
    return


def test_change_wargear(ui_setup):
    interface = ui_setup
    mock_input = ["1",  # Select Patrol
                  "Elites",
                  "7"]  # Riptide
    userint.input = lambda x: mock_input.pop(0)
    interface.add_unit()  # add changeable unit

    mock_input = ["1",
                  "Elites",
                  "Hello",  # False input
                  "1",
                  "1a 2b 3a, 3c"]
    userint.input = lambda x: mock_input.pop(0)
    interface.change_unit_wargear()
    riptide = interface.army.detachments[0].units_dict["Elites"][0]
    print(riptide)
    wargear_added = [init.WargearItem("2*Smart missile system"),
                     init.WargearItem("Ion accelerator"),
                     init.WargearItem("Greater advanced targeting system"),
                     init.WargearItem("Drone controller")]
    for i in wargear_added:
        assert i in riptide.wargear

    assert len(wargear_added) == len(riptide.wargear)
