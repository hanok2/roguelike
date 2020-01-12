import pytest
from ..src import monster_factory

# This one depends on from_dungeon_lvl - test later?
# def monster_chances(dungeon_lvl):


def test_get_random_monster__negative_x_raises_exception():
    with pytest.raises(ValueError):
        monster_factory.get_random_monster(x=-1, y=0)


def test_get_random_monster__negative_y_raises_exception():
    with pytest.raises(ValueError):
         monster_factory.get_random_monster(x=0, y=-1)


def test_get_random_monster__monster_in_monster_chances():
    x, y = 1, 2
    m = monster_factory.get_random_monster(x=x, y=y)
    assert m.name not in monster_factory.monster_chances


def test_get_random_monster__monster_matches_x_y():
    x, y = 1, 2
    m = monster_factory.get_random_monster(x=x, y=y)
    assert m.x == x
    assert m.y == y


# def mk_monster(monster_type, x, y):
