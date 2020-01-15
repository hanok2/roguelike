import tcod
from ..src import stairs
from ..src.config import RenderOrder


# Eventually - turn Stairs into a subclass of Tile

# Test it's a subclass of Entity
# Needs a destination floor
# Needs a current_floor

def test_Stairs_init():
    s = stairs.Stairs(floor=0)
    assert s.floor == 0


def test_StairUp_init():
    s = stairs.StairUp(x=0, y=0, floor=1)
    assert s.x == 0
    assert s.y == 0
    assert s.char == '<'
    assert s.color == tcod.white
    assert s.name == 'Stairs Up'
    assert s.render_order == RenderOrder.STAIRS
    assert s.stair_up
    assert s.stair_up.floor == 1


def test_StairsDown_init():
    s = stairs.StairDown(x=0, y=0, floor=1)
    assert s.x == 0
    assert s.y == 0
    assert s.char == '>'
    assert s.color == tcod.white
    assert s.name == 'Stairs Down'
    assert s.render_order == RenderOrder.STAIRS
    assert s.stair_down
    assert s.stair_down.floor == 1
