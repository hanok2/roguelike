import pytest
from ..src import entity
from ..src import maps
from ..src import tile

from .test_death_functions import orc
from ..src.render_functions import RenderOrder
from ..src.components import Fighter, Item, Level, Equipment, Equippable, ApproachingBehavior
from ..src.inventory import Inventory
from ..src.stairs import Stairs

@pytest.fixture
def open_map():
    # todo: When we revamp map - remove this fixture!!!!!!!!!!!!!!!!!!!!!!!!
    m = maps.Map(10, 10)
    m.tiles = [[tile.Tile(False) for y in range(10)] for x in range(10)]
    return m


def test_Entity_init__defaults():
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player')
    assert e.x == 0
    assert e.y == 0
    assert e.char == '@'
    assert e.color is None
    assert e.name == 'Player'

def test_Entity_init__blocks():
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player', blocks=True)
    assert e.blocks


def test_Entity_init__render_order():
    r_order = RenderOrder.CORPSE
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player', render_order=r_order)
    assert e.render_order == r_order
    assert e.render_order in RenderOrder


def test_Entity_init__fighter():
    fighter_comp = Fighter(hp=100, defense=1, power=2)
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player', fighter=fighter_comp)
    assert isinstance(e.fighter, Fighter)


def test_Entity_init__ai():
    ai = ApproachingBehavior()
    ai.owner = 'bob'
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player', ai=ai)
    assert e.ai == ai


def test_Entity_init__item():
    item_comp = Item()
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player', item=item_comp)
    assert isinstance(e.item, Item)


def test_Entity_init__inv():
    inv_comp = Inventory(26)
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player', inv=inv_comp)
    assert isinstance(e.inv, Inventory)


def test_Entity_init__stair_down():
    stair_comp = Stairs(floor=0)
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player', stair_down=stair_comp)
    assert isinstance(e.stair_down, Stairs)


def test_Entity_init__stair_up():
    stair_comp = Stairs(floor=0)
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player', stair_up=stair_comp)
    assert isinstance(e.stair_up, Stairs)


def test_Entity_init__lvl():
    lvl_comp = Level()
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player', lvl=lvl_comp)
    assert isinstance(e.lvl, Level)


def test_Entity_init__equipment():
    equipment_comp = Equipment()
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player', equipment=equipment_comp)
    assert isinstance(e.equipment, Equipment)


def test_Entity_init__equippable():
    equippable_comp = Equippable(1)
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player', equippable=equippable_comp)
    assert isinstance(e.equippable, Equippable)


def test_Entity_init__human():
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player', human=True)
    assert e.human


def test_Entity_move__to_a_negative_x():
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player')
    with pytest.raises(ValueError):
        e.move(-1, 2)

def test_Entity_move__to_a_negative_y():
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player')
    with pytest.raises(ValueError):
        e.move(1, -2)

def test_Entity_move__positive_values():
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player')
    e.move(1, 2)
    assert e.x == 1
    assert e.y == 2


def test_Entity_move__negative_values():
    e = entity.Entity(x=10, y=10, char='@', color=None, name='Player')
    e.move(-1, 2)
    assert e.x == 9
    assert e.y == 12


def test_Entity_move_towards__negative_target_x_raises_exception(open_map):
    e = entity.Entity(x=10, y=10, char='@', color=None, name='Player')
    with pytest.raises(ValueError):
        e.move_towards(-1, 0, open_map)


def test_Entity_move_towards__negative_target_y_raises_exception(open_map):
    e = entity.Entity(x=10, y=10, char='@', color=None, name='Player')
    with pytest.raises(ValueError):
        e.move_towards(0, -1, open_map)


def test_Entity_move_towards__invalid_coordinates_raises_exception(open_map):
    e = entity.Entity(x=10, y=10, char='@', color=None, name='Player')
    with pytest.raises(IndexError):
        e.move_towards(100, 100, open_map)


def test_Entity_move_towards__blocked_doesnt_move():
    m = maps.Map(10, 10)
    e = entity.Entity(x=5, y=5, char='@', color=None, name='Player')
    e.move_towards(6, 6, m)
    assert e.x == 5
    assert e.y == 5


def test_Entity_move_towards__occupied_doesnt_move(open_map, orc):
    e = entity.Entity(x=1, y=1, char='@', color=None, name='Player')
    open_map.entities.append(e)
    open_map.entities.append(orc)
    e.move_towards(orc.x, orc.y, open_map)
    assert e.x == 1
    assert e.y == 1


def test_Entity_move_towards__target_north(open_map):
    e = entity.Entity(x=5, y=5, char='@', color=None, name='Player')
    e.move_towards(5, 4, open_map)
    assert e.x == 5
    assert e.y == 4


def test_Entity_move_towards__target_south(open_map):
    e = entity.Entity(x=5, y=5, char='@', color=None, name='Player')
    e.move_towards(5, 6, open_map)
    assert e.x == 5
    assert e.y == 6


def test_Entity_move_towards__target_east(open_map):
    e = entity.Entity(x=5, y=5, char='@', color=None, name='Player')
    e.move_towards(6, 5, open_map)
    assert e.x == 6
    assert e.y == 5


def test_Entity_move_towards__target_west(open_map):
    e = entity.Entity(x=5, y=5, char='@', color=None, name='Player')
    e.move_towards(4, 5, open_map)
    assert e.x == 4
    assert e.y == 5


def test_Entity_move_towards__target_NW(open_map):
    e = entity.Entity(x=5, y=5, char='@', color=None, name='Player')
    e.move_towards(4, 4, open_map)
    assert e.x == 4
    assert e.y == 4


def test_Entity_move_towards__target_NE(open_map):
    e = entity.Entity(x=5, y=5, char='@', color=None, name='Player')
    e.move_towards(6, 4, open_map)
    assert e.x == 6
    assert e.y == 4


def test_Entity_move_towards__target_SE(open_map):
    e = entity.Entity(x=5, y=5, char='@', color=None, name='Player')
    e.move_towards(6, 6, open_map)
    assert e.x == 6
    assert e.y == 6


def test_Entity_move_towards__target_SW(open_map):
    e = entity.Entity(x=5, y=5, char='@', color=None, name='Player')
    e.move_towards(4, 6, open_map)
    assert e.x == 4
    assert e.y == 6

# def move_astar(self, target, entities, game_map):
    # Move to map???

# def distance(self, x, y):
# Move to map

# def distance_to(self, other):
# Move to map
