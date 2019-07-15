import pytest
import init
import option_parser


def test_units_dict_options():
    """
    Parses all the options in the units pict to check that they run without
    error. Similar to the test_units_dict() in test_init but parses the option
    strings directly rather than through the main module.
    """
    # create parser
    parser = option_parser.OptionParser()
    parser.build()

    for faction in ["Tau", "Necron"]:
        detachments_dict, armoury_dict, units_dict = init.init(faction)
        for foc, units in units_dict.items():
            for title, i in units.items():
                if i["options"] is None:
                    continue

                try:
                    parser.parse2(i["options"])
                except Exception as e:
                    raise ValueError('Error in {}:{}'.format(title, str(e)))
    return


def test_Option_class():
    """
    Checks list facilities in the Options class and that the object can be
    inialised successfully
    """
    init.init("Necron")
    item_list = [init.WargearItem("Tesla carbine"),
                 init.WargearItem("Gauss cannon"),
                 init.WargearItem("Gauss blaster")]
    option = option_parser.Option(item_list)
    assert item_list[1] == option[1]
    for i, j in enumerate(option):
        assert j == item_list[i]
