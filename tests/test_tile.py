import pytest
from ..src import tile

def test_Tile_init__blocks_isnt_bool_raises_exception():
    with pytest.raises(ValueError):
        tile.Tile(blocks=None)


def test_Tile_init__blocks_True():
    t = tile.Tile(blocks=True)
    assert t.blocks
    assert t.block_sight


def test_Tile_init__blocks_False():
    t = tile.Tile(blocks=False)
    assert t.blocks is False
    assert t.block_sight is False


def test_Tile_init__block_sight_True():
    t = tile.Tile(blocks=True, block_sight=True)
    assert t.blocks
    assert t.block_sight


def test_Tile_init__block_sight_False():
    t = tile.Tile(blocks=True, block_sight=False)
    assert t.blocks
    assert t.block_sight is False


def test_Tile_init__explored_is_False():
    t = tile.Tile(blocks=True)
    assert t.explored is False
