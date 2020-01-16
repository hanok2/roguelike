import pytest
import tcod
from ..src import entity
from ..src import player
from ..src.config import RenderOrder


@pytest.fixture
def hero():
    return player.get_hero()


def test_get_hero__has_dagger(hero):
    assert len(hero.inv.items) == 1


""" Tests for Player class """


def test_Player__subclass_of_Entity():
    p = player.Player()
    assert issubclass(type(p), entity.Entity)


def test_Player__xy_are_0_0():
    p = player.Player()
    assert p.x == 0
    assert p.y == 0


def test_Player__xy_are_passed():
    x, y = 1, 2
    p = player.Player(x, y)
    assert p.x == x
    assert p.y == y


def test_Player__char():
    p = player.Player()
    assert p.char == '@'


def test_Player__color():
    p = player.Player()
    assert p.color == tcod.white


def test_Player__name():
    p = player.Player()
    assert p.name == 'Player'


def test_Player__blocks():
    p = player.Player()
    assert p.blocks


def test_Player__renderorder():
    p = player.Player()
    assert p.render_order is RenderOrder.ACTOR


def test_Player__Fighter():
    p = player.Player()
    assert p.fighter


def test_Player__Inventory():
    p = player.Player()
    assert p.inv
    assert p.inv.capacity == 26


def test_Player__Level():
    p = player.Player()
    assert p.lvl
    assert p.lvl.current_lvl == 1


def test_Player__Equipment():
    p = player.Player()
    assert p.equipment


def test_Player__Human():
    p = player.Player()
    assert p.human
