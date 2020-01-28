import pytest
from ..src import components
from ..src import config
from ..src import entity
from ..src import factory
from ..src import player

Slots = config.Slots

@pytest.fixture
def hero():
    return player.get_hero()


@pytest.fixture
def orc():
    return factory.mk_entity('orc', 0, 0)


@pytest.fixture
def sword():
    return factory.mk_entity('sword', 0, 0)


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


""" Tests for class ApproachAI(object): """

# Requires some major mocking or testing...
# def test_ApproachAI():
# def take_ApproachAI_turn(self, target, fov_map, game_map, entities):
    # hero is usually target
    # target needs .x and .y


""" Tests for class ConfusedBehavior(object): """

def test_ConfusedBehavior_init__(orc):
    prev_ai = orc.ai
    cb = components.ConfusedBehavior(owner=None, prev_ai=prev_ai)
    assert cb.prev_ai == prev_ai
    assert cb.num_turns == 10


def test_ConfusedBehavior_init__negative_turns_raises_exception(orc):
    with pytest.raises(ValueError):
        components.ConfusedBehavior(owner=None, prev_ai=orc.ai, num_turns=-1)


# Requires some major mocking or testing...
# def test_ConfusedBehavior_take_turn__turns_0_returns_result(orc):
    # cb = components.ConfusedBehavior(orc.ai, num_turns=1)
    # cb.take_turn()

# def test_ConfusedBehavior_take_turn(self, target, fov_map, game_map, entities):


""" Tests for class Item(object): """


@pytest.mark.skip(reason='lazy')
def test_Item_init__owner_is_none_raises_exception():
    pass

def test_Item_init__no_args():
    i = components.Item(owner=None)
    assert i.owner is None
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


@pytest.mark.skip(reason='lazy')
def test_Equippable_init__owner_is_none_raises_exception():
    pass


def test_Equippable_init__defaults():
    eq = components.Equippable(owner=None, slot='slot')

    assert eq.owner is None
    assert eq.slot == 'slot'
    assert eq.power_bonus == 0
    assert eq.defense_bonus == 0
    assert eq.max_hp_bonus == 0


def test_Equippable_init__None_slot_raises_exception():
    with pytest.raises(ValueError):
        components.Equippable(owner=None, slot=None)


def test_Equippable_init__negative_power_bonus_raises_exception():
    with pytest.raises(ValueError):
        components.Equippable(owner=None, slot='slot', power_bonus=-1)


def test_Equippable_init__negative_defense_bonus_raises_exception():
    with pytest.raises(ValueError):
        components.Equippable(owner=None, slot='slot', defense_bonus=-1)


def test_Equippable_init__negative_max_hp_bonus_raises_exception():
    with pytest.raises(ValueError):
        components.Equippable(owner=None, slot='slot', max_hp_bonus=-1)


""" Tests for class Equipment(object): """

def test_Equipment_init():
    e = components.Equipment()
    assert len(e.slots) == len(config.Slots)
    assert all(True for slot in config.Slots if slot in e.slots)


def test_Equipment_max_hp_bonus__nothing_equipped_returns_0():
    e = components.Equipment()
    assert e.max_hp_bonus == 0


def test_Equipment_max_hp_bonus__main_hand_bonus():
    ring = factory.mk_entity('ring of hp', 0, 0)
    e = components.Equipment()
    e.slots[Slots.MAIN_HAND] = ring

    assert e.max_hp_bonus == ring.equippable.max_hp_bonus


def test_Equipment_max_hp_bonus__off_hand_bonus():
    ring = factory.mk_entity('ring of hp', 0, 0)
    e = components.Equipment()
    e.slots[Slots.OFF_HAND] = ring

    assert e.max_hp_bonus == ring.equippable.max_hp_bonus


def test_Equipment_max_hp_bonus__both_hands_bonus():
    ring = factory.mk_entity('ring of hp', 0, 0)
    e = components.Equipment()
    e.slots[Slots.MAIN_HAND] = ring
    e.slots[Slots.OFF_HAND] = ring

    assert e.max_hp_bonus == ring.equippable.max_hp_bonus * 2


def test_Equipment_power_bonus__nothing_equipped_returns_0():
    e = components.Equipment()
    assert e.power_bonus == 0


def test_Equipment_power_bonus__main_hand_bonus():
    sword = factory.mk_entity('sword', 0, 0)
    e = components.Equipment()
    e.slots[Slots.MAIN_HAND] = sword

    assert e.power_bonus == sword.equippable.power_bonus


def test_Equipment_power_bonus__off_hand_bonus():
    sword = factory.mk_entity('sword', 0, 0)
    e = components.Equipment()
    e.slots[Slots.OFF_HAND] = sword

    assert e.power_bonus == sword.equippable.power_bonus


def test_Equipment_power_bonus__both_hands_bonus():
    sword = factory.mk_entity('sword', 0, 0)
    e = components.Equipment()
    e.slots[Slots.MAIN_HAND] = sword
    e.slots[Slots.OFF_HAND] = sword

    assert e.power_bonus == sword.equippable.power_bonus * 2


def test_Equipment_defense_bonus__nothing_equipped_returns_0():
    e = components.Equipment()
    assert e.defense_bonus == 0


