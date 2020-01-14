import pytest
from ..src import components
from ..src import config
from ..src import factory
from ..src import player

@pytest.fixture
def hero():
    return player.get_hero()

@pytest.fixture
def orc():
    return factory.mk_entity('orc', 0, 0)


""" Tests for class Fighter(object): """


def test_Fighter_init():
    f = components.Fighter(owner=None, hp=1, defense=2, power=3, xp=0)
    assert f.owner is None
    assert f.base_max_hp == 1
    assert f.hp == 1
    assert f.base_defense == 2
    assert f.base_power == 3
    assert f.xp == 0


def test_Fighter_init__hp_lt_1_raises_exception():
    with pytest.raises(ValueError):
        components.Fighter(owner=None, hp=0, defense=2, power=3, xp=0)


def test_Fighter_init__defense_lt_0_raises_exception():
    with pytest.raises(ValueError):
        components.Fighter(owner=None, hp=1, defense=-1, power=3, xp=0)


def test_Fighter_init__power_lt_0_raises_exception():
    with pytest.raises(ValueError):
        components.Fighter(owner=None, hp=1, defense=2, power=-1, xp=0)


def test_Fighter_init__xp_lt_0_raises_exception():
    with pytest.raises(ValueError):
        components.Fighter(owner=None, hp=1, defense=2, power=3, xp=-1)


@pytest.mark.skip(reason='might be more trouble than its worth.')
def test_Fighter_init__owner_must_be_Entity():
    with pytest.raises(ValueError):
        components.Fighter(owner=None, hp=1, defense=2, power=1, xp=0)


# def test_Fighter_max_hp():
    # How to test w/o owner?
# def test_Fighter_power():
    # How to test w/o owner?
# def test_Fighter_defense():
    # How to test w/o owner?


def test_Fighter_take_dmg__reduces_hp():
    hp = 10
    f = components.Fighter(owner=None, hp=hp, defense=0, power=0, xp=0)
    f.take_dmg(1)
    assert f.hp == 9


def test_Fighter_take_dmg__negative_dmg_raises_exception():
    f = components.Fighter(owner=None, hp=10, defense=0, power=0, xp=0)
    with pytest.raises(ValueError):
        f.take_dmg(-1)


def test_Fighter_take_dmg__returns_empty_results():
    hp = 10
    f = components.Fighter(owner=None, hp=hp, defense=0, power=0, xp=0)
    result = f.take_dmg(1)
    assert not result


def test_Fighter_take_dmg__lethal_dmg_returns_dead_results():
    hp = 10
    f = components.Fighter(owner='bob', hp=hp, defense=0, power=0, xp=0)
    result = f.take_dmg(15)
    result = result.pop()  # get the dict from the list
    assert result['xp'] == 0
    assert result['dead'] == 'bob'


def test_Fighter_heal__hp_is_recovered():
    hp = 10
    f = components.Fighter(owner=None, hp=hp, defense=0, power=0, xp=0)
    f.owner = None
    f.take_dmg(1)
    f.heal(1)
    assert f.hp == hp


def test_Fighter_heal__excess_hp_doesnt_go_over_max():
    f = components.Fighter(owner=None, hp=10, defense=0, power=0, xp=0)
    f.owner = None
    f.heal(100)
    assert f.hp == f.max_hp


def test_Fighter_heal__negative_amt_raises_exception():
    f = components.Fighter(owner=None, hp=10, defense=0, power=0, xp=0)
    f.owner = None
    with pytest.raises(ValueError):
        f.heal(-1)

def test_Fighter_attack__target_takes_dmg(hero, orc):
    # unequip hero dagger
    hero.equipment.toggle_equip(hero.inv.items[0])

    dmg = hero.fighter.power - orc.fighter.defense
    expected_hp = orc.fighter.hp - dmg
    hero.fighter.attack(orc)
    assert orc.fighter.hp == expected_hp


