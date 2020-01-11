import pytest
from ..src import tile

def test_Tile_init__blocked_isnt_bool_raises_exception():
    with pytest.raises(ValueError):
        tile.Tile(blocked=None)


def test_Tile_init__blocked_True():
    t = tile.Tile(blocked=True)
    assert t.blocked
    assert t.block_sight


def test_Tile_init__blocked_False():
    t = tile.Tile(blocked=False)
    assert t.blocked is False
    assert t.block_sight is False


def test_Tile_init__block_sight_True():
    t = tile.Tile(blocked=True, block_sight=True)
    assert t.blocked
    assert t.block_sight


def test_Tile_init__block_sight_False():
    t = tile.Tile(blocked=True, block_sight=False)
    assert t.blocked
    assert t.block_sight is False


def test_Tile_init__explored_is_False():
    t = tile.Tile(blocked=True)
    assert t.explored is False
