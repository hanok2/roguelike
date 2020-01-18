import pytest
import tcod
from ..src import actions
from ..src import config
from ..src import dungeon
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


""" Tests for AttackAction """


def test_AttackAction__super_init(hero):
    attack = actions.AttackAction(hero, dx=1, dy=1)
    assert isinstance(attack, actions.Action)
    assert attack.consumes_turn
    assert attack.results == []


def test_AttackAction__init__instance_variables(hero):
    attack = actions.AttackAction(hero, dx=1, dy=0)
    assert attack.entity == hero
    assert attack.dx == 1
    assert attack.dy == 0


def test_AttackAction__invalid_dx__raises_exception():
    with pytest.raises(ValueError):
        actions.AttackAction(hero, dx=-2, dy=2)


def test_AttackAction__invalid_dy__raises_exception():
    with pytest.raises(ValueError):
        actions.AttackAction(hero, dx=1, dy=-2)


def test_AttackAction__no_target(hero, walk_map):
    attack = actions.AttackAction(hero, dx=-1, dy=0)
    attack.perform(walk_map)
    assert attack.results == [{'msg': 'There is nothing to attack at that position.'}]


def test_AttackAction__attacking_wall(hero, walk_map):
    attack = actions.AttackAction(hero, dx=0, dy=1)
    attack.perform(walk_map)
    assert attack.results == [{'msg': 'You cannot attack the wall!'}]


def test_AttackAction__valid_target(hero, walk_map):
    attack = actions.AttackAction(hero, dx=1, dy=0)
    attack.perform(walk_map)
    assert attack.results == [{'msg': 'Player attacks Orc!'}]


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


def test_StairUpAction__not_at_stairs(hero):
    d = dungeon.Dungeon(hero)
    stage = d.get_stage()

    # Remove the stair up for testing
    stage.entities.remove(stage.find_stair('<'))

    stairup = actions.StairUpAction()
    stairup.perform(d, hero)
    assert stairup.results == [{
        'msg': 'There are no stairs here.'
    }]


def test_StairUpAction__top_stage__leaves_game(hero):
    d = dungeon.Dungeon(hero)
    stairup = actions.StairUpAction()
    stairup.perform(d, hero)
    assert stairup.results == [{
        'msg': 'You go up the stairs and leave the dungeon forever...',
        'state': config.States.HERO_DEAD
    }]


def test_StairUpAction__success_on_lower_level(hero):
    d = dungeon.Dungeon(hero)

    # Create another stage, then move the hero to that stage's upstair
    d.mk_next_stage()
    s = d.stages[1].find_stair('<')
    d.move_hero(1, s.x, s.y)

    stairup = actions.StairUpAction()
    stairup.perform(d, hero)

    assert stairup.results == [{
        'msg': 'You ascend the stairs up.',
        'recompute_fov': True,
        'reset_rendering': True
    }]



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


def test_StairDownAction__not_at_stairs(hero):
    d = dungeon.Dungeon(hero)
    stage = d.get_stage()

    # Remove the stair up for testing
    stage.entities.remove(stage.find_stair('>'))

    stairdown = actions.StairDownAction()
    stairdown.perform(d, hero)
    assert stairdown.results == [{
        'msg': 'There are no stairs here.'
    }]



# Next level DNE: Create level action?  Or use mocking?
def test_StairDownAction__next_stage_DNE(hero):
    d = dungeon.Dungeon(hero)
    prev_stages = len(d.stages)

    s = d.get_stage().find_stair('>')
    d.move_hero(0, s.x, s.y)

    # Find the stairs down and put the hero there for testing
    stairdown = actions.StairDownAction()
    stairdown.perform(d, hero)

    assert len(d.stages) == prev_stages + 1



# Next level exists: Go to next level and place hero at Up stair
def test_StairDownAction__next_stage_exists(hero):
    d = dungeon.Dungeon(hero)

    s = d.get_stage().find_stair('>')
    d.move_hero(0, s.x, s.y)

    # Create the next stage
    d.mk_next_stage()

    # Find the stairs down and put the hero there for testing
    stairdown = actions.StairDownAction()
    stairdown.perform(d, hero)

    assert stairdown.results == [{
        'msg': 'You carefully descend the stairs down.',
        'recompute_fov': True,
        'reset_rendering': True
    }]


""" Tests for LevelUpAction """


def test_LevelUpAction__is_subclass_of_Action():
    levelup = actions.LevelUpAction('hp')
    assert isinstance(levelup, actions.Action)


def test_LevelUpAction__consumes_turn_is_False():
    levelup = actions.LevelUpAction('hp')
    assert levelup.consumes_turn is False


def test_LevelUpAction__results_is_empty():
    levelup = actions.LevelUpAction('hp')
    assert levelup.results == []


def test_LevelUpAction__invalid_stat(hero):
    with pytest.raises(ValueError):
        levelup = actions.LevelUpAction(stat='boogers')


def test_LevelUpAction__boost_hp(hero):
    levelup = actions.LevelUpAction(stat='hp')
    levelup.perform(hero)
    assert levelup.results == [
        {'msg': 'Boosted max HP!'},
        {'state': 'previous state'}
    ]


def test_LevelUpAction__boost_strength(hero):
    levelup = actions.LevelUpAction(stat='str')
    levelup.perform(hero)
    assert levelup.results == [
        {'msg': 'Boosted strength!'},
        {'state': 'previous state'}
    ]


def test_LevelUpAction__boost_defense(hero):
    levelup = actions.LevelUpAction(stat='def')
    levelup.perform(hero)
    assert levelup.results == [
        {'msg': 'Boosted defense!'},
        {'state': 'previous state'}
    ]


