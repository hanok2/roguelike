import pytest
from pytest_mock import mocker

from ..src import entity
from ..src import maps
from ..src import config
from ..src import rect

DEFAULT_LENGTH = 50
INVALID_LENGTH = 2

@pytest.fixture
def basic_hero():
    return entity.Entity(0, 0, '@', None, 'Player', human=True)


"""Tests for class Dungeon(object):"""

def test_dungeon_init__beginning_variables(basic_hero):
    d = maps.Dungeon(basic_hero)
    assert d.hero is basic_hero
    assert d.current_lvl == 0


def test_dungeon_init__1_level_exists(basic_hero):
    # Make sure 1 level is generated on init
    d = maps.Dungeon(basic_hero)
    assert len(d.levels) == 1


@pytest.mark.skip(reason='Cannot implement yet because mocking causes problem with hero access to levels list.')
def test_dungeon_init__generate_next_lvl_called(mocker, basic_hero):
    mocker.patch.object(maps.Dungeon, 'generate_next_level')
    d = maps.Dungeon(basic_hero)
    d.generate_next_level.assert_called_once()


def test_dungeon_init__hero_exists_on_map(basic_hero):
    d = maps.Dungeon(basic_hero)
    m = d.current_map()
    assert any([True for e in m.entities if e.human])


def test_dungeon_init__move_hero_called(mocker, basic_hero):
    mocker.patch.object(maps.Dungeon, 'move_hero')
    d = maps.Dungeon(basic_hero)
    d.move_hero.assert_called_once()


def test_dungeon_init__populate_called(mocker, basic_hero):
    mocker.patch.object(maps.Map, 'populate')
    d = maps.Dungeon(basic_hero)
    m = d.current_map()

    m.populate.assert_called_once()


def test_current_map__1_level(basic_hero):
    d = maps.Dungeon(basic_hero)
    m = d.current_map()
    assert m.dungeon_lvl == d.current_lvl + 1


def test_current_map__2_levels(basic_hero):
    d = maps.Dungeon(basic_hero)
    d.generate_next_level()

    m = d.current_map()
    assert m.dungeon_lvl == d.current_lvl + 1

    d.current_lvl = 1
    m = d.current_map()
    assert m.dungeon_lvl == d.current_lvl + 1


# def test_place_hero(, level):
    # Should this take the hero as a parameter?
    # Test that the hero is put somewhere

def test_generate_next_level__levels_increases(basic_hero):
    d = maps.Dungeon(basic_hero)
    assert len(d.levels) == 1
    d.generate_next_level()

    assert len(d.levels) == 2


def test_generate_next_level__maps_are_numbered_correctly(basic_hero):
    d = maps.Dungeon(basic_hero)
    assert d.levels[0].dungeon_lvl == 1
    d.generate_next_level()

    assert d.levels[1].dungeon_lvl == 2


def test_hero_at_stairs__valid_returns_True(basic_hero):
    d = maps.Dungeon(basic_hero)
    down_stair = d.current_map().find_stair('>')
    d.hero.x, d.hero.y = down_stair.x, down_stair.y
    assert d.hero_at_stairs('>')


def test_hero_at_stairs__invalid_returns_False(basic_hero):
    d = maps.Dungeon(basic_hero)
    assert d.hero_at_stairs('>') is False


def test_hero_at_stairs__starting_upstair_returns_True(basic_hero):
    d = maps.Dungeon(basic_hero)
    # Hero starts on an upstair, so this should be True.
    assert d.hero_at_stairs('<')


def test_move_downstairs__not_on_down_stair_returns_False(basic_hero):
    d = maps.Dungeon(basic_hero)
    d.generate_next_level()

    result = d.move_downstairs()
    assert result is False


def test_move_downstairs__hero_moved_to_next_upstair(basic_hero):
    d = maps.Dungeon(basic_hero)
    down_stair = d.current_map().find_stair('>')
    d.hero.x, d.hero.y = down_stair.x, down_stair.y
    d.generate_next_level()

    d.move_downstairs()
    up_stair = d.current_map().find_stair('<')

    assert d.hero.x == up_stair.x
    assert d.hero.y == up_stair.y


def test_move_downstairs__dungeon_lvl_incremented(basic_hero):
    d = maps.Dungeon(basic_hero)
    prev_lvl = d.current_lvl
    down_stair = d.current_map().find_stair('>')
    d.hero.x, d.hero.y = down_stair.x, down_stair.y
    d.generate_next_level()

    d.move_downstairs()

    assert d.current_lvl == prev_lvl + 1

def test_move_downstairs__success_returns_True(basic_hero):
    d = maps.Dungeon(basic_hero)
    prev_lvl = d.current_lvl
    down_stair = d.current_map().find_stair('>')
    d.hero.x, d.hero.y = down_stair.x, down_stair.y
    d.generate_next_level()

    assert d.move_downstairs()


