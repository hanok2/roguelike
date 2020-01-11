import pytest
from ..src import inventory
from .test_components import ring_of_power

""" Tests for Inventory """


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


def test_Inventory_add_item_within_capacity_items_increases(ring_of_power):
    i = inventory.Inventory(10)
    prev_items = len(i.items)
    i.add_item(ring_of_power)
    assert len(i.items) == prev_items + 1


def test_Inventory_add_item_within_capacity_item_in_inv(ring_of_power):
    i = inventory.Inventory(10)
    i.add_item(ring_of_power)
    assert ring_of_power in i.items


def test_Inventory_add_item_within_capacity_results_item_added(ring_of_power):
    i = inventory.Inventory(10)
    result = i.add_item(ring_of_power).pop()
    assert result['item_added'] == ring_of_power


def test_Inventory_add_item_within_capacity_results_msg(ring_of_power):
    i = inventory.Inventory(10)
    result = i.add_item(ring_of_power).pop()
    assert result['msg'] == 'You pick up the Ring of Power.'


def test_Inventory_add_item_outside_capacity_items_same(ring_of_power):
    i = inventory.Inventory(1)
    i.add_item(ring_of_power)
    prev_items = len(i.items)

    i.add_item(ring_of_power)
    assert len(i.items) == prev_items


@pytest.mark.skip(reason='need a item generator to get a different item.')
def test_Inventory_add_item_outside_capacity_item_in_inv():
    pass


def test_Inventory_add_item_outside_capacity_results_msg(ring_of_power):
    i = inventory.Inventory(1)
    i.add_item(ring_of_power)
    result = i.add_item(ring_of_power).pop()
    assert result['msg'] == inventory.INV_FULL_MSG


def test_Inventory_add_item_outside_capacity_results_item_added(ring_of_power):
    i = inventory.Inventory(1)
    i.add_item(ring_of_power)
    result = i.add_item(ring_of_power).pop()
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
def test_Inventory_rm_item__in_inv_items_decreases(ring_of_power):
    i = inventory.Inventory(1)
    i.add_item(ring_of_power)
    i.rm_item(ring_of_power)
    assert i.items == []


# todo: Add multiple items to inventory for this test
def test_Inventory_rm_item__in_inv_removes_item(ring_of_power):
    i = inventory.Inventory(1)
    i.add_item(ring_of_power)
    i.rm_item(ring_of_power)
    assert ring_of_power not in i.items


# todo: Add multiple items to inventory for this test
def test_Inventory_rm_item__in_inv_returns_True(ring_of_power):
    i = inventory.Inventory(1)
    i.add_item(ring_of_power)
    assert i.rm_item(ring_of_power)


# todo: Add multiple items to inventory for this test
def test_Inventory_rm_item__DNE_items_remains_same(ring_of_power):
    i = inventory.Inventory(1)
    i.rm_item(ring_of_power)
    assert i.items == []


# todo: Add multiple items to inventory for this test
def test_Inventory_rm_item__DNE_returns_False(ring_of_power):
    i = inventory.Inventory(1)
    assert i.rm_item(ring_of_power) is False


# def test_Inventory_drop(self, item):
