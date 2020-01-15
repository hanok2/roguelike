import pytest
import tcod
from ..src import components
from ..src import death_functions
from ..src import factory
from ..src import player
from ..src.config import RenderOrder, States


@pytest.fixture
def basic_hero():
    return player.get_hero()


@pytest.fixture
def orc():
    return factory.mk_entity('orc', 0, 0)


def test_kill_hero__char_is_corpse(basic_hero):
    death_functions.kill_hero(basic_hero)
    assert basic_hero.char == '%'


def test_kill_hero__color_is_darkred(basic_hero):
    death_functions.kill_hero(basic_hero)
    assert basic_hero.color == tcod.dark_red


def test_kill_hero__returns_death_msg_and_dead_status(basic_hero):
    result = death_functions.kill_hero(basic_hero)
    assert result == (
        'You died!',
        States.HERO_DEAD
    )


def test_kill_monster__char_is_corpse(orc):
    death_functions.kill_monster(orc)
    assert orc.char == '%'


def test_kill_monster__name_is_remains(orc):
    death_functions.kill_monster(orc)
    assert orc.name == 'remains of Orc'


def test_kill_monster__color_is_red(orc):
    death_functions.kill_monster(orc)
    assert orc.color == tcod.dark_red


def test_kill_monster__blocks_is_False(orc):
    death_functions.kill_monster(orc)
    assert orc.blocks is False


def test_kill_monster__renderorder_is_corpse(orc):
    death_functions.kill_monster(orc)
    assert orc.render_order == RenderOrder.CORPSE


def test_kill_monster__fighter_is_None(orc):
    death_functions.kill_monster(orc)
    assert orc.has_comp('fighter') is False


def test_kill_monster__ai_is_none(orc):
    death_functions.kill_monster(orc)
    assert orc.has_comp('ai') is False


def test_kill_monster__item_comp_is_True(orc):
    death_functions.kill_monster(orc)
    assert isinstance(orc.item, components.Item)


def test_kill_monster__returns_death_msg(orc):
    result = death_functions.kill_monster(orc)
    assert result == 'The Orc dies!'
