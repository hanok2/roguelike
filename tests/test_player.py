import pytest
import tcod
from ..src import player
from ..src.config import RenderOrder


@pytest.fixture
def hero():
    return player.get_hero()


def test_get_hero__xy_are_0_0(hero):
    assert hero.x == 0
    assert hero.y == 0


def test_get_hero__char(hero):
    assert hero.char == '@'


def test_get_hero__color(hero):
    assert hero.color == tcod.white


def test_get_hero__name(hero):
    assert hero.name == 'Player'


def test_get_hero__blocks(hero):
    assert hero.blocks


def test_get_hero__renderorder(hero):
    assert hero.render_order is RenderOrder.ACTOR


def test_get_hero__Fighter(hero):
    assert hero.fighter
    # Stats?


def test_get_hero__Inventory(hero):
    assert hero.inv
    assert hero.inv.capacity == 26


def test_get_hero__Level(hero):
    assert hero.lvl
    assert hero.lvl.current_lvl == 1


def test_get_hero__Equipment(hero):
    assert hero.equipment


def test_get_hero__Human(hero):
    assert hero.human


def test_get_hero__has_dagger(hero):
    assert len(hero.inv.items) == 1
