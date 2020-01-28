import pytest
from pytest_mock import mocker
from ..src import entity
from ..src import factory
from ..src import stages
from ..src import tile
from ..src.config import RenderOrder
from ..src.components import Fighter, Item, Level, Equipment, Equippable, ApproachAI
from ..src.inventory import Inventory
from ..src.stairs import Stairs


@pytest.fixture
def open_map():
    # todo: When we revamp map - remove this fixture!!!!!!!!!!!!!!!!!!!!!!!!
    m = stages.Stage(10, 10)
    m.tiles = [[tile.Tile(False) for y in range(10)] for x in range(10)]
    return m


@pytest.fixture
def orc():
    return factory.mk_entity('orc', 0, 0)



def test_Entity_init__defaults():
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player')
    assert e.x == 0
    assert e.y == 0
    assert e.char == '@'
    assert e.color is None
    assert e.name == 'Player'


def test_Entity_init__components_dict():
    e = entity.Entity(x=0, y=0)
    assert e.components == {'x': 0, 'y': 0}


@pytest.mark.skip(reason='implement after ecs is mostly done.')
def test_Entity_init__kwargs_become_components():
    pass


def test_Entity_str__has_name():
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player')
    assert str(e) == 'Player'

def test_Entity_str__unnamed():
    e = entity.Entity(x=0, y=0, char='@', color=None)
    assert str(e) == 'Unnamed'


def test_Entity_init__add_comp__1_kwarg():
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player')
    e.add_comp(a=1)
    assert e.components['a'] == 1


def test_Entity_init__add_comp__2_kwargs():
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player')
    e.add_comp(a=1, b=2)
    assert e.components['a'] == 1
    assert e.components['b'] == 2


def test_Entity_init__add_comp__already_exists_and_replaces():
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player')
    e.add_comp(a=1)
    e.add_comp(a=2)
    assert e.components['a'] == 2


def test_Entity_init__has_comp():
    e = entity.Entity(x=0, y=0)
    assert e.has_comp('x')
    assert e.has_comp('y')


def test_Entity_init__rm_comp__success_removes_component():
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player')
    e.add_comp(a=1)
    e.rm_comp('a')
    assert 'a' not in e.components


def test_Entity_init__rm_comp__success_returns_True():
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player')
    e.add_comp(a=1)
    result = e.rm_comp('a')
    assert result


def test_Entity_init__rm_comp__fail_returns_False():
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player')
    result = e.rm_comp('z')
    # Raise exception?


def test_Entity_init__getattr__returns_component_value():
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player')
    e.add_comp(a=1)
    assert e.a == 1


def test_Entity_init__getattr__DNE_returns_None():
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player')
    with pytest.raises(AttributeError):
        result = e.a


def test_Entity_init__blocks_component():
    e = entity.Entity(x=0, y=0, char='@', color=None, name='Player', blocks=True)

    assert e.blocks
    assert 'blocks' in e.components


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