def test_move_upstairs__not_on_up_stair_returns_False(basic_hero):
    d = maps.Dungeon(basic_hero)
    down_stair = d.current_map().find_stair('>')

    # Move hero to downstair (won't be on upstair)
    d.hero.x, d.hero.y = down_stair.x, down_stair.y
    assert d.move_upstairs() is False


def test_move_upstairs__hero_moved_to_prev_downstair(basic_hero):
    d = maps.Dungeon(basic_hero)
    down_stair = d.current_map().find_stair('>')
    d.hero.x, d.hero.y = down_stair.x, down_stair.y
    d.generate_next_level()

    # Move the hero downstairs first
    d.move_downstairs()

    # Hero moves back to previous down-stair
    d.move_upstairs()
    assert d.hero.x == down_stair.x
    assert d.hero.y == down_stair.y


def test_move_upstairs__success_returns_True(basic_hero):
    d = maps.Dungeon(basic_hero)
    down_stair = d.current_map().find_stair('>')
    d.hero.x, d.hero.y = down_stair.x, down_stair.y
    d.generate_next_level()

    d.move_downstairs()
    assert d.move_upstairs()


# def test_move_upstairs__when_at_the_top_lvl():
    # Return False?

# Wait on this test - might want to remove some calls from Dungeon init
# def test_move_hero__hero_not_placed_yet(basic_hero):
    # d = maps.Dungeon(basic_hero)

def test_move_hero__to_wall_returns_False(basic_hero):
    d = maps.Dungeon(basic_hero)
    m = maps.Map(10, 10, 2)
    d.levels.append(m)
    assert d.move_hero(dest_lvl=1, dest_x=0, dest_y=0) is False


def test_move_hero__to_occupied_spot_returns_False(basic_hero):
    d = maps.Dungeon(basic_hero)
    rnd_monster = [e for e in d.current_map().entities if e.ai].pop()
    dest_x = rnd_monster.x
    dest_y = rnd_monster.y
    assert d.move_hero(dest_lvl=0, dest_x=dest_x, dest_y=dest_y) is False


def test_move_hero__same_floor_returns_True(basic_hero):
    d = maps.Dungeon(basic_hero)
    dest_x, dest_y = d.current_map().get_random_open_spot()
    assert d.move_hero(dest_lvl=0, dest_x=dest_x, dest_y=dest_y)


def test_move_hero__same_floor_hero_xy_updated(basic_hero):
    d = maps.Dungeon(basic_hero)
    dest_x, dest_y = d.current_map().get_random_open_spot()
    d.move_hero(dest_lvl=0, dest_x=dest_x, dest_y=dest_y)
    assert d.hero.x == dest_x
    assert d.hero.y == dest_y


def test_move_hero__same_floor_lvl_remains_same(basic_hero):
    d = maps.Dungeon(basic_hero)
    d_lvl = d.current_lvl
    dest_x, dest_y = d.current_map().get_random_open_spot()
    d.move_hero(dest_lvl=0, dest_x=dest_x, dest_y=dest_y)
    assert d.current_lvl == d_lvl


def test_move_hero__diff_floor_returns_True(basic_hero):
    dest_lvl = 1
    d = maps.Dungeon(basic_hero)
    d.generate_next_level()

    dest_x, dest_y = d.levels[dest_lvl].get_random_open_spot()
    assert d.move_hero(dest_lvl=dest_lvl, dest_x=dest_x, dest_y=dest_y)


def test_move_hero__diff_floor_hero_xy_updated(basic_hero):
    dest_lvl = 1
    d = maps.Dungeon(basic_hero)
    d.generate_next_level()

    dest_x, dest_y = d.levels[dest_lvl].get_random_open_spot()
    d.move_hero(dest_lvl=dest_lvl, dest_x=dest_x, dest_y=dest_y)
    assert d.hero.x == dest_x
    assert d.hero.y == dest_y


def test_move_hero__diff_floor_dungeon_lvl_updated(basic_hero):
    dest_lvl = 1
    d = maps.Dungeon(basic_hero)
    d.generate_next_level()

    dest_x, dest_y = d.levels[dest_lvl].get_random_open_spot()
    d.move_hero(dest_lvl=dest_lvl, dest_x=dest_x, dest_y=dest_y)
    assert d.current_lvl == dest_lvl


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

def test_map_rm_hero_if_present_returns_True(basic_hero):
    m = maps.Map(width=3, height=3)
    m.entities.append(basic_hero)
    result = m.rm_hero()
    assert result is True
    # Also check there is no hero in the entities
    assert basic_hero not in m.entities


