import pytest
from ..src import entity
from ..src import maps
from ..src import config
from ..src import rect

DEFAULT_LENGTH = 50
INVALID_LENGTH = 2

"""Tests for class Dungeon(object):"""

# def test_dungeon_init__():
# def test_current_map():
# def test_place_hero(, level):
# def test_generate_next_level():
# def test_move_downstairs():
# def test_move_upstairs():


"""Tests for class Map(object):"""


def test_map_init():
    m = maps.Map(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    assert len(m.tiles) == DEFAULT_LENGTH
    assert m.entities == []
    assert m.rooms == []
    assert m.dungeon_lvl == config.DEFAULT_DUNGEON_LVL

def test_map_init_invalid_width_raises_exception():
    with pytest.raises(ValueError):
        maps.Map(width=INVALID_LENGTH, height=DEFAULT_LENGTH)

def test_map_init_invalid_height_raises_exception():
    with pytest.raises(ValueError):
        maps.Map(width=DEFAULT_LENGTH, height=INVALID_LENGTH)

def test_map_init_invalid_dungeon_lvl_raises_exception():
    with pytest.raises(ValueError):
        maps.Map(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH, dungeon_lvl=0)

def test_map_rm_hero_if_absent_returns_False():
    m = maps.Map(width=3, height=3)
    result = m.rm_hero()
    # Should be False because the map is not initialized with the hero in it.
    assert result is False

def test_map_rm_hero_if_present_returns_True():
    m = maps.Map(width=3, height=3)
    hero = entity.Entity(0, 0, '@', None, 'Player', human=True)
    m.entities.append(hero)
    result = m.rm_hero()
    assert result is True
    # Also check there is no hero in the entities
    assert hero not in m.entities


def test_map_find_down_stair():
    m = maps.Map(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    m.make_map()
    # Find where the stairs are
    stair = [e for e in m.entities if e.stair_down].pop()
    result = m.find_down_stair()
    assert result == stair

def test_map_find_down_stair_DNE_return_None():
    m = maps.Map(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    result = m.find_down_stair()
    assert result is None


def test_map_initialize_tiles():
    # Test that all initialized tiles are True (aka: Wall)
    m = maps.Map(width=3, height=3)
    result = m.initialize_tiles()
    assert all(t for t in result)


def test_map_is_blocked_wall_returns_true():
    m = maps.Map(width=3, height=3)
    result = m.is_blocked(0, 0)
    assert result is True

def test_map_is_blocked_not_wall_returns_False():
    x, y = 1, 1  # Dig out
    m = maps.Map(width=3, height=3)
    m.tiles[x][y].blocked = False
    result = m.is_blocked(x, y)
    assert result is False


def test_map_mk_room_x1_in_map():
    m = maps.Map(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    r = m.mk_room()
    assert r.x1 >= 0
    assert r.x1 < DEFAULT_LENGTH

def test_map_mk_room_x2_in_map():
    m = maps.Map(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    r = m.mk_room()
    assert r.x2 >= 0
    assert r.x2 < DEFAULT_LENGTH

def test_map_mk_room_y1_in_map():
    m = maps.Map(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    r = m.mk_room()
    assert r.y1 >= 0
    assert r.y1 < DEFAULT_LENGTH

def test_map_mk_room_y2_in_map():
    m = maps.Map(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    r = m.mk_room()
    assert r.y2 >= 0
    assert r.y2 < DEFAULT_LENGTH


def test_map_dig_room_4x4():
    m = maps.Map(width=10, height=10)
    r = rect.Rect(0, 0, 4, 4)
    m.dig_room(r)

    assert m.tiles[0][0].blocked is True  # Wall
    assert m.tiles[1][1].blocked is False  # Floor
    assert m.tiles[2][2].blocked is False  # Floor
    assert m.tiles[3][3].blocked is True  # Wall


def test_map_dig_room_room_4x3():
    m = maps.Map(width=10, height=10)
    r = rect.Rect(0, 0, 4, 3)
    m.dig_room(r)

    assert m.tiles[0][0].blocked is True  # Wall
    assert m.tiles[1][1].blocked is False  # Floor
    assert m.tiles[2][1].blocked is False  # Floor
    assert m.tiles[2][3].blocked is True # Wall


def test_map_dig_room_5x5():
    m = maps.Map(width=10, height=10)
    r = rect.Rect(0, 0, 5, 5)
    m.dig_room(r)

    assert m.tiles[0][0].blocked is True  # Wall
    assert m.tiles[1][1].blocked is False  # Floor
    assert m.tiles[2][2].blocked is False  # Floor
    assert m.tiles[3][3].blocked is False  # Floor
    assert m.tiles[4][4].blocked is True  # Wall


def test_map_mk_tunnel_simple_horz_first():
    m = maps.Map(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    r1 = rect.Rect(0, 0, 4, 4)
    r2 = rect.Rect(8, 8, 4, 4)
    m.mk_tunnel_simple(r1, r2)

    cx1, cy1 = r1.center()
    cx2, cy2 = r2.center()

    # Test the horizontal tunnel
    for x in range(cx1, cx2 + 1):
        assert m.tiles[x][cy1].blocked is False # Floor

    # Test the vertical tunnel
    for y in range(cy1, cy2 + 1):
        assert m.tiles[cx2][y].blocked is False # Floor


def test_map_mk_tunnel_simple_vert_first():
    m = maps.Map(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    r1 = rect.Rect(0, 0, 4, 4)
    r2 = rect.Rect(8, 8, 4, 4)
    m.mk_tunnel_simple(r1, r2, horz_first=False)

    cx1, cy1 = r1.center()
    cx2, cy2 = r2.center()

    # Test the vertical tunnel
    for y in range(cy1, cy2 + 1):
        assert m.tiles[cx1][y].blocked is False # Floor

    # Test the horizontal tunnel
    for x in range(cx1, cx2 + 1):
        assert m.tiles[x][cy2].blocked is False # Floor


def test_map_dig_h_tunnel():
    m = maps.Map(width=10, height=10)
    m.dig_h_tunnel(x1=0, x2=8, y=0)
    assert m.tiles[0][0].blocked is False
    assert m.tiles[8][0].blocked is False
    assert m.tiles[9][0].blocked is True


def test_map_dig_h_tunnel_reversed_parameters():
    m = maps.Map(width=10, height=10)
    m.dig_h_tunnel(x1=8, x2=0, y=0)
    assert m.tiles[0][0].blocked is False
    assert m.tiles[8][0].blocked is False
    assert m.tiles[9][0].blocked is True


def test_map_dig_v_tunnel():
    m = maps.Map(width=10, height=10)
    m.dig_v_tunnel(y1=0, y2=8, x=0)
    assert m.tiles[0][0].blocked is False
    assert m.tiles[0][8].blocked is False
    assert m.tiles[0][9].blocked is True


def test_map_dig_v_tunnel_reversed_parameters():
    m = maps.Map(width=10, height=10)
    m.dig_v_tunnel(y1=8, y2=0, x=0)
    assert m.tiles[0][0].blocked is False
    assert m.tiles[0][8].blocked is False
    assert m.tiles[0][9].blocked is True

# def test_map_get_last_room_center():
# def test_map_make_map():
# def test_map_populate():

def test_map_is_occupied__not_occupied_returns_False():
    # Test if there are any entities at the coordinates
    m = maps.Map(width=10, height=10)
    result = m.is_occupied(0, 0)
    assert result is False

def test_map_is_occupied__occupied_return_True():
    # Test if there are any entities at the coordinates
    m = maps.Map(width=10, height=10)
    x, y = 0, 0
    hero = entity.Entity(x, y, '@', None, 'Player', human=True)
    m.entities.append(hero)
    assert m.is_occupied(x, y) is True


def test_map_get_random_non_wall_loc__default_map_returns_None():
    m = maps.Map(width=10, height=10)
    # There should be no non-Wall tiles in a default map
    assert m.get_random_non_wall_loc() is None

def test_map_get_random_non_wall_loc__returns_non_wall():
    m = maps.Map(width=10, height=10)
    m.tiles[0][0].blocked = False
    result = m.get_random_non_wall_loc()
    assert result == (0, 0)

def test_map_get_random_room_loc__map_corner():
    m = maps.Map(width=50, height=50)
    r = rect.Rect(x=0, y=0, w=5, h=5)
    result_x, result_y = m.get_random_room_loc(r)
    min_x = r.x1 + config.NW_OFFSET
    max_x = r.x2 - config.SE_OFFSET
    min_y = r.y1 + config.NW_OFFSET
    max_y = r.y2 - config.SE_OFFSET

    assert result_x >= min_x and result_x <= max_x
    assert result_y >= min_y and result_y <= max_y


def test_map_get_random_room_loc__map_middle():
    m = maps.Map(width=50, height=50)
    r = rect.Rect(x=10, y=10, w=15, h=5)
    result_x, result_y = m.get_random_room_loc(r)
    min_x = r.x1 + config.NW_OFFSET
    max_x = r.x2 - config.SE_OFFSET
    min_y = r.y1 + config.NW_OFFSET
    max_y = r.y2 - config.SE_OFFSET

    assert result_x >= min_x and result_x <= max_x
    assert result_y >= min_y and result_y <= max_y


def test_map_place_entities_no_entities_appear_in_Wall():
    m = maps.Map(width=50, height=50)
    r = rect.Rect(0, 0, 5, 5)
    m.dig_room(r)
    m.place_entities(r)

    for e in m.entities:
        assert m.tiles[e.x][e.y].blocked is False

# def test_map_place_stairs_down():
# def test_map_place_stairs_up():
