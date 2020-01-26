import pytest
from ..src import menus
from ..src import player
from ..src import factory
from ..src import config

States = config.States

@pytest.fixture
def hero():
    return player.get_hero()


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


def test_inv_options__SHOW_INV__empty_inv():
    hero = player.Player()
    header, options = menus.inv_options(hero, States.SHOW_INV)

    assert header == 'Press the key next to an item to use it, or ESC to cancel.\n'
    assert options == ['Inventory is empty.']


def test_inv_options__SHOW_INV__msg(hero):
    header, options = menus.inv_options(hero, States.SHOW_INV)
    assert header == 'Press the key next to an item to use it, or ESC to cancel.\n'


def test_inv_options__SHOW_INV__main_hand_equipped(hero):
    potion = factory.mk_entity('healing_potion', x=0, y=0)
    hero.inv.add_item(potion)

    header, options = menus.inv_options(hero, States.SHOW_INV)
    assert options == [
        '(a) Dagger (on main hand)',
        '(b) Healing potion'
    ]


def test_inv_options__SHOW_INV__both_hands_equipped(hero):
    shield = factory.mk_entity('shield', x=0, y=0)
    hero.inv.add_item(shield)
    hero.equipment.toggle_equip(shield)

    header, options = menus.inv_options(hero, States.SHOW_INV)

    assert options == [
        '(a) Dagger (on main hand)',
        '(b) Shield (on off hand)'
    ]


def test_inv_options__DROP_INV__empty_inv():
    hero = player.Player()
    header, options = menus.inv_options(hero, States.DROP_INV)

    assert header == 'Press the key next to an item to drop it, or ESC to cancel.\n'
    assert options == ['Inventory is empty.']


def test_inv_options__DROP_INV__msg(hero):
    header, options = menus.inv_options(hero, States.DROP_INV)
    assert header == 'Press the key next to an item to drop it, or ESC to cancel.\n'


def test_inv_options__DROP_INV__main_hand_equipped(hero):
    potion = factory.mk_entity('healing_potion', x=0, y=0)
    hero.inv.add_item(potion)

    header, options = menus.inv_options(hero, States.DROP_INV)
    assert options == [
        '(a) Dagger (on main hand)',
        '(b) Healing potion'
    ]


def test_inv_options__DROP_INV__both_hands_equipped(hero):
    shield = factory.mk_entity('shield', x=0, y=0)
    hero.inv.add_item(shield)
    hero.equipment.toggle_equip(shield)

    header, options = menus.inv_options(hero, States.DROP_INV)

    assert options == [
        '(a) Dagger (on main hand)',
        '(b) Shield (on off hand)'
    ]


def test_hero_info(hero):
    results = menus.hero_info(hero)

    assert len(results) == 7
    assert results[0] == 'Character Information'
    assert results[1] == 'Level: {}'.format(hero.lvl.current_lvl)
    assert results[2] == 'Experience: {}'.format(hero.lvl.current_xp)
    assert results[3] == 'Experience to Level: {}'.format(hero.lvl.xp_to_next_lvl)
    assert results[4] == 'Maximum HP: {}'.format(hero.fighter.max_hp)
    assert results[5] == 'Attack: {}'.format(hero.fighter.power)
    assert results[6] == 'Defense: {}'.format(hero.fighter.defense)


def test_main_menu_options():
    result = menus.main_menu_options()
    assert len(result) == 4
    assert result == [
        '(n) New game',
        '(c) Continue last game',
        '(o) Options',
        '(q) Quit'
    ]