def test_map_find_stair__down_stair_returns_entity():
    m = maps.Map(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    m.make_map()
    stair = [e for e in m.entities if e.stair_down].pop()
    result = m.find_stair('>')
    assert result == stair

def test_map_find_stair__up_stair_returns_entity():
    m = maps.Map(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    m.make_map()
    stair = [e for e in m.entities if e.stair_up].pop()
    result = m.find_stair('<')
    assert result == stair


def test_map_find_stair__DNE_returns_None():
    m = maps.Map(width=DEFAULT_LENGTH, height=DEFAULT_LENGTH)
    assert m.find_stair('>') is None
    assert m.find_stair('<') is None

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

def test_map_make_map__has_at_least_2_rooms():
    m = maps.Map(width=50, height=50)
    m.make_map()
    assert len(m.rooms) >= 2


def test_map_make_map__has_up_stair():
    m = maps.Map(width=50, height=50)
    m.make_map()
    assert any(True for e in m.entities if e.stair_up)


def test_map_make_map__has_down_stair():
    m = maps.Map(width=50, height=50)
    m.make_map()
    assert any(True for e in m.entities if e.stair_down)


def test_map_make_map__up_and_down_stairs_in_diff_rooms():
    m = maps.Map(width=50, height=50)
    m.make_map()
    stair_up = [e for e in m.entities if e.stair_up].pop()
    stair_down = [e for e in m.entities if e.stair_down].pop()

    stair_up_room = None
    for room in m.rooms:
        if room.within(stair_up.x, stair_up.y):
            stair_up_room = room
            break
    # The coordinates of stair_down should not be within the same room as
    # stair_up
    assert not stair_up_room.within(stair_down.x, stair_down.y)


# def test_map_make_map__all_rooms_interconnected():
    # Need a pathfinding algorithm??


def test_map_populate__calls_place_entities_and_items(mocker):
    m = maps.Map(width=50, height=50)
    m.make_map()
    mocker.patch.object(m, 'place_monsters')
    mocker.patch.object(m, 'place_items')
    m.populate()

    m.place_monsters.assert_called_once_with()
    m.place_items.assert_called()


def test_map_populate__no_rooms_does_not_call_place_items(mocker):
    m = maps.Map(width=50, height=50)
    mocker.patch.object(m, 'place_monsters')
    mocker.patch.object(m, 'place_items')
    m.populate()

    m.place_monsters.assert_called_once_with()
    assert not m.place_items.called


def test_map_is_occupied__not_occupied_returns_False():
    # Test if there are any entities at the coordinates
    m = maps.Map(width=10, height=10)
    result = m.is_occupied(0, 0)
    assert result is False

def test_map_is_occupied__occupied_return_True(basic_hero):
    # Test if there are any entities at the coordinates
    m = maps.Map(width=10, height=10)
    x, y = 0, 0
    m.entities.append(basic_hero)
    assert m.is_occupied(x, y) is True


def test_get_random_open_spot__all_wall_returns_None():
    m = maps.Map(width=10, height=10)
    assert m.get_random_open_spot() is None


def test_get_random_open_spot__single_spot():
    m = maps.Map(width=10, height=10)
    m.tiles[0][0].blocked = False
    assert m.get_random_open_spot() == (0, 0)


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


def test_map_place_monsters__all_wall_tiles():
    m = maps.Map(width=50, height=50)
    m.place_monsters()

    # Check that no entities are on Wall tiles
    for e in m.entities:
        assert m.tiles[e.x][e.y].blocked is False


def test_map_place_monsters_no_entities_appear_in_Wall():
    m = maps.Map(width=50, height=50)
    m.make_map()
    m.place_monsters()

    # Check that no entities are on Wall tiles
    for e in m.entities:
        assert m.tiles[e.x][e.y].blocked is False


def test_map_place_items_no_entities_appear_in_Wall():
    m = maps.Map(width=50, height=50)
    r = rect.Rect(0, 0, 5, 5)
    m.dig_room(r)
    m.place_items(r)

    # Check that no entities are on Wall tiles
    for e in m.entities:
        assert m.tiles[e.x][e.y].blocked is False


def test_map_place_stairs_down_on_floor__valid_pos():
    m = maps.Map(width=50, height=50)
    r = rect.Rect(0, 0, 5, 5)
    m.dig_room(r)
    x, y = r.center()
    result = m.place_stairs_down(x, y)

    assert result.x == x
    assert result.y == y
    assert result in m.entities


def test_map_place_stairs_down_on_wall_raises_exception():
    m = maps.Map(width=50, height=50)
    x, y = 0, 0
    with pytest.raises(ValueError):
        m.place_stairs_down(x, y)


def test_map_place_stairs_up__valid_pos():
    m = maps.Map(width=50, height=50)
    r = rect.Rect(0, 0, 5, 5)
    m.dig_room(r)
    x, y = r.center()
    result = m.place_stairs_up(x, y)

    assert result.x == x
    assert result.y == y
    assert result in m.entities


def test_map_place_stairs_up_on_wall_raises_exception():
    m = maps.Map(width=50, height=50)
    x, y = 0, 0
    with pytest.raises(ValueError):
        m.place_stairs_up(x, y)
