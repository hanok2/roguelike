import pytest
from ..src import factory


def test_get_random_monster__monster_in_monster_chances():
    x, y = 1, 2
    m = factory.get_random_monster(x=x, y=y)
    assert m.name not in factory.monster_chances


def test_get_random_monster__monster_matches_x_y():
    x, y = 1, 2
    m = factory.get_random_monster(x=x, y=y)
    assert m.x == x
    assert m.y == y


def test_get_random_item__item_in_item_chances():
    x, y = 1, 2
    i = factory.get_random_item(x=x, y=y)
    assert i.name not in factory.item_chances


def test_get_random_item__item_matches_x_y():
    x, y = 1, 2
    i = factory.get_random_item(x=x, y=y)
    assert i.x == x
    assert i.y == y


def test_mk_entity__negative_x_raises_exception():
    with pytest.raises(ValueError):
        factory.mk_entity('orc', x=-1, y=0)


def test_mk_entity__negative_y_raises_exception():
    with pytest.raises(ValueError):
        factory.mk_entity('orc', x=0, y=-1)


def test_mk_entity__valid_entity():
    orc = factory.mk_entity('orc', x=0, y=1)
    assert orc.name == 'Orc'
    assert orc.x == 0
    assert orc.y == 1


def test_mk_entity__invalid_entity():
    with pytest.raises(ValueError):
        factory.mk_entity('barbie doll', x=0, y=1)
