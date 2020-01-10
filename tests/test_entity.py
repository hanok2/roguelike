import pytest
from ..src import entity
from ..src.render_functions import RenderOrder
from ..src.components import Fighter, Item, Level, Equipment, Equippable, ApproachingBehavior
from ..src.inventory import Inventory
from ..src.stairs import Stairs


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


# def move_towards(self, target_x, target_y, game_map, entities):
    # Move to map???
# def move_astar(self, target, entities, game_map):
    # Move to map???

# def distance(self, x, y):
# Move to map

# def distance_to(self, other):
# Move to map
