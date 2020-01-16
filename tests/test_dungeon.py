import pytest
from pytest_mock import mocker
from ..src import dungeon
from ..src import stages
from ..src import player


@pytest.fixture
def hero():
    return player.get_hero()


"""Tests for class Dungeon(object):"""


def test_dungeon_init__beginning_variables(hero):
    d = dungeon.Dungeon(hero)
    assert d.hero is hero
    assert d.current_stage == 0


def test_dungeon_init__1_level_exists(hero):
    # Make sure 1 level is generated on init
    d = dungeon.Dungeon(hero)
    assert len(d.stages) == 1


@pytest.mark.skip(reason='Cannot implement yet because mocking causes problem with hero access to stages list.')
def test_dungeon_init__mk_next_stage_called(mocker, hero):
    mocker.patch.object(dungeon.Dungeon, 'mk_next_stage')
    d = dungeon.Dungeon(hero)
    d.mk_next_stage.assert_called_once()


def test_dungeon_init__hero_exists_on_stage(hero):
    d = dungeon.Dungeon(hero)
    m = d.get_stage()
    assert any([True for e in m.entities if e.has_comp('human')])


def test_dungeon_init__move_hero_called(mocker, hero):
    mocker.patch.object(dungeon.Dungeon, 'move_hero')
    d = dungeon.Dungeon(hero)
    d.move_hero.assert_called_once()


def test_dungeon_init__populate_called(mocker, hero):
    mocker.patch.object(stages.Stage, 'populate')
    d = dungeon.Dungeon(hero)
    m = d.get_stage()

    m.populate.assert_called_once()


def test_get_stage__1_level(hero):
    d = dungeon.Dungeon(hero)
    m = d.get_stage()
    assert m.dungeon_lvl == d.current_stage + 1


def test_get_stage__2_stages(hero):
    d = dungeon.Dungeon(hero)
    d.mk_next_stage()

    m = d.get_stage()
    assert m.dungeon_lvl == d.current_stage + 1

    d.current_stage = 1
    m = d.get_stage()
    assert m.dungeon_lvl == d.current_stage + 1


# def test_place_hero(, level):
    # Should this take the hero as a parameter?
    # Test that the hero is put somewhere

def test_mk_next_stage__stages_increases(hero):
    d = dungeon.Dungeon(hero)
    assert len(d.stages) == 1
    d.mk_next_stage()

    assert len(d.stages) == 2


def test_mk_next_stage__stages_are_numbered_correctly(hero):
    d = dungeon.Dungeon(hero)
    assert d.stages[0].dungeon_lvl == 1
    d.mk_next_stage()

    assert d.stages[1].dungeon_lvl == 2


def test_hero_at_stairs__valid_returns_True(hero):
    d = dungeon.Dungeon(hero)
    down_stair = d.get_stage().find_stair('>')
    d.hero.x, d.hero.y = down_stair.x, down_stair.y
    assert d.hero_at_stairs('>')


def test_hero_at_stairs__invalid_returns_False(hero):
    d = dungeon.Dungeon(hero)
    assert d.hero_at_stairs('>') is False


def test_hero_at_stairs__starting_upstair_returns_True(hero):
    d = dungeon.Dungeon(hero)
    # Hero starts on an upstair, so this should be True.
    assert d.hero_at_stairs('<')


def test_move_downstairs__not_on_down_stair_returns_False(hero):
    d = dungeon.Dungeon(hero)
    d.mk_next_stage()

    result = d.move_downstairs()
    assert result is False


def test_move_downstairs__hero_moved_to_next_upstair(hero):
    d = dungeon.Dungeon(hero)
    down_stair = d.get_stage().find_stair('>')
    d.hero.x, d.hero.y = down_stair.x, down_stair.y
    d.mk_next_stage()

    d.move_downstairs()
    up_stair = d.get_stage().find_stair('<')

    assert d.hero.x == up_stair.x
    assert d.hero.y == up_stair.y


def test_move_downstairs__dungeon_lvl_incremented(hero):
    d = dungeon.Dungeon(hero)
    prev_lvl = d.current_stage
    down_stair = d.get_stage().find_stair('>')
    d.hero.x, d.hero.y = down_stair.x, down_stair.y
    d.mk_next_stage()

    d.move_downstairs()

    assert d.current_stage == prev_lvl + 1

