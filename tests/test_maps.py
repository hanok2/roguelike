import pytest
from ..src import maps
from ..src import config

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
    result = maps.Map(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    assert len(result.tiles) == DEFAULT_LENGTH
    assert result.entities == []
    assert result.rooms == []
    assert result.dungeon_lvl == config.DEFAULT_DUNGEON_LVL

def test_map_init_invalid_width_raises_exception():
    with pytest.raises(ValueError):
        maps.Map(width=INVALID_LENGTH, height=DEFAULT_LENGTH)

def test_map_init_invalid_height_raises_exception():
    with pytest.raises(ValueError):
        maps.Map(width=DEFAULT_LENGTH, height=INVALID_LENGTH)

def test_map_init_invalid_dungeon_lvl_raises_exception():
    with pytest.raises(ValueError):
        maps.Map(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH, dungeon_lvl=0)

# def test_map_rm_hero():
# def test_map_find_down_stair():

def test_map_initialize_tiles():
    # Test that all initialized tiles are True (aka: Wall)
    m = maps.Map(width=3, height=3)
    result = m.initialize_tiles()
    assert all(t for t in result)


# def test_map_is_blocked():
# def test_map_mk_room():
# def test_map_dig_room():
# def test_map_mk_tunnel_simple():
# def test_map_dig_h_tunnel():
# def test_map_dig_v_tunnel():
# def test_map_get_last_room_center():
# def test_map_make_map():
# def test_map_populate():
# def test_map_place_entities():
# def test_map_place_stairs_down():
# def test_map_place_stairs_up():
