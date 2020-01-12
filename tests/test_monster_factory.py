import pytest
from ..src import monster_factory


def test_get_random_monster__monster_in_monster_chances():
    x, y = 1, 2
    m = monster_factory.get_random_monster(x=x, y=y)
    assert m.name not in monster_factory.monster_chances


def test_get_random_monster__monster_matches_x_y():
    x, y = 1, 2
    m = monster_factory.get_random_monster(x=x, y=y)
    assert m.x == x
    assert m.y == y


def test_mk_monster__negative_x_raises_exception():
    with pytest.raises(ValueError):
        monster_factory.mk_monster('orc', x=-1, y=0)


def test_mk_monster__negative_y_raises_exception():
    with pytest.raises(ValueError):
        monster_factory.mk_monster('orc', x=0, y=-1)


def test_mk_monster__valid_monster():
    orc = monster_factory.mk_monster('orc', x=0, y=1)
    assert orc.name == 'Orc'
    assert orc.x == 0
    assert orc.y == 1


def test_mk_monster__invalid_monster():
    with pytest.raises(ValueError):
        monster_factory.mk_monster('barbie doll', x=0, y=1)