""" Tests for ExitAction """


def test_ExitAction__is_subclass_of_Action():
    state = config.States.HERO_TURN
    exit_action = actions.ExitAction(state)
    assert isinstance(exit_action, actions.Action)


def test_ExitAction__consumes_turn_is_False():
    state = config.States.HERO_TURN
    exit_action = actions.ExitAction(state)
    assert exit_action.consumes_turn is False


def test_ExitAction__state_is_SHOW_INV():
    prev_state = config.States.HERO_TURN
    exit_action = actions.ExitAction(prev_state)

    state = config.States.SHOW_INV
    exit_action.perform(state)
    assert exit_action.results == [{'state': prev_state}]


def test_ExitAction__state_is_DROP_INV():
    prev_state = config.States.HERO_TURN
    exit_action = actions.ExitAction(prev_state)

    state = config.States.DROP_INV
    exit_action.perform(state)
    assert exit_action.results == [{'state': prev_state}]


def test_ExitAction__state_is_SHOW_STATS():
    prev_state = config.States.HERO_TURN
    exit_action = actions.ExitAction(prev_state)

    state = config.States.SHOW_STATS
    exit_action.perform(state)
    assert exit_action.results == [{'state': prev_state}]


def test_ExitAction__state_is_TARGETING():
    prev_state = config.States.HERO_TURN
    exit_action = actions.ExitAction(prev_state)

    state = config.States.TARGETING
    exit_action.perform(state)
    assert exit_action.results == [{
        'state': prev_state,
        'cancel_target': True,
        'msg': 'Targeting cancelled.',
    }]


def test_ExitAction__state_is_HERO_TURN():
    prev_state = config.States.HERO_TURN
    exit_action = actions.ExitAction(prev_state)

    state = config.States.MAIN_MENU
    exit_action.perform(state)
    assert exit_action.results == [{'state': state}]


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


def test_FullScreenAction__calls_tcod_console_set_fullscreen(mocker):
    mocker.patch('tcod.console_set_fullscreen')

    fullscreen = actions.FullScreenAction()
    fullscreen.perform()
    tcod.console_set_fullscreen.assert_called_with(fullscreen=not tcod.console_is_fullscreen())


""" Tests for TargetAction """


def test_TargetAction__is_subclass_of_Action():
    target = actions.TargetAction(x=0, y=0, lclick=True)
    assert isinstance(target, actions.Action)


def test_TargetAction__consumes_turn_is_False():
    lclick = actions.TargetAction(x=0, y=0, lclick=True)
    assert lclick.consumes_turn is False


def test_TargetAction__results_is_empty():
    lclick = actions.TargetAction(x=0, y=0, lclick=True)
    assert lclick.results == []


def test_TargetAction__no_click_raises_exception():
    with pytest.raises(ValueError):
        actions.TargetAction(x=0, y=0)


def test_TargetAction__both_clicks_raises_exception():
    with pytest.raises(ValueError):
        actions.TargetAction(x=0, y=0, lclick=True, rclick=True)


""" Tests for ShowInvAction """


def test_ShowInvAction__is_subclass_of_Action():
    prev_state = config.States.HERO_TURN
    show_inv = actions.ShowInvAction(prev_state)
    assert isinstance(show_inv, actions.Action)


def test_ShowInvAction__consumes_turn_is_False():
    prev_state = config.States.HERO_TURN
    show_inv = actions.ShowInvAction(prev_state)
    assert show_inv.consumes_turn is False


def test_ShowInvAction__results_is_empty():
    prev_state = config.States.HERO_TURN
    show_inv = actions.ShowInvAction(prev_state)
    assert show_inv.results == []


def test_ShowInvAction():
    prev_state = config.States.HERO_TURN
    show_inv = actions.ShowInvAction(prev_state)
    show_inv.perform()
    assert show_inv.results == [{'state': config.States.SHOW_INV}]



""" Tests for DropInvAction """
def test_DropInvAction__is_subclass_of_Action():
    prev_state = config.States.HERO_TURN
    drop_inv = actions.DropInvAction(prev_state)

    assert isinstance(drop_inv, actions.Action)


def test_DropInvAction__consumes_turn_is_False():
    prev_state = config.States.HERO_TURN
    drop_inv = actions.DropInvAction(prev_state)
    assert drop_inv.consumes_turn is False


def test_DropInvAction__results_is_empty():
    prev_state = config.States.HERO_TURN
    drop_inv = actions.DropInvAction(prev_state)
    assert drop_inv.results == []


def test_DropInvAction():
    prev_state = config.States.HERO_TURN
    show_inv = actions.DropInvAction(prev_state)
    show_inv.perform()
    assert show_inv.results == [{'state': config.States.DROP_INV}]


""" Tests for CharScreenAction """


def test_CharScreenAction__is_subclass_of_Action():
    prev_state = config.States.HERO_TURN
    char_scr = actions.CharScreenAction(prev_state)
    assert isinstance(char_scr, actions.Action)


def test_CharScreenAction__consumes_turn_is_False():
    prev_state = config.States.HERO_TURN
    char_scr = actions.CharScreenAction(prev_state)
    assert char_scr.consumes_turn is False


def test_CharScreenAction__results_is_empty():
    prev_state = config.States.HERO_TURN
    char_scr = actions.CharScreenAction(prev_state)
    assert char_scr.results == []


def test_CharScreenAction():
    prev_state = config.States.HERO_TURN
    show_inv = actions.CharScreenAction(prev_state)
    show_inv.perform()
    assert show_inv.results == [{'state': config.States.SHOW_STATS}]


