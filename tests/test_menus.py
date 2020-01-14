from ..src import menus


def test_default_lettering_dict__no_items():
    items = []
    result = menus.default_lettering_dict(items)

    assert result == {}


def test_default_lettering_dict__one_item():
    items = ['dinglebop']
    result = menus.default_lettering_dict(items)

    assert result == {'a': 'dinglebop'}


def test_default_lettering_dict__two_items():
    items = ['dinglebop', 'schmuff']
    result = menus.default_lettering_dict(items)

    assert result == {'a': 'dinglebop', 'b': 'schmuff'}


def test_lvl_up_options():
    header, options = menus.lvl_up_options()
    assert header == 'Level up! Choose a stat to raise:'
    assert options['h'] == 'Hit Points (+20 HP)'
    assert options['s'] == 'Strength (+1 attack)'
    assert options['d'] == 'Defense (+1 defense)'


# def test_inv_options():

# def test_hero_info():

# def test_main_menu_options():

