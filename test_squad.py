import squad
import init
import pytest

init.init('Necron')


def test_squad():
    """Checks the attributes of the units class"""
    warriors = squad.Unit("Necron Warriors", "Troops")
    assert warriors.pts == 120
    assert warriors.wargear == [init.WargearItem("Gauss flayer")]
    return


def test_re_size_mono_model():
    """
    Checks the Unit.re_size() method for unit containing one type of model
    """
    warriors = squad.Unit("Necron Warriors", "Troops")
    warriors.re_size(15)
    # check valid input modifies the unit points
    assert warriors.pts == (warriors.models[0].pts_per_model + warriors.wargear_pts) * 15
    assert warriors.models[0].no_models == 15

    # check programmer input raises the correct errors
    warriors.re_size(10)
    assert warriors.pts == 120
    return


def test_re_size_poly_model():
    """
    Checks the Unit.test_resize() method for unist containing multiple models
    """
    # check that changes no applied to the whole unit creates a new model
    unit = squad.Unit("Destroyers", "Fast Attack")
    unit.re_size((2,1))
    assert unit.get_size() == 3
    assert unit.models[0].no_models == 2
    assert unit.models[1].wargear == [init.WargearItem("Heavy gauss cannon")]

    # check that when re-sizing and repeating the existing extra model is modified
    unit.re_size((5,1))
    assert unit.get_size() == 6
    assert unit.models[0].no_models == 5
    assert unit.models[1].wargear == [init.WargearItem("Heavy gauss cannon")]
    return


def test_change_wargear():
    """Checks the Unit.change_wargear() method"""
    unit = squad.Unit("Catacomb Command Barge", "HQ")
    unit.parser.options_list = []
    for option in unit.options:
        unit.parser.parse2(option)

    choices = [(0,1), (1,2), (2,0), (3,0)]
    wargear_to_add = []
    for choice in choices:
        sel_option = unit.parser.options_list[choice[0]]
        sel_option.select(choice[1])
        wargear_to_add.append(sel_option)
    unit.change_wargear(wargear_to_add)
    wargear_selected = [init.WargearItem("Tesla cannon"),
                        init.WargearItem("Hyperphase sword"),
                        init.WargearItem("Phylactery"),
                        init.WargearItem("Resurrection orb")]
    for i in wargear_selected:
        assert i in unit.wargear


def test_reset():
    """
    Checks the Unit.reset() method returns the Unit back to its initial state
    """
    mock_input = ["1b", 'no', 'y']
    squad.input = lambda s: mock_input.pop(0)
    unit = squad.Unit("Immortals", "Troops")
    unit_copy = squad.Unit("Immortals", "Troops")

    unit.parser.options_list = []
    for option in unit.options:
        unit.parser.parse2(option)

    unit.re_size(10)
    sel_option = unit.parser.options_list[0]
    sel_option.select(1)
    unit.change_wargear([sel_option])  # input = '1b'

    assert unit_copy.get_size() != unit.get_size()
    assert unit_copy.wargear != unit.wargear

    # input = 'y'
    unit.reset()
    assert unit_copy.get_size() == unit.get_size()
    assert unit_copy.wargear == unit.wargear


def test_check_validity():
    """
    Checks the Unit.check_validty method highlights errors in the unit
    """
    unit = squad.Unit("Destroyers", "Fast Attack")
    unit.re_size((5,5))
    assert unit.check_validity() is False  # initial state too big and too many Heavy Destroyers

    unit.re_size((4,2))  # right size too many Heavy Destroyers
    assert unit.check_validity() is False

    unit.re_size((5, 1))  # Valid unit
    assert unit.check_validity() is True
