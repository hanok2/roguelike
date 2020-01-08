from ..src import maps
from ..src import config


"""Tests for class Dungeon(object):"""

# def test_dungeon_init__():
# def test_current_map():
# def test_place_hero(, level):
# def test_generate_next_level():
# def test_move_downstairs():
# def test_move_upstairs():


"""Tests for class Map(object):"""

def test_map_init():
    map_len = 50
    result = maps.Map(width=map_len, height=map_len)
    assert len(result.tiles) == map_len
    assert result.entities == []
    assert result.rooms == []
    assert result.dungeon_lvl == config.DEFAULT_DUNGEON_LVL


# width can't be < 3
# height can't be < 3
# dungeon_lvl can't be less than 0


# def test_map_rm_hero():
# def test_map_find_down_stair():
# def test_map_initialize_tiles():
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
