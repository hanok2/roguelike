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


""" Tests for ActionResult """


def test_ActionResult__action_succeeded():
    ar = actions.ActionResult(success=True)
    assert ar.success
    assert ar.alternative is None


def test_ActionResult__action_failed():
    ar = actions.ActionResult(success=False)
    assert ar.success is False
    assert ar.alternative is None


def test_ActionResult__action_alternative():
    ar = actions.ActionResult(alternative=actions.WaitAction())
    assert ar.success is False
    assert isinstance(ar.alternative, actions.WaitAction)


def test_ActionResult__success_True_and_alterative_raises_exception():
    with pytest.raises(ValueError):
        actions.ActionResult(success=True, alternative=actions.WaitAction())



""" Tests for WalkAction """


# Don't Need?
# def test_WalkAction__not_heros_turn__returns_False(walk_map):

def test_WalkAction__init():
    walk = actions.WalkAction(dx=1, dy=0)
    assert isinstance(walk, actions.Action)
    assert walk.consumes_turn
    assert walk.results == []


def test_WalkAction__into_monster__returns_AttackAction(walk_map, hero):
    walk_map.entities.append(hero)

    walk = actions.WalkAction(dx=1, dy=0)
    walk.perform(stage=walk_map, entity=hero)
    result = walk.results[0]['alternate']
    assert isinstance(result, actions.AttackAction)
    assert result.dx == walk.dx
    assert result.dy == walk.dy
    assert walk.consumes_turn is False


def test_WalkAction__alt_AttackAction__consumes_turn_is_False(walk_map, hero):
    walk_map.entities.append(hero)

    walk = actions.WalkAction(dx=1, dy=0)
    walk.perform(stage=walk_map, entity=hero)
    assert walk.consumes_turn is False


def test_WalkAction__blocked_by_wall__msg_and_returns_fail(walk_map, hero):
    walk_map.entities.append(hero)

    walk = actions.WalkAction(dx=0, dy=1)
    walk.perform(stage=walk_map, entity=hero)
    assert walk.results == [{ 'msg': 'You cannot walk into the wall...' }]
    assert walk.consumes_turn is False


def test_WalkAction__success__recompute_fov(walk_map, hero):
    walk_map.entities.append(hero)
    walk = actions.WalkAction(dx=-1, dy=-1)
    walk.perform(stage=walk_map, entity=hero)
    assert walk.results == [{'fov_recompute': True}]


@pytest.mark.skip(reason='we do not have an item checking method yet for stages.')
def test_WalkAction__over_item__returns_walkover_msg(walk_map, hero):
    walk_map.entities.append(hero)
    walk = actions.WalkAction(dx=0, dy=-1)
    result = walk.perform(stage=walk_map, entity=hero)
    assert result == 'you see a healing position'


def test_WalkAction__more_than_1_sq_away__raise_exception(walk_map):
    walk_map.entities.append(hero)
    with pytest.raises(ValueError):
        actions.WalkAction(dx=-2, dy=-1)


""" Tests for AttackAction """


def test_AttackAction__init(hero):
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
    attack.perform(stage=walk_map)
    assert attack.results == [{'msg': 'There is nothing to attack at that position.'}]


def test_AttackAction__attacking_wall(hero, walk_map):
    attack = actions.AttackAction(hero, dx=0, dy=1)
    attack.perform(stage=walk_map)
    assert attack.results == [{'msg': 'You cannot attack the wall!'}]


def test_AttackAction__valid_target(hero, walk_map):
    attack = actions.AttackAction(hero, dx=1, dy=0)
    attack.perform(stage=walk_map)
    assert attack.results == [{'msg': 'Player attacks Orc!'}]


""" Tests for WaitAction """


def test_WaitAction__init():
    wait = actions.WaitAction()
    assert isinstance(wait, actions.Action)
    assert wait.consumes_turn
    assert wait.results == []


