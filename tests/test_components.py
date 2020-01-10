import pytest
import tcod
from ..src import components
from ..src import entity
from ..src import render_functions

@pytest.fixture
def hero():
    fighter_comp = components.Fighter(hp=100, defense=1, power=2)
    return entity.Entity(
        x=0, y=0,
        char='@',
        color=None,
        name='Player',
        human=True,
        equipment=None,
        fighter=fighter_comp
    )


@pytest.fixture
def orc():
    fighter_comp = components.Fighter(hp=10, defense=1, power=3, xp=35)
    ai_comp = components.ApproachingBehavior()
    return entity.Entity(
        x=0, y=0,
        char='o',
        color=tcod.desaturated_green,
        name='Orc',
        blocks=True,
        render_order=render_functions.RenderOrder.ACTOR,
        fighter=fighter_comp,
        ai=ai_comp
    )


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
    # How to test w/o owner?
# def test_power():
    # How to test w/o owner?
# def test_defense():
    # How to test w/o owner?


def test_take_dmg__reduces_hp():
    hp = 10
    f = components.Fighter(hp=hp, defense=0, power=0, xp=0)
    f.take_dmg(1)
    assert f.hp == 9


def test_take_dmg__negative_dmg_raises_exception():
    f = components.Fighter(hp=10, defense=0, power=0, xp=0)
    with pytest.raises(ValueError):
        f.take_dmg(-1)


def test_take_dmg__returns_empty_results():
    hp = 10
    f = components.Fighter(hp=hp, defense=0, power=0, xp=0)
    result = f.take_dmg(1)
    assert not result


def test_take_dmg__lethal_dmg_returns_dead_results():
    hp = 10
    f = components.Fighter(hp=hp, defense=0, power=0, xp=0)
    f.owner = 'owner'
    result = f.take_dmg(15)
    result = result.pop()  # get the dict from the list
    assert result['xp'] == 0
    assert result['dead'] == 'owner'


def test_heal__hp_is_recovered():
    hp = 10
    f = components.Fighter(hp=hp, defense=0, power=0, xp=0)
    f.owner = None
    f.take_dmg(1)
    f.heal(1)
    assert f.hp == hp


def test_heal__excess_hp_doesnt_go_over_max():
    f = components.Fighter(hp=10, defense=0, power=0, xp=0)
    f.owner = None
    f.heal(100)
    assert f.hp == f.max_hp


def test_heal__negative_amt_raises_exception():
    f = components.Fighter(hp=10, defense=0, power=0, xp=0)
    f.owner = None
    with pytest.raises(ValueError):
        f.heal(-1)

# Revamp once we figure out owner co-dependence
def test_attack__target_takes_dmg(hero, orc):
    dmg = hero.fighter.power - orc.fighter.defense
    expected_hp = orc.fighter.hp - dmg
    hero.fighter.attack(orc)
    assert orc.fighter.hp == expected_hp


def test_attack__dmg_returns_results(hero, orc):
    results = hero.fighter.attack(orc)
    results = results.pop()  # Get the dict from the list
    assert len(results) == 1
    assert results['msg'] == 'Player attacks Orc!'


def test_attack__target_doesnt_take_dmg(hero, orc):
    hero.fighter.base_power = 1
    dmg = hero.fighter.power - orc.fighter.defense
    assert dmg == 0

    expected_hp = orc.fighter.hp
    hero.fighter.attack(orc)
    assert orc.fighter.hp == expected_hp


def test_attack__no_dmg_returns_results(hero, orc):
    hero.fighter.base_power = 1
    results = hero.fighter.attack(orc)
    results = results.pop()  # Get the dict from the list
    assert results['msg'] == 'Player attacks Orc... But does no damage.'


""" Tests for class ApproachingBehavior(object): """

# Requires some major mocking or testing...
# def test_take_turn():
# def take_turn(self, target, fov_map, game_map, entities):
    # hero is usually target
    # target needs .x and .y


""" Tests for class ConfusedBehavior(object): """

def test_ConfusedBehavior_init__(orc):
    prev_ai = orc.ai
    cb = components.ConfusedBehavior(prev_ai)
    assert cb.prev_ai == prev_ai
    assert cb.num_turns == 10


def test_ConfusedBehavior_init__negative_turns_raises_exception(orc):
    with pytest.raises(ValueError):
        components.ConfusedBehavior(orc.ai, num_turns=-1)


# Requires some major mocking or testing...
# def test_take_turn__turns_0_returns_result(orc):
    # cb = components.ConfusedBehavior(orc.ai, num_turns=1)
    # cb.take_turn()

# def take_turn(self, target, fov_map, game_map, entities):

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