def test_Fighter_attack__dmg_returns_results(hero, orc):
    results = hero.fighter.attack(orc)
    results = results.pop()  # Get the dict from the list
    assert len(results) == 1
    assert results['msg'] == 'Player attacks Orc!'


def test_Fighter_attack__target_doesnt_take_dmg(hero, orc):
    # unequip hero dagger
    hero.equipment.toggle_equip(hero.inv.items[0])

    hero.fighter.base_power = 1
    dmg = hero.fighter.power - orc.fighter.defense
    assert dmg == 0

    expected_hp = orc.fighter.hp
    hero.fighter.attack(orc)
    assert orc.fighter.hp == expected_hp


def test_Fighter_attack__no_dmg_returns_results(hero, orc):
    # unequip hero dagger
    hero.equipment.toggle_equip(hero.inv.items[0])

    hero.fighter.base_power = 1
    results = hero.fighter.attack(orc)
    results = results.pop()  # Get the dict from the list
    assert results['msg'] == 'Player attacks Orc... But does no damage.'


""" Tests for class ApproachingBehavior(object): """

# Requires some major mocking or testing...
# def test_ApproachingBehavior_take_turn():
# def take_ApproachingBehavior_turn(self, target, fov_map, game_map, entities):
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
# def test_ConfusedBehavior_take_turn__turns_0_returns_result(orc):
    # cb = components.ConfusedBehavior(orc.ai, num_turns=1)
    # cb.take_turn()

# def test_ConfusedBehavior_take_turn(self, target, fov_map, game_map, entities):


""" Tests for class Item(object): """


def test_Item_init__no_args():
    i = components.Item()
    assert i.use_func is None
    assert i.targeting is False
    assert i.targeting_msg is None
    assert i.func_kwargs == {}


""" Tests for class Level(object): """

def test_Level_init__no_args():
    l = components.Level()
    assert l.current_lvl == config.default_lvl
    assert l.current_xp == config.starting_xp
    assert l.lvl_up_base == config.lvl_up_base
    assert l.lvl_up_factor == config.lvl_up_factor


def test_Level_xp_to_next_lvl():
    l = components.Level()
    result = l.xp_to_next_lvl
    expected = l.lvl_up_base + l.current_lvl * l.lvl_up_factor
    assert result == expected


def test_Level_add_xp__negative_xp_raises_exception():
    l = components.Level()
    with pytest.raises(ValueError):
        l.add_xp(-1)


def test_Level_add_xp__at_threshold_returns_False():
    l = components.Level()
    xp = l.xp_to_next_lvl
    assert l.add_xp(xp) is False


def test_Level_add_xp__above_lvl_returns_True():
    l = components.Level()
    xp = l.xp_to_next_lvl + 1
    assert l.add_xp(xp) is True


def test_Level_add_xp__above_lvl_increments_lvl():
    l = components.Level()
    prev_lvl = l.current_lvl
    xp = l.xp_to_next_lvl + 1
    l.add_xp(xp)
    assert l.current_lvl == prev_lvl + 1


def test_Level_add_xp__above_lvl_reset_current_xp_with_remainder():
    l = components.Level()
    xp = l.xp_to_next_lvl + 1
    l.add_xp(xp)
    assert l.current_xp == 1


def test_Level_add_xp__below_lvl_returns_False():
    l = components.Level()
    xp = l.xp_to_next_lvl - 1
    assert l.add_xp(xp) is False


def test_Level_add_xp__below_lvl_increases_current_xp():
    l = components.Level()
    l.add_xp(1)
    assert l.current_xp == 1


""" Tests for class Equippable(object): """

def test_Equippable_init__defaults():
    eq = components.Equippable('slot')
    assert eq.slot == 'slot'
    assert eq.power_bonus == 0
    assert eq.defense_bonus == 0
    assert eq.max_hp_bonus == 0


def test_Equippable_init__None_slot_raises_exception():
    with pytest.raises(ValueError):
        components.Equippable(None)


