import pytest
from ..src import actions
from ..src import factory
from ..src import player
from ..src import stages
from ..src import tile


@pytest.fixture
def hero():
    return player.Player(x=1, y=1)


@pytest.fixture
def walk_map():
    m = stages.Stage(3, 3)
    # Set all tiles to non-blocking
    m.tiles = [[tile.Tile(False) for y in range(10)] for x in range(10)]
    m.tiles[1][2].blocked = True  # Add a wall

    orc = factory.mk_entity('orc', 2, 1)
    potion = factory.mk_entity('healing_potion', 1, 0)
    m.entities.extend([orc, potion])
    return m


""" Tests for WalkAction """


# Don't Need?
# def test_WalkAction__not_heros_turn__returns_False(walk_map):

def test_WalkAction__is_subclass_of_Action():
    walk = actions.WalkAction(dx=1, dy=0)
    assert isinstance(walk, actions.Action)


def test_WalkAction__consumed_turn():
    walk = actions.WalkAction(dx=1, dy=0)
    assert walk.consumes_turn


def test_WalkAction__blocked_by_monster__returns_AttackAction(walk_map, hero):
    walk_map.entities.append(hero)

    walk = actions.WalkAction(dx=1, dy=0)
    result = walk.perform(walk_map, hero)
    assert result == 'attack!'


def test_WalkAction__blocked_by_wall__msg_and_returns_fail(walk_map, hero):
    walk_map.entities.append(hero)

    walk = actions.WalkAction(dx=0, dy=1)
    result = walk.perform(walk_map, hero)
    assert result is False


def test_WalkAction__unblocked__performs_walk_and_returns_True(walk_map, hero):
    walk_map.entities.append(hero)
    walk = actions.WalkAction(dx=-1, dy=-1)
    result = walk.perform(walk_map, hero)
    assert result


@pytest.mark.skip(reason='we do not have an item checking method yet for stages.')
def test_WalkAction__over_item__returns_walkover_msg(walk_map, hero):
    walk_map.entities.append(hero)
    walk = actions.WalkAction(dx=0, dy=-1)
    result = walk.perform(walk_map, hero)
    assert result == 'you see a healing position'


def test_WalkAction__more_than_1_sq_away__raise_exception(walk_map):
    walk_map.entities.append(hero)
    with pytest.raises(ValueError):
        actions.WalkAction(dx=-2, dy=-1)


""" Tests for WaitAction """


def test_WaitAction__is_subclass_of_Action():
    wait = actions.WaitAction()
    assert isinstance(wait, actions.Action)


def test_WalkAction__consumes_turn():
    wait = actions.WaitAction()
    assert wait.consumes_turn


def test_WaitAction__returns_True():
    wait = actions.WaitAction()
    assert wait.perform()

