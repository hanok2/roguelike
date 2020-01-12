import pytest
from ..src import factory
from ..src import inventory
from ..src import player

""" Tests for Inventory """

@pytest.fixture
def hero():
    return player.get_hero()


@pytest.fixture
def potion():
    return factory.mk_entity('healing_potion', 0, 0)


@pytest.fixture
def sword():
    return factory.mk_entity('sword', 0, 0)


def test_Inventory_init__negative_capacity_raises_exception():
    with pytest.raises(ValueError):
        inventory.Inventory(-1)


def test_Inventory_init__0_capacity_raises_exception():
    with pytest.raises(ValueError):
        inventory.Inventory(0)


def test_Inventory_init():
    i = inventory.Inventory(10)
    assert i.capacity == 10
    assert i.items == []


def test_Inventory_add_item_within_capacity_items_increases(potion):
    i = inventory.Inventory(10)
    prev_items = len(i.items)
    i.add_item(potion)
    assert len(i.items) == prev_items + 1


def test_Inventory_add_item_within_capacity_item_in_inv(potion):
    i = inventory.Inventory(10)
    i.add_item(potion)
    assert potion in i.items


def test_Inventory_add_item_within_capacity_results_item_added(potion):
    i = inventory.Inventory(10)
    result = i.add_item(potion).pop()
    assert result['item_added'] == potion


def test_Inventory_add_item_within_capacity_results_msg(potion):
    i = inventory.Inventory(10)
    result = i.add_item(potion).pop()
    assert result['msg'] == 'You pick up the Healing potion.'


def test_Inventory_add_item_outside_capacity_items_same(potion):
    i = inventory.Inventory(1)
    i.add_item(potion)
    prev_items = len(i.items)

    i.add_item(potion)
    assert len(i.items) == prev_items


@pytest.mark.skip(reason='need a item generator to get a different item.')
def test_Inventory_add_item_outside_capacity_item_in_inv():
    pass


def test_Inventory_add_item_outside_capacity_results_msg(potion):
    i = inventory.Inventory(1)
    i.add_item(potion)
    result = i.add_item(potion).pop()
    assert result['msg'] == inventory.INV_FULL_MSG


def test_Inventory_add_item_outside_capacity_results_item_added(potion):
    i = inventory.Inventory(1)
    i.add_item(potion)
    result = i.add_item(potion).pop()
    assert result['item_added'] is None


@pytest.mark.skip(reason='Need to flesh this test out more - need resources.')
def test_Inventory_use():
    pass
    # Needs item_entity with item_comp
    # Test consumable items (scrolls/potions)
    # Test equippable items (shield/sword)
    # Test targetable items (confuse monster/lightning)
    # Test return results


# todo: Add multiple items to inventory for this test
def test_Inventory_rm_item__in_inv_items_decreases(potion):
    i = inventory.Inventory(1)
    i.add_item(potion)
    i.rm_item(potion)
    assert i.items == []


# todo: Add multiple items to inventory for this test
def test_Inventory_rm_item__in_inv_removes_item(potion):
    i = inventory.Inventory(1)
    i.add_item(potion)
    i.rm_item(potion)
    assert potion not in i.items


# todo: Add multiple items to inventory for this test
def test_Inventory_rm_item__in_inv_returns_True(potion):
    i = inventory.Inventory(1)
    i.add_item(potion)
    assert i.rm_item(potion)


# todo: Add multiple items to inventory for this test
def test_Inventory_rm_item__DNE_items_remains_same(potion):
    i = inventory.Inventory(1)
    i.rm_item(potion)
    assert i.items == []


# todo: Add multiple items to inventory for this test
def test_Inventory_rm_item__DNE_returns_False(potion):
    i = inventory.Inventory(1)
    assert i.rm_item(potion) is False


# todo: Simplify this???
def test_Inventory_drop__item_DNE_raise_exception(potion, hero):
    with pytest.raises(ValueError):
        hero.inv.drop(potion)


def test_Inventory_drop__returns_result_msg(potion, hero):
    hero.inv.add_item(potion)
    results = hero.inv.drop(potion).pop()
    assert results['msg'] == 'You dropped the Healing potion.'


def test_Inventory_drop__returns_result_item_dropped(potion, hero):
    hero.inv.add_item(potion)
    results = hero.inv.drop(potion).pop()
    assert results['item_dropped'] == potion


def test_Inventory_drop__updates_item_xy(potion, hero):
    hero.inv.add_item(potion)
    hero.inv.drop(potion)
    assert potion.x == hero.x
    assert potion.y == hero.y


@pytest.mark.skip(reason='need to mock')
def test_Inventory_drop__equipped_item_called_drop_equipped(sword, hero):
    pass


# Todo: Revise the results system! We can see how ugly this is.
def test_Inventory_drop__equipped_item__results(sword, hero):
    hero.inv.add_item(sword)
    hero.equipment.toggle_equip(sword)
    results = hero.inv.drop(sword)

    assert results[0]['dequipped'] == sword

    assert results[1]['msg'] == 'You dropped the Sword.'
    assert results[1]['item_dropped'] == sword


def test_Inventory_drop__equipped_item__updates_item_xy(sword, hero):
    hero.inv.add_item(sword)
    hero.equipment.toggle_equip(sword)
    hero.inv.drop(sword)

    assert sword.x == hero.x
    assert sword.y == hero.y

def test_Inventory_drop__equipped_item__item_dropped(sword, hero):
    hero.inv.add_item(sword)
    hero.equipment.toggle_equip(sword)

    hero.inv.drop(sword)
    assert sword not in hero.inv.items


def test_Inventory_chk_equipped__equipped_item_returns_result(sword, hero):
    hero.inv.add_item(sword)
    hero.equipment.toggle_equip(sword)

    results = hero.inv.chk_equipped(sword)
    assert results[0]['dequipped'] == sword


def test_Inventory_chk_equipped__not_equipped_returns_empty_result(sword, hero):
    hero.inv.add_item(sword)
    assert hero.inv.chk_equipped(sword) == []


@pytest.mark.skip('todo later')
def test_Inventory_chk_equipped__item_is_not_equipment(potion, hero):
    pass


@pytest.mark.skip('todo later')
def test_Inventory_chk_equipped__hero_doesnt_have_anything_equipped(hero):
    pass
