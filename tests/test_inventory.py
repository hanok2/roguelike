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
        inventory.Inventory(owner=None, capacity=-1)


def test_Inventory_init__0_capacity_raises_exception():
    with pytest.raises(ValueError):
        inventory.Inventory(owner=None, capacity=0)


def test_Inventory_init():
    i = inventory.Inventory(owner=None, capacity=10)
    assert i.capacity == 10
    assert i.items == []


def test_Inventory_add_item__returns_True(potion):
    i = inventory.Inventory(owner=None, capacity=10)
    assert i.add_item(potion)


def test_Inventory_add_item__items_increases(potion):
    i = inventory.Inventory(owner=None, capacity=10)
    prev_items = len(i.items)
    i.add_item(potion)
    assert len(i.items) == prev_items + 1


def test_Inventory_add_item___item_in_inv(potion):
    i = inventory.Inventory(owner=None, capacity=10)
    i.add_item(potion)
    assert potion in i.items


def test_Inventory_add_item__full__returns_False(potion):
    i = inventory.Inventory(owner=None, capacity=1)
    i.add_item(potion)
    assert i.add_item(potion) is False


def test_Inventory_add_item__full__items_same(potion):
    i = inventory.Inventory(owner=None, capacity=1)
    i.add_item(potion)
    prev_items = len(i.items)

    i.add_item(potion)
    assert len(i.items) == prev_items


def test_Inventory_rm_item__in_inv_items_decreases(potion):
    i = inventory.Inventory(owner=None, capacity=1)
    i.add_item(potion)
    i.rm_item(potion)
    assert i.items == []


def test_Inventory_rm_item__in_inv_removes_item(potion):
    i = inventory.Inventory(owner=None, capacity=1)
    i.add_item(potion)
    i.rm_item(potion)
    assert potion not in i.items


def test_Inventory_rm_item__in_inv_returns_True(potion):
    i = inventory.Inventory(owner=None, capacity=1)
    i.add_item(potion)
    assert i.rm_item(potion)


def test_Inventory_rm_item__DNE__returns_False(potion):
    i = inventory.Inventory(owner=None, capacity=1)
    assert i.rm_item(potion) is False