def test_Equippable_init__negative_power_bonus_raises_exception():
    with pytest.raises(ValueError):
        components.Equippable('slot', power_bonus=-1)


def test_Equippable_init__negative_defense_bonus_raises_exception():
    with pytest.raises(ValueError):
        components.Equippable('slot', defense_bonus=-1)


def test_Equippable_init__negative_max_hp_bonus_raises_exception():
    with pytest.raises(ValueError):
        components.Equippable('slot', max_hp_bonus=-1)


""" Tests for class Equipment(object): """

def test_Equipment_init():
    e = components.Equipment()

    assert e.main_hand is None
    assert e.off_hand is None


def test_Equipment_max_hp_bonus__nothing_equipped_returns_0():
    e = components.Equipment()
    assert e.max_hp_bonus == 0


def test_Equipment_max_hp_bonus__main_hand_bonus():
    ring = factory.mk_entity('ring of hp', 0, 0)
    e = components.Equipment(main_hand=ring)
    assert e.max_hp_bonus == ring.equippable.max_hp_bonus


def test_Equipment_max_hp_bonus__off_hand_bonus():
    ring = factory.mk_entity('ring of hp', 0, 0)
    e = components.Equipment(off_hand=ring)
    assert e.max_hp_bonus == ring.equippable.max_hp_bonus


def test_Equipment_max_hp_bonus__both_hands_bonus():
    ring = factory.mk_entity('ring of hp', 0, 0)
    e = components.Equipment(main_hand=ring, off_hand=ring)
    assert e.max_hp_bonus == ring.equippable.max_hp_bonus * 2


def test_Equipment_power_bonus__nothing_equipped_returns_0():
    e = components.Equipment()
    assert e.power_bonus == 0


def test_Equipment_power_bonus__main_hand_bonus():
    sword = factory.mk_entity('sword', 0, 0)
    e = components.Equipment(main_hand=sword)
    assert e.power_bonus == sword.equippable.power_bonus


def test_Equipment_power_bonus__off_hand_bonus():
    sword = factory.mk_entity('sword', 0, 0)
    e = components.Equipment(off_hand=sword)
    assert e.power_bonus == sword.equippable.power_bonus


def test_Equipment_power_bonus__both_hands_bonus():
    sword = factory.mk_entity('sword', 0, 0)
    e = components.Equipment(main_hand=sword, off_hand=sword)
    assert e.power_bonus == sword.equippable.power_bonus * 2


def test_Equipment_defense_bonus__nothing_equipped_returns_0():
    e = components.Equipment()
    assert e.defense_bonus == 0


def test_Equipment_defense_bonus__main_hand_bonus():
    shield = factory.mk_entity('shield', 0, 0)
    e = components.Equipment(main_hand=shield)
    assert e.defense_bonus == shield.equippable.defense_bonus


def test_Equipment_defense_bonus__off_hand_bonus():
    shield = factory.mk_entity('shield', 0, 0)
    e = components.Equipment(off_hand=shield)
    assert e.defense_bonus == shield.equippable.defense_bonus


def test_Equipment_defense_bonus__both_hands_bonus():
    shield = factory.mk_entity('shield', 0, 0)
    e = components.Equipment(main_hand=shield, off_hand=shield)
    assert e.defense_bonus == shield.equippable.defense_bonus * 2


def test_Equipment_toggle_equip__nothing_equipped():
    shield = factory.mk_entity('shield', 0, 0)
    e = components.Equipment()
    results = e.toggle_equip(shield)

    # Nothing equipped - equipping returns the slot
    assert results == [{'equipped': e.off_hand}]


def test_Equipment_toggle_equip__unequips_item():
    shield = factory.mk_entity('shield', 0, 0)
    e = components.Equipment(off_hand=shield)
    results = e.toggle_equip(shield)

    # Dequipping an item returns the item
    assert results == [{'dequipped': shield}]
