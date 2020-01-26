import pytest
from pytest_mock import mocker

from ..src import config
from ..src import entity
from ..src import player
from ..src import rect
from ..src import stages

DEFAULT_LENGTH = 50
INVALID_LENGTH = 2

@pytest.fixture
def hero():
    return player.Player()


"""Tests for class Stage(object):"""


def test_Stage_init():
    m = stages.Stage(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    assert len(m.tiles) == DEFAULT_LENGTH
    assert m.entities == []
    assert m.rooms == []
    assert m.dungeon_lvl == config.DEFAULT_DUNGEON_LVL

def test_Stage_init_invalid_width_raises_exception():
    with pytest.raises(ValueError):
        stages.Stage(width=INVALID_LENGTH, height=DEFAULT_LENGTH)

def test_Stage_init_invalid_height_raises_exception():
    with pytest.raises(ValueError):
        stages.Stage(width=DEFAULT_LENGTH, height=INVALID_LENGTH)

def test_Stage_init_invalid_dungeon_lvl_raises_exception():
    with pytest.raises(ValueError):
        stages.Stage(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH, dungeon_lvl=0)

def test_Stage_rm_hero_if_absent_returns_False():
    m = stages.Stage(width=3, height=3)
    result = m.rm_hero()
    # Should be False because the stage is not initialized with the hero in it.
    assert result is False

def test_Stage_rm_hero_if_present_returns_True(hero):
    m = stages.Stage(width=3, height=3)
    m.entities.append(hero)
    result = m.rm_hero()
    assert result is True
    # Also check there is no hero in the entities
    assert hero not in m.entities


def test_Stage_find_stair__down_stair_returns_entity():
    m = stages.Stage(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    m.mk_stage()
    stair = [e for e in m.entities if e.has_comp('stair_down')].pop()
    result = m.find_stair('>')
    assert result == stair

def test_Stage_find_stair__up_stair_returns_entity():
    m = stages.Stage(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    m.mk_stage()
    stair = [e for e in m.entities if e.has_comp('stair_up')].pop()
    result = m.find_stair('<')
    assert result == stair


def test_Stage_find_stair__DNE_returns_None():
    m = stages.Stage(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    assert m.find_stair('>') is None
    assert m.find_stair('<') is None

def test_Stage_initialize_tiles():
    # Test that all initialized tiles are True (aka: Wall)
    m = stages.Stage(width=3, height=3)
    result = m.initialize_tiles()
    assert all(t for t in result)


def test_Stage_is_blocked_wall_returns_true():
    m = stages.Stage(width=3, height=3)
    result = m.blocks(0, 0)
    assert result is True

def test_Stage_is_blocked_not_wall_returns_False():
    x, y = 1, 1  # Dig out
    m = stages.Stage(width=3, height=3)
    m.tiles[x][y].blocks = False
    result = m.blocks(x, y)
    assert result is False


def test_Stage_mk_room_x1_in_stage():
    m = stages.Stage(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    r = m.mk_room()
    assert r.x1 >= 0
    assert r.x1 < DEFAULT_LENGTH

def test_Stage_mk_room_x2_in_stage():
    m = stages.Stage(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    r = m.mk_room()
    assert r.x2 >= 0
    assert r.x2 < DEFAULT_LENGTH

def test_Stage_mk_room_y1_in_stage():
    m = stages.Stage(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    r = m.mk_room()
    assert r.y1 >= 0
    assert r.y1 < DEFAULT_LENGTH

def test_Stage_mk_room_y2_in_stage():
    m = stages.Stage(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    r = m.mk_room()
    assert r.y2 >= 0
    assert r.y2 < DEFAULT_LENGTH


def test_Stage_dig_room_4x4():
    m = stages.Stage(width=10, height=10)
    r = rect.Rect(0, 0, 4, 4)
    m.dig_room(r)

    assert m.tiles[0][0].blocks is True  # Wall
    assert m.tiles[1][1].blocks is False  # Floor
    assert m.tiles[2][2].blocks is False  # Floor
    assert m.tiles[3][3].blocks is True  # Wall


def test_Stage_dig_room_room_4x3():
    m = stages.Stage(width=10, height=10)
    r = rect.Rect(0, 0, 4, 3)
    m.dig_room(r)

    assert m.tiles[0][0].blocks is True  # Wall
    assert m.tiles[1][1].blocks is False  # Floor
    assert m.tiles[2][1].blocks is False  # Floor
    assert m.tiles[2][3].blocks is True # Wall


def test_Stage_dig_room_5x5():
    m = stages.Stage(width=10, height=10)
    r = rect.Rect(0, 0, 5, 5)
    m.dig_room(r)

    assert m.tiles[0][0].blocks is True  # Wall
    assert m.tiles[1][1].blocks is False  # Floor
    assert m.tiles[2][2].blocks is False  # Floor
    assert m.tiles[3][3].blocks is False  # Floor
    assert m.tiles[4][4].blocks is True  # Wall


def test_Stage_mk_tunnel_simple_horz_first():
    m = stages.Stage(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    r1 = rect.Rect(0, 0, 4, 4)
    r2 = rect.Rect(8, 8, 4, 4)
    m.mk_tunnel_simple(r1, r2)

    cx1, cy1 = r1.center()
    cx2, cy2 = r2.center()

    # Test the horizontal tunnel
    for x in range(cx1, cx2 + 1):
        assert m.tiles[x][cy1].blocks is False # Floor

    # Test the vertical tunnel
    for y in range(cy1, cy2 + 1):
        assert m.tiles[cx2][y].blocks is False # Floor


def test_Stage_mk_tunnel_simple_vert_first():
    m = stages.Stage(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    r1 = rect.Rect(0, 0, 4, 4)
    r2 = rect.Rect(8, 8, 4, 4)
    m.mk_tunnel_simple(r1, r2, horz_first=False)

    cx1, cy1 = r1.center()
    cx2, cy2 = r2.center()

    # Test the vertical tunnel
    for y in range(cy1, cy2 + 1):
        assert m.tiles[cx1][y].blocks is False # Floor

    # Test the horizontal tunnel
    for x in range(cx1, cx2 + 1):
        assert m.tiles[x][cy2].blocks is False # Floor


def test_Stage_dig_h_tunnel():
    m = stages.Stage(width=10, height=10)
    m.dig_h_tunnel(x1=0, x2=8, y=0)
    assert m.tiles[0][0].blocks is False
    assert m.tiles[8][0].blocks is False
    assert m.tiles[9][0].blocks is True


def test_Stage_dig_h_tunnel_reversed_parameters():
    m = stages.Stage(width=10, height=10)
    m.dig_h_tunnel(x1=8, x2=0, y=0)
    assert m.tiles[0][0].blocks is False
    assert m.tiles[8][0].blocks is False
    assert m.tiles[9][0].blocks is True


def test_Stage_dig_v_tunnel():
    m = stages.Stage(width=10, height=10)
    m.dig_v_tunnel(y1=0, y2=8, x=0)
    assert m.tiles[0][0].blocks is False
    assert m.tiles[0][8].blocks is False
    assert m.tiles[0][9].blocks is True


def test_Stage_dig_v_tunnel_reversed_parameters():
    m = stages.Stage(width=10, height=10)
    m.dig_v_tunnel(y1=8, y2=0, x=0)
    assert m.tiles[0][0].blocks is False
    assert m.tiles[0][8].blocks is False
    assert m.tiles[0][9].blocks is True

def test_Stage_mk_stage__has_at_least_2_rooms():
    m = stages.Stage(width=50, height=50)
    m.mk_stage()
    assert len(m.rooms) >= 2


def test_Stage_mk_stage__has_up_stair():
    m = stages.Stage(width=50, height=50)
    m.mk_stage()
    assert  m.find_stair('<')


def test_Stage_mk_stage__has_down_stair():
    m = stages.Stage(width=50, height=50)
    m.mk_stage()
    assert m.find_stair('>')


def test_Stage_mk_stage__up_and_down_stairs_in_diff_rooms():
    m = stages.Stage(width=50, height=50)
    m.mk_stage()
    stair_up = m.find_stair('<')
    stair_down = m.find_stair('>')

    stair_up_room = None
    for room in m.rooms:
        if room.within(stair_up.x, stair_up.y):
            stair_up_room = room
            break
    # The coordinates of stair_down should not be within the same room as stair_up
    assert not stair_up_room.within(stair_down.x, stair_down.y)


# def test_Stage_mk_stage__all_rooms_interconnected():
    # Need a pathfinding algorithm??


def test_Stage_populate__calls_place_entities_and_items(mocker):
    m = stages.Stage(width=50, height=50)
    m.mk_stage()
    mocker.patch.object(m, 'place_monsters')
    mocker.patch.object(m, 'place_items')
    m.populate()

    m.place_monsters.assert_called_once_with()
    m.place_items.assert_called()


def test_Stage_populate__no_rooms_does_not_call_place_items(mocker):
    m = stages.Stage(width=50, height=50)
    mocker.patch.object(m, 'place_monsters')
    mocker.patch.object(m, 'place_items')
    m.populate()

    m.place_monsters.assert_called_once_with()
    assert not m.place_items.called


def test_Stage_is_occupied__not_occupied_returns_False():
    # Test if there are any entities at the coordinates
    m = stages.Stage(width=10, height=10)
    result = m.is_occupied(0, 0)
    assert result is False

def test_Stage_is_occupied__occupied_return_True(hero):
    # Test if there are any entities at the coordinates
    m = stages.Stage(width=10, height=10)
    x, y = 0, 0
    m.entities.append(hero)
    assert m.is_occupied(x, y) is True


def test_get_random_open_spot__all_wall_returns_None():
    m = stages.Stage(width=10, height=10)
    assert m.get_random_open_spot() is None


def test_get_random_open_spot__single_spot():
    m = stages.Stage(width=10, height=10)
    m.tiles[0][0].blocks = False
    assert m.get_random_open_spot() == (0, 0)


def test_Stage_get_random_non_wall_loc__default_stage_returns_None():
    m = stages.Stage(width=10, height=10)
    # There should be no non-Wall tiles in a default stage
    assert m.get_random_non_wall_loc() is None

def test_Stage_get_random_non_wall_loc__returns_non_wall():
    m = stages.Stage(width=10, height=10)
    m.tiles[0][0].blocks = False
    result = m.get_random_non_wall_loc()
    assert result == (0, 0)

def test_Stage_get_random_room_loc__stage_corner():
    m = stages.Stage(width=50, height=50)
    r = rect.Rect(x=0, y=0, w=5, h=5)
    result_x, result_y = m.get_random_room_loc(r)
    min_x = r.x1 + config.NW_OFFSET
    max_x = r.x2 - config.SE_OFFSET
    min_y = r.y1 + config.NW_OFFSET
    max_y = r.y2 - config.SE_OFFSET

    assert result_x >= min_x and result_x <= max_x
    assert result_y >= min_y and result_y <= max_y


def test_Stage_get_random_room_loc__stage_middle():
    m = stages.Stage(width=50, height=50)
    r = rect.Rect(x=10, y=10, w=15, h=5)
    result_x, result_y = m.get_random_room_loc(r)
    min_x = r.x1 + config.NW_OFFSET
    max_x = r.x2 - config.SE_OFFSET
    min_y = r.y1 + config.NW_OFFSET
    max_y = r.y2 - config.SE_OFFSET

    assert result_x >= min_x and result_x <= max_x
    assert result_y >= min_y and result_y <= max_y


def test_Stage_place_monsters__all_wall_tiles():
    m = stages.Stage(width=50, height=50)
    m.place_monsters()

    # Check that no entities are on Wall tiles
    for e in m.entities:
        assert m.tiles[e.x][e.y].blocks is False


def test_Stage_place_monsters_no_entities_appear_in_Wall():
    m = stages.Stage(width=50, height=50)
    m.mk_stage()
    m.place_monsters()

    # Check that no entities are on Wall tiles
    for e in m.entities:
        assert m.tiles[e.x][e.y].blocks is False


def test_Stage_place_items_no_entities_appear_in_Wall():
    m = stages.Stage(width=50, height=50)
    r = rect.Rect(0, 0, 5, 5)
    m.dig_room(r)
    m.place_items(r)

    # Check that no entities are on Wall tiles
    for e in m.entities:
        assert m.tiles[e.x][e.y].blocks is False


def test_Stage_place_stairs_down_on_floor__valid_pos():
    m = stages.Stage(width=50, height=50)
    r = rect.Rect(0, 0, 5, 5)
    m.dig_room(r)
    x, y = r.center()
    result = m.place_stairs_down(x, y)

    assert result.x == x
    assert result.y == y
    assert result in m.entities


def test_Stage_place_stairs_down_on_wall_raises_exception():
    m = stages.Stage(width=50, height=50)
    x, y = 0, 0
    with pytest.raises(ValueError):
        m.place_stairs_down(x, y)


def test_Stage_place_stairs_up__valid_pos():
    m = stages.Stage(width=50, height=50)
    r = rect.Rect(0, 0, 5, 5)
    m.dig_room(r)
    x, y = r.center()
    result = m.place_stairs_up(x, y)

    assert result.x == x
    assert result.y == y
    assert result in m.entities


def test_Stage_place_stairs_up_on_wall_raises_exception():
    m = stages.Stage(width=50, height=50)
    x, y = 0, 0
    with pytest.raises(ValueError):
        m.place_stairs_up(x, y)


def test_Stage_get_blocker_at_loc__blocked_returns_entity():
    m = stages.Stage(width=50, height=50)
    m.mk_stage()
    m.place_monsters()

    # Note - might be fragile - depending on monsters added last
    monster = m.entities[-1]

    print(monster.name)
    result = m.get_blocker_at_loc(monster.x, monster.y)
    assert result == monster


def test_Stage_get_blocker_at_loc__not_blocked_returns_None():
    m = stages.Stage(width=50, height=50)
    result = m.get_blocker_at_loc(0, 0)
    assert result is None


def test_Stage_calc_dxdy__N():
    dx, dy = stages.Stage.calc_dxdy(1, 1, 1, 0)
    assert dx == 0 and dy == -1


def test_Stage_calc_dxdy__NE():
    dx, dy = stages.Stage.calc_dxdy(1, 1, 2, 0)
    assert dx == 1 and dy == -1


def test_Stage_calc_dxdy__E():
    dx, dy = stages.Stage.calc_dxdy(1, 1, 2, 1)
    assert dx == 1 and dy == 0


def test_Stage_calc_dxdy__SE():
    dx, dy = stages.Stage.calc_dxdy(1, 1, 2, 2)
    assert dx == 1 and dy == 1


def test_Stage_calc_dxdy__S():
    dx, dy = stages.Stage.calc_dxdy(1, 1, 1, 2)
    assert dx == 0 and dy == 1


def test_Stage_calc_dxdy__SW():
    dx, dy = stages.Stage.calc_dxdy(1, 1, 0, 2)
    assert dx == -1 and dy == 1


def test_Stage_calc_dxdy__W():
    dx, dy = stages.Stage.calc_dxdy(1, 1, 0, 1)
    assert dx == -1 and dy == 0


def test_Stage_calc_dxdy__NW():
    dx, dy = stages.Stage.calc_dxdy(1, 1, 0, 0)
    assert dx == -1 and dy == -1


def test_Stage_calc_move__same_point_returns_0_0():
    dx, dy = stages.Stage.calc_move(0, 0, 0, 0)
    assert dx == 0 and dy == 0


def test_Stage_calc_move__south():
    dx, dy = stages.Stage.calc_move(0, 0, 0, 1)
    assert dx == 0 and dy == 1


def test_Stage_calc_move__knights_jump_south():
    dx, dy = stages.Stage.calc_move(0, 0, 1, 2)
    assert dx == 0 and dy == 1


def test_Stage_distance__same_point_returns_0():
    result = stages.Stage.distance(0, 0, 0, 0)
    assert result == 0


def test_Stage_distance__1_tile_away_returns_1():
    result = stages.Stage.distance(0, 0, 1, 0)
    assert result == 1


def test_Stage_distance__1_diagonal_tile_away_returns_something():
    result = stages.Stage.distance(0, 0, 1, 1)
    result = round(result, 2)  # Round to 2 decimal places
    assert result == 1.41


def test_Stage_distance_between_entities():
    hero = entity.Entity(x=0, y=0)
    orc = entity.Entity(x=0, y=10)
    result = stages.Stage.distance_between_entities(hero, orc)

    assert result == 10
