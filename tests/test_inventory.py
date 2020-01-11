import pytest
from ..src import inventory

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


# def test_Inventory_add_item(self, item):

# def test_Inventory_use(self, item_entity, **kwargs):

# def test_Inventory_rm_item(self, item):

# def test_Inventory_drop(self, item):
