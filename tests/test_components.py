import pytest
from ..src import components

""" Tests for class Fighter(object): """

def test_init():
    f = components.Fighter(hp=1, defense=2, power=3, xp=0)
    assert f.base_max_hp == 1
    assert f.hp == 1
    assert f.base_defense == 2
    assert f.base_power == 3
    assert f.xp == 0


def test_init__hp_lt_1_raises_exception():
    with pytest.raises(ValueError):
        components.Fighter(hp=0, defense=2, power=3, xp=0)


def test_init__defense_lt_0_raises_exception():
    with pytest.raises(ValueError):
        components.Fighter(hp=1, defense=-1, power=3, xp=0)


def test_init__power_lt_0_raises_exception():
    with pytest.raises(ValueError):
        components.Fighter(hp=1, defense=2, power=-1, xp=0)


def test_init__xp_lt_0_raises_exception():
    with pytest.raises(ValueError):
        components.Fighter(hp=1, defense=2, power=3, xp=-1)


# def test_max_hp():
# def test_power():
# def test_defense():
# def test_take_dmg():
# def test_heal():
# def test_attack():


""" Tests for class ApproachingBehavior(object): """

# def test_take_turn():

""" Tests for class ConfusedBehavior(object): """

# def test_init_():
# def test_take_turn():

""" Tests for class Item(object): """

# def test_init_():

""" Tests for class Level(object): """

# def test_init_():
# def test_xp_to_next_lvl():
# def test_add_xp():


""" Tests for class Equippable(object): """

# def test_init():


""" Tests for class Equipment(object): """

# def test_init():
# def test_max_hp_bonus():
# def test_power_bonus():
# def test_defense_bonus():
# def test_toggle_equip():
