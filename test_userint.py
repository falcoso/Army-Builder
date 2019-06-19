import pytest

import userint
import unit_class

@pytest.fixture
def ui_setup():
    mock_input = ["Tau", "Patrol", "A1", "1", "1 5"]
    userint.input = lambda x: mock_input.pop(0)
    interface = userint.UI()
    return interface

def test_ui_init(ui_setup):
    interface = ui_setup
    detach = interface.army.detachments[0]
    assert detach.type == "Patrol"
    breachers = unit_class.Unit("Breacher Team", "Troops")
    assert detach.units_dict["HQ"][0] == unit_class.Unit("Aun'Shi", "HQ")
    breachers.re_size((1,5))
    assert detach.units_dict["Troops"][0] == breachers