def test_WaitAction__returns_None():
    wait = actions.WaitAction()
    assert wait.perform() is None


""" Tests for PickupAction """


def test_PickupAction__init():
    pickup = actions.PickupAction()
    assert isinstance(pickup, actions.Action)
    assert pickup.consumes_turn
    assert pickup.results == []


def test_PickupAction__item(walk_map, hero):
    hero.x, hero.y = 1, 0   # Move the player to the same tile as the potion
    walk_map.entities.append(hero)
    pickup = actions.PickupAction()
    pickup.perform(stage=walk_map, entity=hero)

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
    pickup.perform(stage=walk_map, entity=hero)

    # pickup.results[0] = {'item_added': None, 'msg': INV_FULL_MSG}
    assert pickup.results == 'pickup menu'


def test_PickupAction__no_items_at_entity_location(walk_map, hero):
    walk_map.entities.append(hero)
    pickup = actions.PickupAction()
    pickup.perform(stage=walk_map, entity=hero)

    assert pickup.results == [{'msg': 'There is nothing here to pick up.'}]


""" Tests for UseItemAction """


def test_UseItemAction__init():
    use = actions.UseItemAction(0)
    assert isinstance(use, actions.Action)
    assert use.consumes_turn
    assert use.results == []


def test_UseItemAction__inv_index_out_of_bounds(walk_map, hero):
    use = actions.UseItemAction(inv_index=-1)
    with pytest.raises(IndexError):
        use.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=config.States.HERO_TURN)


def test_UseItemAction__equippable__returns_EquipAction(walk_map, hero):
    shield = factory.mk_entity('shield', 1, 0)
    hero.inv.add_item(shield)

    use = actions.UseItemAction(inv_index=0)  # Assume shield is at index 0
    use.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)

    # assert use.results == [{'alternate': actions.EquipAction}]
    result = use.results[0]['alternate']
    assert isinstance(result, actions.EquipAction)


def test_UseItemAction__targets__returns_GetTargetAction(walk_map, hero):
    confusion_scroll = factory.mk_entity('confusion_scroll', 1, 0)
    hero.inv.add_item(confusion_scroll)

    use = actions.UseItemAction(inv_index=0)  # Assume shield is at index 0

    use.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)

    result = use.results[0]['alternate']
    assert isinstance(result, actions.GetTargetAction)


def test_UseItemAction__valid_item(walk_map, hero):
    potion = factory.mk_entity('healing_potion', 1, 0)
    hero.inv.add_item(potion)

    use = actions.UseItemAction(inv_index=0)  # Assume potion is at index 0
    use.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)
    assert use.results == [{
        'consumed': False,
        'msg': 'You are already at full health'
    }]


def test_UseItemAction__invalid_item(walk_map, hero):
    rock = factory.mk_entity('rock', 1, 0)
    hero.inv.add_item(rock)

    use = actions.UseItemAction(inv_index=0)  # Assume rock is at index 0
    use.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)
    assert use.results == [{
        'msg': 'The {} cannot be used.'.format(rock.name),
    }]


# Use the item - was it consumed?


""" Tests for EquipAction """


def test_EquipAction__init(hero):
    use = actions.EquipAction(e=hero, item=None)
    assert isinstance(use, actions.Action)
    assert use.consumes_turn
    assert use.results == []


def test_EquipAction__non_equippable_item(hero):
    potion = factory.mk_entity('healing_potion', 1, 0)
    hero.inv.add_item(potion)

    use = actions.EquipAction(e=hero, item=potion)  # Assume shield is at index 0
    use.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)

    # assert use.results[0]['equipped'] is False
    assert use.results == [{'msg': 'You cannot equip the {}'.format(potion.name)}]


