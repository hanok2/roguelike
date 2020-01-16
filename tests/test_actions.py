import pytest
from ..src import actions
from ..src import config
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
    m.entities.extend([potion, orc])
    return m


""" Tests for WalkAction """


# Don't Need?
# def test_WalkAction__not_heros_turn__returns_False(walk_map):

def test_WalkAction__is_subclass_of_Action():
    walk = actions.WalkAction(dx=1, dy=0)
    assert isinstance(walk, actions.Action)


def test_WalkAction__consumes_turn():
    walk = actions.WalkAction(dx=1, dy=0)
    assert walk.consumes_turn


def test_WalkAction__results_is_empty():
    walk = actions.WalkAction(dx=1, dy=0)
    assert walk.results == []


def test_WalkAction__blocked_by_monster__returns_AttackAction(walk_map, hero):
    walk_map.entities.append(hero)

    walk = actions.WalkAction(dx=1, dy=0)
    walk.perform(walk_map, hero)
    assert walk.results == [{'alternate': 'AttackAction'}]


def test_WalkAction__blocked_by_wall__msg_and_returns_fail(walk_map, hero):
    walk_map.entities.append(hero)

    walk = actions.WalkAction(dx=0, dy=1)
    walk.perform(walk_map, hero)
    assert walk.results == [{'msg': 'You walk into the wall...'}]


def test_WalkAction__unblocked__performs_walk_and_returns_True(walk_map, hero):
    walk_map.entities.append(hero)
    walk = actions.WalkAction(dx=-1, dy=-1)
    walk.perform(walk_map, hero)
    assert walk.results == []


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


def test_WaitAction__consumes_turn():
    wait = actions.WaitAction()
    assert wait.consumes_turn


def test_WaitAction__results_is_empty():
    wait = actions.WaitAction()
    assert wait.results == []


def test_WaitAction__returns_True():
    wait = actions.WaitAction()
    assert wait.perform()


""" Tests for PickupAction """


def test_PickupAction__is_subclass_of_Action():
    pickup = actions.PickupAction()
    assert isinstance(pickup, actions.Action)


def test_PickupAction__consumes_turn():
    pickup = actions.PickupAction()
    assert pickup.consumes_turn


def test_PickupAction__results_is_empty():
    pickup = actions.PickupAction()
    assert pickup.results == []


def test_PickupAction__item(walk_map, hero):
    hero.x, hero.y = 1, 0   # Move the player to the same tile as the potion
    walk_map.entities.append(hero)
    pickup = actions.PickupAction()
    pickup.perform(walk_map, hero)

    # todo: Fix this later - use a Stage.get_entities function instead
    potion = walk_map.entities[0]
    assert potion.name == 'Healing potion'

    assert pickup.results == [{'item_added': potion, 'msg': 'You pick up the Healing potion.'}]


@pytest.mark.skip(reason='we dont have a Multiple Pickup Menu yet.')
def test_PickupAction__multiple_items(walk_map, hero):
    walk_map.entities.append(hero)
    # Add another potion to the same tile
    walk_map.entities.append(factory.mk_entity('healing_potion', 1, 0))
    pickup = actions.PickupAction()
    pickup.perform(walk_map, hero)

    # pickup.results[0] = {'item_added': None, 'msg': INV_FULL_MSG}
    assert pickup.results == 'pickup menu'


def test_PickupAction__no_items_at_entity_location(walk_map, hero):
    walk_map.entities.append(hero)
    pickup = actions.PickupAction()
    pickup.perform(walk_map, hero)

    assert pickup.results == [{'msg': 'There is nothing here to pick up.'}]


""" Tests for UseItemAction """


def test_UseItemAction__is_subclass_of_Action():
    use = actions.UseItemAction()
    assert isinstance(use, actions.Action)


def test_UseItemAction__consumes_turn():
    use = actions.UseItemAction()
    assert use.consumes_turn


def test_UseItemAction__results_is_empty():
    use = actions.UseItemAction()
    assert use.results == []


def test_UseItemAction__valid_item(walk_map, hero):
    potion = factory.mk_entity('healing_potion', 1, 0)
    hero.inv.add_item(potion)
    inv_index = 0  # Assume potion is at index 0
    use = actions.UseItemAction()
    use.perform(
        stage=walk_map,
        fov_map=None,
        inv_index=inv_index,
        hero=hero,
        prev_state=None
    )
    assert use.results == [{
        'consumed': False,
        'cancel_inv': True,
        'msg': 'You are already at full health'
    }]


def test_UseItemAction__hero_is_dead(walk_map, hero):
    use = actions.UseItemAction()
    use.perform(
        stage=walk_map,
        fov_map=None,
        inv_index=0,
        hero=hero,
        prev_state=config.States.HERO_DEAD
    )
    assert use.results == []


def test_UseItemAction__inv_index_out_of_bounds(walk_map, hero):
    use = actions.UseItemAction()
    with pytest.raises(IndexError):
        use.perform(
            stage=walk_map,
            fov_map=None,
            inv_index=-1,
            hero=hero,
            prev_state=config.States.HERO_TURN
        )


""" Tests for DropItemAction """


def test_DropItemAction__is_subclass_of_Action():
    drop = actions.DropItemAction()
    assert isinstance(drop, actions.Action)


def test_DropItemAction__consumes_turn():
    drop = actions.DropItemAction()
    assert drop.consumes_turn


def test_DropItemAction__results_is_empty():
    drop = actions.DropItemAction()
    assert drop.results == []