def test_move_downstairs__success_returns_True(hero):
    d = dungeon.Dungeon(hero)
    down_stair = d.get_stage().find_stair('>')
    d.hero.x, d.hero.y = down_stair.x, down_stair.y
    d.mk_next_stage()

    assert d.move_downstairs()


def test_move_upstairs__not_on_up_stair_returns_False(hero):
    d = dungeon.Dungeon(hero)
    down_stair = d.get_stage().find_stair('>')

    # Move hero to downstair (won't be on upstair)
    d.hero.x, d.hero.y = down_stair.x, down_stair.y
    assert d.move_upstairs() is False


def test_move_upstairs__hero_moved_to_prev_downstair(hero):
    d = dungeon.Dungeon(hero)
    down_stair = d.get_stage().find_stair('>')
    d.hero.x, d.hero.y = down_stair.x, down_stair.y
    d.mk_next_stage()

    # Move the hero downstairs first
    d.move_downstairs()

    # Hero moves back to previous down-stair
    d.move_upstairs()
    assert d.hero.x == down_stair.x
    assert d.hero.y == down_stair.y


def test_move_upstairs__success_returns_True(hero):
    d = dungeon.Dungeon(hero)
    down_stair = d.get_stage().find_stair('>')
    d.hero.x, d.hero.y = down_stair.x, down_stair.y
    d.mk_next_stage()

    d.move_downstairs()
    assert d.move_upstairs()


# def test_move_upstairs__when_at_the_top_lvl():
    # Return False?

# Wait on this test - might want to remove some calls from Dungeon init
# def test_move_hero__hero_not_placed_yet(hero):
    # d = dungeon.Dungeon(hero)

def test_move_hero__to_wall_returns_False(hero):
    d = dungeon.Dungeon(hero)
    m = stages.Stage(10, 10, 2)
    d.stages.append(m)
    assert d.move_hero(dest_stage_index=1, dest_x=0, dest_y=0) is False


def test_move_hero__to_occupied_spot_returns_False(hero):
    d = dungeon.Dungeon(hero)
    rnd_monster = [e for e in d.get_stage().entities if e.has_comp('ai')].pop()
    dest_x = rnd_monster.x
    dest_y = rnd_monster.y
    assert d.move_hero(dest_stage_index=0, dest_x=dest_x, dest_y=dest_y) is False


def test_move_hero__same_floor_returns_True(hero):
    d = dungeon.Dungeon(hero)
    dest_x, dest_y = d.get_stage().get_random_open_spot()
    assert d.move_hero(dest_stage_index=0, dest_x=dest_x, dest_y=dest_y)


def test_move_hero__same_floor_hero_xy_updated(hero):
    d = dungeon.Dungeon(hero)
    dest_x, dest_y = d.get_stage().get_random_open_spot()
    d.move_hero(dest_stage_index=0, dest_x=dest_x, dest_y=dest_y)
    assert d.hero.x == dest_x
    assert d.hero.y == dest_y


def test_move_hero__same_floor_lvl_remains_same(hero):
    d = dungeon.Dungeon(hero)
    d_lvl = d.current_stage
    dest_x, dest_y = d.get_stage().get_random_open_spot()
    d.move_hero(dest_stage_index=0, dest_x=dest_x, dest_y=dest_y)
    assert d.current_stage == d_lvl


def test_move_hero__diff_floor_returns_True(hero):
    dest_stage_index = 1
    d = dungeon.Dungeon(hero)
    d.mk_next_stage()

    dest_x, dest_y = d.stages[dest_stage_index].get_random_open_spot()
    assert d.move_hero(dest_stage_index=dest_stage_index, dest_x=dest_x, dest_y=dest_y)


def test_move_hero__diff_floor_hero_xy_updated(hero):
    dest_stage_index = 1
    d = dungeon.Dungeon(hero)
    d.mk_next_stage()

    dest_x, dest_y = d.stages[dest_stage_index].get_random_open_spot()
    d.move_hero(dest_stage_index=dest_stage_index, dest_x=dest_x, dest_y=dest_y)
    assert d.hero.x == dest_x
    assert d.hero.y == dest_y


def test_move_hero__diff_floor_dungeon_lvl_updated(hero):
    dest_stage_index = 1
    d = dungeon.Dungeon(hero)
    d.mk_next_stage()

    dest_x, dest_y = d.stages[dest_stage_index].get_random_open_spot()
    d.move_hero(dest_stage_index=dest_stage_index, dest_x=dest_x, dest_y=dest_y)
    assert d.current_stage == dest_stage_index