def test_EquipAction__already_equipped__dequips_item(hero):
    shield = factory.mk_entity('shield', 1, 0)
    hero.inv.add_item(shield)
    hero.equipment.toggle_equip(shield)  # Equip the thing

    use = actions.EquipAction(e=hero, item=shield)  # Assume shield is at index 0
    use.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)

    assert use.results == [
        # {'dequipped': shield},
        {'msg': 'You dequipped the {}'.format(shield.name)}
    ]


def test_EquipAction__not_equipped__equips_item(hero):
    shield = factory.mk_entity('shield', 1, 0)
    hero.inv.add_item(shield)

    use = actions.EquipAction(e=hero, item=shield)  # Assume shield is at index 0
    use.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)

    assert use.results == [
        # {'equipped': shield},
        {'msg': 'You equipped the {}'.format(shield.name)}
    ]

""" Tests for class GetTargetAction """



""" Tests for DropItemAction """


def test_DropItemAction__init():
    drop = actions.DropItemAction(inv_index=0)
    assert isinstance(drop, actions.Action)
    assert drop.consumes_turn
    assert drop.results == []


def test_DropItemAction__hero_is_dead(walk_map, hero):
    drop = actions.DropItemAction(inv_index=0)
    drop.perform(
        stage=walk_map,
        entity=hero,
        prev_state=config.States.HERO_DEAD
    )
    assert drop.results == []


def test_DropItemAction__valid_item(walk_map, hero):
    potion = factory.mk_entity('healing_potion', 1, 0)
    hero.inv.add_item(potion)

    drop = actions.DropItemAction(inv_index=0)  # Assume potion is at index 0
    drop.perform(
        stage=walk_map,
        entity=hero,
        prev_state=None
    )
    assert drop.results == [{
        'item_dropped': potion,
        'msg': 'You dropped the {}.'.format(potion.name)
    }]


def test_DropItemAction__inv_index_out_of_bounds(walk_map, hero):
    drop = actions.DropItemAction(inv_index=-1)
    with pytest.raises(IndexError):
        drop.perform(
            stage=walk_map,
            entity=hero,
            prev_state=config.States.HERO_TURN
        )


""" Tests for StairUpAction """


def test_StairUpAction__init():
    stairup = actions.StairUpAction()
    assert isinstance(stairup, actions.Action)
    assert stairup.consumes_turn
    assert stairup.results == []


def test_StairUpAction__not_at_stairs(hero):
    d = dungeon.Dungeon(hero)
    stage = d.get_stage()

    # Remove the stair up for testing
    stage.entities.remove(stage.find_stair('<'))

    stairup = actions.StairUpAction()
    stairup.perform(dungeon=d, entity=hero)
    assert stairup.results == [{
        'msg': 'There are no stairs here.'
    }]


def test_StairUpAction__top_stage__leaves_game(hero):
    d = dungeon.Dungeon(hero)
    stairup = actions.StairUpAction()
    stairup.perform(dungeon=d, entity=hero)
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
    stairup.perform(dungeon=d, entity=hero)

    assert stairup.results == [{
        'msg': 'You ascend the stairs up.',
        'redraw': True,
    }]


""" Tests for StairDownAction """


def test_StairDownAction__init():
    stairdown = actions.StairDownAction()
    assert isinstance(stairdown, actions.Action)
    assert stairdown.consumes_turn
    assert stairdown.results == []


def test_StairDownAction__not_at_stairs(hero):
    d = dungeon.Dungeon(hero)
    stage = d.get_stage()

    # Remove the stair up for testing
    stage.entities.remove(stage.find_stair('>'))

    stairdown = actions.StairDownAction()
    stairdown.perform(dungeon=d, entity=hero)
    assert stairdown.results == [{
        'msg': 'There are no stairs here.'
    }]


def test_StairDownAction__next_stage_DNE(hero):
    d = dungeon.Dungeon(hero)
    prev_stages = len(d.stages)

    s = d.get_stage().find_stair('>')
    d.move_hero(0, s.x, s.y)

    # Find the stairs down and put the hero there for testing
    stairdown = actions.StairDownAction()
    stairdown.perform(dungeon=d, entity=hero)

    assert len(d.stages) == prev_stages + 1