def test_DropItemAction__hero_is_dead(walk_map, hero):
    drop = actions.DropItemAction()
    drop.perform(
        stage=walk_map,
        inv_index=0,
        hero=hero,
        prev_state=config.States.HERO_DEAD
    )
    assert drop.results == []


def test_DropItemAction__valid_item(walk_map, hero):
    potion = factory.mk_entity('healing_potion', 1, 0)
    hero.inv.add_item(potion)
    inv_index = 0  # Assume potion is at index 0

    drop = actions.DropItemAction()
    drop.perform(
        stage=walk_map,
        inv_index=inv_index,
        hero=hero,
        prev_state=None
    )
    assert drop.results == [{
        'item_dropped': potion,
        'msg': 'You dropped the {}.'.format(potion.name)
    }]


def test_DropItemAction__inv_index_out_of_bounds(walk_map, hero):
    drop = actions.DropItemAction()
    with pytest.raises(IndexError):
        drop.perform(
            stage=walk_map,
            inv_index=-1,
            hero=hero,
            prev_state=config.States.HERO_TURN
        )


""" Tests for StairUpAction """


def test_StairUpAction__is_subclass_of_Action():
    stairup = actions.StairUpAction()
    assert isinstance(stairup, actions.Action)


def test_StairUpAction__consumes_turn():
    stairup = actions.StairUpAction()
    assert stairup.consumes_turn


def test_StairUpAction__results_is_empty():
    stairup = actions.StairUpAction()
    assert stairup.results == []

""" Tests for StairDownAction """


def test_StairDownAction__is_subclass_of_Action():
    stairdown = actions.StairDownAction()
    assert isinstance(stairdown, actions.Action)


def test_StairDownAction__consumes_turn():
    stairdown = actions.StairDownAction()
    assert stairdown.consumes_turn


def test_StairDownAction__results_is_empty():
    stairdown = actions.StairDownAction()
    assert stairdown.results == []


""" Tests for LevelUpAction """


def test_LevelUpAction__is_subclass_of_Action():
    levelup = actions.LevelUpAction()
    assert isinstance(levelup, actions.Action)


def test_LevelUpAction__consumes_turn_is_False():
    levelup = actions.LevelUpAction()
    assert levelup.consumes_turn is False


def test_LevelUpAction__results_is_empty():
    levelup = actions.LevelUpAction()
    assert levelup.results == []


""" Tests for ExitAction """


def test_ExitAction__is_subclass_of_Action():
    exit_action = actions.ExitAction()
    assert isinstance(exit_action, actions.Action)


def test_ExitAction__consumes_turn_is_False():
    exit_action = actions.ExitAction()
    assert exit_action.consumes_turn is False


def test_ExitAction__results_is_empty():
    exit_action = actions.ExitAction()
    assert exit_action.results == []


""" Tests for FullScreenAction """


def test_FullScreenAction__is_subclass_of_Action():
    fullscreen = actions.FullScreenAction()
    assert isinstance(fullscreen, actions.Action)


def test_FullScreenAction__consumes_turn_is_False():
    fullscreen = actions.FullScreenAction()
    assert fullscreen.consumes_turn is False


def test_FullScreenAction__results_is_empty():
    fullscreen = actions.FullScreenAction()
    assert fullscreen.results == []


""" Tests for LClickAction """


def test_LClickAction__is_subclass_of_Action():
    lclick = actions.LClickAction()
    assert isinstance(lclick, actions.Action)


def test_LClickAction__consumes_turn_is_False():
    lclick = actions.LClickAction()
    assert lclick.consumes_turn is False


def test_LClickAction__results_is_empty():
    lclick = actions.LClickAction()
    assert lclick.results == []


""" Tests for RClickAction """


def test_RClickAction__is_subclass_of_Action():
    rclick = actions.RClickAction()
    assert isinstance(rclick, actions.Action)


def test_RClickAction__consumes_turn_is_False():
    rclick = actions.RClickAction()
    assert rclick.consumes_turn is False


def test_RClickAction__results_is_empty():
    rclick = actions.RClickAction()
    assert rclick.results == []


""" Tests for ShowInvAction """
def test_ShowInvAction__is_subclass_of_Action():
    show_inv = actions.ShowInvAction()
    assert isinstance(show_inv, actions.Action)


def test_ShowInvAction__consumes_turn_is_False():
    show_inv = actions.ShowInvAction()
    assert show_inv.consumes_turn is False


def test_ShowInvAction__results_is_empty():
    show_inv = actions.ShowInvAction()
    assert show_inv.results == []


""" Tests for DropInvAction """
def test_DropInvAction__is_subclass_of_Action():
    drop_inv = actions.DropInvAction()
    assert isinstance(drop_inv, actions.Action)


def test_DropInvAction__consumes_turn_is_False():
    drop_inv = actions.DropInvAction()
    assert drop_inv.consumes_turn is False


def test_DropInvAction__results_is_empty():
    drop_inv = actions.DropInvAction()
    assert drop_inv.results == []


""" Tests for ShowCharScreenAction """

def test_ShowCharScreenAction__is_subclass_of_Action():
    char_scr = actions.ShowCharScreenAction()
    assert isinstance(char_scr, actions.Action)


def test_ShowCharScreenAction__consumes_turn_is_False():
    char_scr = actions.ShowCharScreenAction()
    assert char_scr.consumes_turn is False


def test_ShowCharScreenAction__results_is_empty():
    char_scr = actions.ShowCharScreenAction()
    assert char_scr.results == []