def test_Equipment_defense_bonus__main_hand_bonus():
    shield = factory.mk_entity('shield', 0, 0)
    e = components.Equipment()
    e.slots[Slots.MAIN_HAND] = shield

    assert e.defense_bonus == shield.equippable.defense_bonus


def test_Equipment_defense_bonus__off_hand_bonus():
    shield = factory.mk_entity('shield', 0, 0)
    e = components.Equipment()
    e.slots[Slots.OFF_HAND] = shield

    assert e.defense_bonus == shield.equippable.defense_bonus


def test_Equipment_defense_bonus__both_hands_bonus():
    shield = factory.mk_entity('shield', 0, 0)
    e = components.Equipment()
    e.slots[Slots.MAIN_HAND] = shield
    e.slots[Slots.OFF_HAND] = shield

    assert e.defense_bonus == shield.equippable.defense_bonus * 2


def test_Equipment__is_equipped__equipped_returns_True(sword):
    e = components.Equipment()
    e.slots[Slots.MAIN_HAND] = sword

    assert e.is_equipped(sword)


def test_Equipment__is_equipped__not_equipped_returns_False(sword):
    e = components.Equipment()
    assert not e.is_equipped(sword)


def test_Equipment_equip__success__returns_True():
    shield = factory.mk_entity('shield', 0, 0)
    e = components.Equipment()
    assert e.equip(shield)


def test_Equipment_equip__success__item_is_in_slot():
    shield = factory.mk_entity('shield', 0, 0)
    e = components.Equipment()
    e.equip(shield)
    assert e.slots[Slots.OFF_HAND] == shield


def test_Equipment_equip__same_equipped_item_returns_True():
    shield = factory.mk_entity('shield', 0, 0)
    e = components.Equipment()
    e.equip(shield)
    assert e.equip(shield)


def test_Equipment_equip__another_item_while_equipped():
    sword = factory.mk_entity('sword', 0, 0)
    dagger = factory.mk_entity('dagger', 0, 0)
    e = components.Equipment()
    e.equip(sword)

    assert e.equip(dagger)
    assert e.slots[Slots.MAIN_HAND] == dagger


def test_Equipment_equip__both_slots():
    sword = factory.mk_entity('sword', 0, 0)
    shield = factory.mk_entity('shield', 0, 0)
    e = components.Equipment()

    assert e.equip(sword)
    assert e.equip(shield)
    assert e.slots[Slots.MAIN_HAND] == sword
    assert e.slots[Slots.OFF_HAND] == shield


def test_Equipment_equip__invalid_item_raises_AttributeError():
    potion = factory.mk_entity('healing_potion', 0, 0)
    e = components.Equipment()
    with pytest.raises(AttributeError):
        e.equip(potion)


def test_Equipment_unequip__success__returns_True():
    shield = factory.mk_entity('shield', 0, 0)
    e = components.Equipment()
    e.equip(shield)
    assert e.unequip(shield)


def test_Equipment_unequip__success__item_is_not_in_slot():
    shield = factory.mk_entity('shield', 0, 0)
    e = components.Equipment()
    e.equip(shield)
    e.unequip(shield)

    assert e.slots[Slots.MAIN_HAND] != shield
    assert e.slots[Slots.OFF_HAND] != shield


def test_Equipment_unequip__unequipped_item_returns_False():
    shield = factory.mk_entity('shield', 0, 0)
    e = components.Equipment()
    assert e.unequip(shield) is False


""" Tests for EnergyMeter """


def test_EnergyMeter__init():
    am = components.EnergyMeter(threshold=100)
    assert am.threshold == 100
    assert am.energy == 0


def test_EnergyMeter__burn_turn__not_enough_returns_False():
    am = components.EnergyMeter(threshold=100)

    result = am.burn_turn()
    assert result is False


def test_EnergyMeter__burn_turn__at_threshold_returns_True():
    am = components.EnergyMeter(threshold=100)
    am.add_energy(100)

    result = am.burn_turn()
    assert result

def test_EnergyMeter__burn_turn__at_threshold__energy_eq_0():
    am = components.EnergyMeter(threshold=100)
    am.add_energy(100)
    am.burn_turn()

    assert am.energy == 0

def test_EnergyMeter__burn_turn__above_threshold_returns_True():
    am = components.EnergyMeter(threshold=100)

    am.add_energy(110)
    result = am.burn_turn()
    assert result


def test_EnergyMeter__burn_turn__above_threshold__energy_eq_remainder():
    am = components.EnergyMeter(threshold=100)

    am.add_energy(110)
    am.burn_turn()
    assert am.energy == 10


def test_EnergyMeter__add_energy():
    am = components.EnergyMeter(threshold=100)

    am.add_energy(10)
    assert am.energy == 10


def test_EnergyMeter__burned_out__sufficient_energy_returns_False():
    am = components.EnergyMeter(threshold=100)
    am.add_energy(100)
    assert am.burned_out() is False


def test_EnergyMeter__burned_out__insufficient_energy_returns_True():
    am = components.EnergyMeter(threshold=100)
    am.add_energy(10)
    assert am.burned_out()