def test_StairDownAction__next_stage_exists(hero):
    d = dungeon.Dungeon(hero)

    s = d.get_stage().find_stair('>')
    d.move_hero(0, s.x, s.y)

    # Create the next stage
    d.mk_next_stage()

    # Find the stairs down and put the hero there for testing
    stairdown = actions.StairDownAction()
    stairdown.perform(dungeon=d, entity=hero)

    assert stairdown.results == [{
        'msg': 'You carefully descend the stairs down.',
        'redraw': True,
    }]


""" Tests for LevelUpAction """


def test_LevelUpAction__init():
    prev_state = config.States.HERO_TURN
    levelup = actions.LevelUpAction('hp')

    assert isinstance(levelup, actions.Action)
    assert levelup.consumes_turn is False
    assert levelup.results == []


def test_LevelUpAction__invalid_stat(hero):
    prev_state = config.States.HERO_TURN
    with pytest.raises(ValueError):
        levelup = actions.LevelUpAction(stat='boogers')


def test_LevelUpAction__boost_hp(hero):
    prev_state = config.States.HERO_TURN
    levelup = actions.LevelUpAction(stat='hp')
    levelup.perform(entity=hero, prev_state=prev_state)

    assert levelup.results == [
        {'msg': 'Boosted max HP!'},
        {'state': prev_state}
    ]


def test_LevelUpAction__boost_strength(hero):
    prev_state = config.States.HERO_TURN
    levelup = actions.LevelUpAction(stat='str')
    levelup.perform(entity=hero, prev_state=prev_state)

    assert levelup.results == [
        {'msg': 'Boosted strength!'},
        {'state': prev_state}
    ]


def test_LevelUpAction__boost_defense(hero):
    prev_state = config.States.HERO_TURN
    levelup = actions.LevelUpAction(stat='def')
    levelup.perform(entity=hero, prev_state=prev_state)

    assert levelup.results == [
        {'msg': 'Boosted defense!'},
        {'state': prev_state}
    ]


""" Tests for ExitAction """


def test_ExitAction__init():
    state = config.States.SHOW_INV
    exit_action = actions.ExitAction(state)

    assert isinstance(exit_action, actions.Action)
    assert exit_action.consumes_turn is False
    assert exit_action.results == []


def test_ExitAction__SHOW_INV_returns_to_HERO_TURN():
    state = config.States.SHOW_INV
    exit_action = actions.ExitAction(state)

    prev_state = config.States.HERO_TURN
    exit_action.perform(prev_state=prev_state)
    assert exit_action.results == [{'state': prev_state}]


def test_ExitAction__DROP_INV_returns_to_HERO_TURN():
    state = config.States.DROP_INV
    exit_action = actions.ExitAction(state)

    prev_state = config.States.HERO_TURN
    exit_action.perform(prev_state=prev_state)
    assert exit_action.results == [{'state': prev_state}]


def test_ExitAction__SHOW_STATS_returns_to_HERO_TURN():
    state = config.States.SHOW_STATS
    exit_action = actions.ExitAction(state)

    prev_state = config.States.HERO_TURN
    exit_action.perform(prev_state=prev_state)
    assert exit_action.results == [{'state': prev_state}]


def test_ExitAction__TARGETING_returns_to_HERO_TURN():
    state = config.States.TARGETING
    exit_action = actions.ExitAction(state)

    prev_state = config.States.HERO_TURN
    exit_action.perform(prev_state=prev_state)

    assert exit_action.results == [{
        'state': prev_state,
        'cancel_target': True,
        'msg': 'Targeting cancelled.',
    }]


def test_ExitAction__HERO_TURN_returns_to_MAIN_MENU():
    state = config.States.HERO_TURN
    exit_action = actions.ExitAction(state)

    prev_state = config.States.MAIN_MENU
    exit_action.perform(prev_state=prev_state)
    assert exit_action.results == [{'state': prev_state}]


""" Tests for FullScreenAction """


def test_FullScreenAction__init():
    fullscreen = actions.FullScreenAction()
    assert isinstance(fullscreen, actions.Action)
    assert fullscreen.consumes_turn is False
    assert fullscreen.results == []


def test_FullScreenAction__calls_tcod_console_set_fullscreen(mocker):
    mocker.patch('tcod.console_set_fullscreen')

    fullscreen = actions.FullScreenAction()
    fullscreen.perform()
    tcod.console_set_fullscreen.assert_called_with(fullscreen=not tcod.console_is_fullscreen())



""" Tests for GetTargetAction """


def test_GetTargetAction_init():
    target = actions.GetTargetAction(item=None)
    assert isinstance(target, actions.Action)
    assert target.consumes_turn is False
    assert target.results == []


@pytest.mark.skip(reason='mental block')
def test_GetTargetAction__state_TARGETING():
    target = actions.GetTargetAction(item='plumbus')


@pytest.mark.skip(reason='mental block')
def test_GetTargetAction__targeting_item_is_set():
    target = actions.GetTargetAction(item='plumbus')


@pytest.mark.skip(reason='mental block')
def test_GetTargetAction__targeting_msg():
    target = actions.GetTargetAction(item='plumbus')


""" Tests for TargetAction """


def test_TargetAction__init():
    target = actions.TargetAction(x=0, y=0, lclick=True)
    assert isinstance(target, actions.Action)
    assert target.consumes_turn is False
    assert target.results == []


def test_TargetAction__no_click_raises_exception():
    with pytest.raises(ValueError):
        actions.TargetAction(x=0, y=0)


def test_TargetAction__both_clicks_raises_exception():
    with pytest.raises(ValueError):
        actions.TargetAction(x=0, y=0, lclick=True, rclick=True)


""" Tests for ShowInvAction """


def test_ShowInvAction__init():
    prev_state = config.States.HERO_TURN
    show_inv = actions.ShowInvAction(prev_state)
    assert isinstance(show_inv, actions.Action)
    assert show_inv.consumes_turn is False
    assert show_inv.results == []


def test_ShowInvAction():
    prev_state = config.States.HERO_TURN
    show_inv = actions.ShowInvAction(prev_state)
    show_inv.perform()
    assert show_inv.results == [{'state': config.States.SHOW_INV}]


""" Tests for DropInvAction """


def test_DropInvAction__init():
    prev_state = config.States.HERO_TURN
    drop_inv = actions.DropInvAction(prev_state)

    assert isinstance(drop_inv, actions.Action)
    assert drop_inv.consumes_turn is False
    assert drop_inv.results == []


def test_DropInvAction():
    prev_state = config.States.HERO_TURN
    show_inv = actions.DropInvAction(prev_state)
    show_inv.perform()
    assert show_inv.results == [{'state': config.States.DROP_INV}]


""" Tests for CharScreenAction """


def test_CharScreenAction__init():
    prev_state = config.States.HERO_TURN
    char_scr = actions.CharScreenAction(prev_state)
    assert isinstance(char_scr, actions.Action)
    assert char_scr.consumes_turn is False
    assert char_scr.results == []


def test_CharScreenAction():
    prev_state = config.States.HERO_TURN
    show_inv = actions.CharScreenAction(prev_state)
    show_inv.perform()
    assert show_inv.results == [{'state': config.States.SHOW_STATS}]


def test_KillMonsterAction_init():
    action = actions.KillMonsterAction()
    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False
    assert action.results == []


def test_KillPlayerAction_init():
    action = actions.KillPlayerAction()
    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False
    assert action.results == []


def test_AddXPAction_init():
    action = actions.AddXPAction()
    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False
    assert action.results == []
