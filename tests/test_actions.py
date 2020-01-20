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
def orc():
    return factory.mk_entity('orc', 0, 0)


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
    action = actions.ActionResult(success=True)
    assert action.success
    assert action.alternative is None


def test_ActionResult__action_failed():
    action = actions.ActionResult(success=False)
    assert action.success is False
    assert action.alternative is None


def test_ActionResult__action_alternative():
    action = actions.ActionResult(alternative=actions.WaitAction())
    assert action.success is False
    assert isinstance(action.alternative, actions.WaitAction)


def test_ActionResult__success_True_and_alterative_raises_exception():
    with pytest.raises(ValueError):
        actions.ActionResult(success=True, alternative=actions.WaitAction())


def test_ActionResult__new_state__success_defaults_None():
    action = actions.ActionResult(success=True)
    assert action.new_state is None


def test_ActionResult__new_state__fail_defaults_None():
    action = actions.ActionResult(success=False)
    assert action.new_state is None


def test_ActionResult__new_state__alt_defaults_None():
    action = actions.ActionResult(alternative=actions.WaitAction())
    assert action.new_state is None



""" Tests for WalkAction """


# Don't Need?
# def test_WalkAction__not_heros_turn__returns_False(walk_map):

def test_WalkAction__init():
    action = actions.WalkAction(dx=1, dy=0)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn
    assert action.results == []


def test_WalkAction__into_monster__returns_AttackAction(walk_map, hero):
    walk_map.entities.append(hero)

    action = actions.WalkAction(dx=1, dy=0)
    action.perform(stage=walk_map, entity=hero)
    result = action.results[0]['alternate']
    assert isinstance(result, actions.AttackAction)
    assert result.dx == action.dx
    assert result.dy == action.dy
    assert action.consumes_turn is False


def test_WalkAction__alt_AttackAction__consumes_turn_is_False(walk_map, hero):
    walk_map.entities.append(hero)

    action = actions.WalkAction(dx=1, dy=0)
    action.perform(stage=walk_map, entity=hero)
    assert action.consumes_turn is False


def test_WalkAction__blocked_by_wall__msg_and_returns_fail(walk_map, hero):
    walk_map.entities.append(hero)

    action = actions.WalkAction(dx=0, dy=1)
    action.perform(stage=walk_map, entity=hero)
    assert action.results == [{ 'msg': 'You cannot walk into the wall...' }]
    assert action.consumes_turn is False


def test_WalkAction__success__recompute_fov(walk_map, hero):
    walk_map.entities.append(hero)
    action = actions.WalkAction(dx=-1, dy=-1)
    action.perform(stage=walk_map, entity=hero)
    assert action.results == [{'fov_recompute': True}]


@pytest.mark.skip(reason='we do not have an item checking method yet for stages.')
def test_WalkAction__over_item__returns_walkover_msg(walk_map, hero):
    walk_map.entities.append(hero)
    action = actions.WalkAction(dx=0, dy=-1)
    result = action.perform(stage=walk_map, entity=hero)
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
    action = actions.WaitAction()
    assert isinstance(action, actions.Action)
    assert action.consumes_turn
    assert action.results == []


def test_WaitAction__returns_None():
    action = actions.WaitAction()
    assert action.perform() is None


""" Tests for PickupAction """


def test_PickupAction__init():
    action = actions.PickupAction()
    assert isinstance(action, actions.Action)
    assert action.consumes_turn
    assert action.results == []


def test_PickupAction__item(walk_map, hero):
    hero.x, hero.y = 1, 0   # Move the player to the same tile as the potion
    walk_map.entities.append(hero)
    action = actions.PickupAction()
    action.perform(stage=walk_map, entity=hero)

    # todo: Fix this later - use a Stage.get_entities function instead
    potion = walk_map.entities[0]
    assert potion.name == 'Healing potion'

    assert action.results == [{'item_added': potion, 'msg': 'You pick up the Healing potion.'}]


@pytest.mark.skip(reason='we dont have a Multiple Pickup Menu yet.')
def test_PickupAction__multiple_items(walk_map, hero):
    walk_map.entities.append(hero)
    # Add another potion to the same tile
    walk_map.entities.append(factory.mk_entity('healing_potion', 1, 0))
    action = actions.PickupAction()
    action.perform(stage=walk_map, entity=hero)

    # action.results[0] = {'item_added': None, 'msg': INV_FULL_MSG}
    assert action.results == 'pickup menu'


def test_PickupAction__no_items_at_entity_location(walk_map, hero):
    walk_map.entities.append(hero)
    action = actions.PickupAction()
    action.perform(stage=walk_map, entity=hero)

    assert action.results == [{'msg': 'There is nothing here to pick up.'}]


""" Tests for UseItemAction """


def test_UseItemAction__init():
    action = actions.UseItemAction(0)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn
    assert action.results == []


def test_UseItemAction__inv_index_out_of_bounds(walk_map, hero):
    action = actions.UseItemAction(inv_index=-1)
    with pytest.raises(IndexError):
        action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=config.States.HERO_TURN)


def test_UseItemAction__equippable__returns_EquipAction(walk_map, hero):
    shield = factory.mk_entity('shield', 1, 0)
    hero.inv.add_item(shield)

    action = actions.UseItemAction(inv_index=0)  # Assume shield is at index 0
    action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)

    # assert action.results == [{'alternate': actions.EquipAction}]
    result = action.results[0]['alternate']
    assert isinstance(result, actions.EquipAction)


def test_UseItemAction__targets__returns_GetTargetAction(walk_map, hero):
    confusion_scroll = factory.mk_entity('confusion_scroll', 1, 0)
    hero.inv.add_item(confusion_scroll)

    action = actions.UseItemAction(inv_index=0)  # Assume shield is at index 0

    action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)

    result = action.results[0]['alternate']
    assert isinstance(result, actions.GetTargetAction)


def test_UseItemAction__valid_item(walk_map, hero):
    potion = factory.mk_entity('healing_potion', 1, 0)
    hero.inv.add_item(potion)

    action = actions.UseItemAction(inv_index=0)  # Assume potion is at index 0
    action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)
    assert action.results == [{
        'consumed': False,
        'msg': 'You are already at full health'
    }]


def test_UseItemAction__invalid_item(walk_map, hero):
    rock = factory.mk_entity('rock', 1, 0)
    hero.inv.add_item(rock)

    action = actions.UseItemAction(inv_index=0)  # Assume rock is at index 0
    action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)
    assert action.results == [{
        'msg': 'The {} cannot be used.'.format(rock.name),
    }]


# Use the item - was it consumed?


""" Tests for EquipAction """


def test_EquipAction__init(hero):
    action = actions.EquipAction(e=hero, item=None)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn
    assert action.results == []


def test_EquipAction__non_equippable_item(hero):
    potion = factory.mk_entity('healing_potion', 1, 0)
    hero.inv.add_item(potion)

    action = actions.EquipAction(e=hero, item=potion)  # Assume shield is at index 0
    action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)

    # assert action.results[0]['equipped'] is False
    assert action.results == [{'msg': 'You cannot equip the {}'.format(potion.name)}]


def test_EquipAction__already_equipped__dequips_item(hero):
    shield = factory.mk_entity('shield', 1, 0)
    hero.inv.add_item(shield)
    hero.equipment.toggle_equip(shield)  # Equip the thing

    action = actions.EquipAction(e=hero, item=shield)  # Assume shield is at index 0
    action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)

    assert action.results == [
        # {'dequipped': shield},
        {'msg': 'You dequipped the {}'.format(shield.name)}
    ]


def test_EquipAction__not_equipped__equips_item(hero):
    shield = factory.mk_entity('shield', 1, 0)
    hero.inv.add_item(shield)

    action = actions.EquipAction(e=hero, item=shield)  # Assume shield is at index 0
    action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)

    assert action.results == [
        # {'equipped': shield},
        {'msg': 'You equipped the {}'.format(shield.name)}
    ]

""" Tests for class GetTargetAction """



""" Tests for DropItemAction """


def test_DropItemAction__init():
    action = actions.DropItemAction(inv_index=0)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn
    assert action.results == []


def test_DropItemAction__hero_is_dead(walk_map, hero):
    action = actions.DropItemAction(inv_index=0)
    action.perform(
        stage=walk_map,
        entity=hero,
        prev_state=config.States.HERO_DEAD
    )
    assert action.results == []


def test_DropItemAction__valid_item(walk_map, hero):
    potion = factory.mk_entity('healing_potion', 1, 0)
    hero.inv.add_item(potion)

    action = actions.DropItemAction(inv_index=0)  # Assume potion is at index 0
    action.perform(
        stage=walk_map,
        entity=hero,
        prev_state=None
    )
    assert action.results == [{
        'item_dropped': potion,
        'msg': 'You dropped the {}.'.format(potion.name)
    }]


def test_DropItemAction__inv_index_out_of_bounds(walk_map, hero):
    action = actions.DropItemAction(inv_index=-1)
    with pytest.raises(IndexError):
        action.perform(
            stage=walk_map,
            entity=hero,
            prev_state=config.States.HERO_TURN
        )


""" Tests for StairUpAction """


def test_StairUpAction__init():
    action = actions.StairUpAction()
    assert isinstance(action, actions.Action)
    assert action.consumes_turn
    assert action.results == []


def test_StairUpAction__not_at_stairs(hero):
    d = dungeon.Dungeon(hero)
    stage = d.get_stage()

    # Remove the stair up for testing
    stage.entities.remove(stage.find_stair('<'))

    action = actions.StairUpAction()
    action.perform(dungeon=d, entity=hero)
    assert action.results == [{
        'msg': 'There are no stairs here.'
    }]


def test_StairUpAction__top_stage__leaves_game(hero):
    d = dungeon.Dungeon(hero)
    action = actions.StairUpAction()
    action.perform(dungeon=d, entity=hero)
    assert action.results == [{
        'msg': 'You go up the stairs and leave the dungeon forever...',
        'state': config.States.HERO_DEAD
    }]


def test_StairUpAction__success_on_lower_level(hero):
    d = dungeon.Dungeon(hero)

    # Create another stage, then move the hero to that stage's upstair
    d.mk_next_stage()
    s = d.stages[1].find_stair('<')
    d.move_hero(1, s.x, s.y)

    action = actions.StairUpAction()
    action.perform(dungeon=d, entity=hero)

    assert action.results == [{
        'msg': 'You ascend the stairs up.',
        'redraw': True,
    }]


""" Tests for StairDownAction """


def test_StairDownAction__init():
    action = actions.StairDownAction()
    assert isinstance(action, actions.Action)
    assert action.consumes_turn
    assert action.results == []


def test_StairDownAction__not_at_stairs(hero):
    d = dungeon.Dungeon(hero)
    stage = d.get_stage()

    # Remove the stair up for testing
    stage.entities.remove(stage.find_stair('>'))

    action = actions.StairDownAction()
    action.perform(dungeon=d, entity=hero)
    assert action.results == [{
        'msg': 'There are no stairs here.'
    }]


def test_StairDownAction__next_stage_DNE(hero):
    d = dungeon.Dungeon(hero)
    prev_stages = len(d.stages)

    s = d.get_stage().find_stair('>')
    d.move_hero(0, s.x, s.y)

    # Find the stairs down and put the hero there for testing
    action = actions.StairDownAction()
    action.perform(dungeon=d, entity=hero)

    assert len(d.stages) == prev_stages + 1


def test_StairDownAction__next_stage_exists(hero):
    d = dungeon.Dungeon(hero)

    s = d.get_stage().find_stair('>')
    d.move_hero(0, s.x, s.y)

    # Create the next stage
    d.mk_next_stage()

    # Find the stairs down and put the hero there for testing
    action = actions.StairDownAction()
    action.perform(dungeon=d, entity=hero)

    assert action.results == [{
        'msg': 'You carefully descend the stairs down.',
        'redraw': True,
    }]


""" Tests for LevelUpAction """


def test_LevelUpAction__init():
    prev_state = config.States.HERO_TURN
    action = actions.LevelUpAction('hp')

    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False
    assert action.results == []


def test_LevelUpAction__invalid_stat(hero):
    prev_state = config.States.HERO_TURN
    with pytest.raises(ValueError):
        action = actions.LevelUpAction(stat='boogers')


def test_LevelUpAction__boost_hp(hero):
    prev_state = config.States.HERO_TURN
    action = actions.LevelUpAction(stat='hp')
    action.perform(entity=hero, prev_state=prev_state)

    assert action.results == [
        {'msg': 'Boosted max HP!'},
        {'state': prev_state}
    ]


def test_LevelUpAction__boost_strength(hero):
    prev_state = config.States.HERO_TURN
    action = actions.LevelUpAction(stat='str')
    action.perform(entity=hero, prev_state=prev_state)

    assert action.results == [
        {'msg': 'Boosted strength!'},
        {'state': prev_state}
    ]


def test_LevelUpAction__boost_defense(hero):
    prev_state = config.States.HERO_TURN
    action = actions.LevelUpAction(stat='def')
    action.perform(entity=hero, prev_state=prev_state)

    assert action.results == [
        {'msg': 'Boosted defense!'},
        {'state': prev_state}
    ]


""" Tests for ExitAction """


def test_ExitAction__init():
    state = config.States.SHOW_INV
    action = actions.ExitAction(state)

    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False
    assert action.results == []


def test_ExitAction__SHOW_INV_returns_to_HERO_TURN():
    state = config.States.SHOW_INV
    action = actions.ExitAction(state)

    prev_state = config.States.HERO_TURN
    action.perform(prev_state=prev_state)
    assert action.results == [{'state': prev_state}]


def test_ExitAction__DROP_INV_returns_to_HERO_TURN():
    state = config.States.DROP_INV
    action = actions.ExitAction(state)

    prev_state = config.States.HERO_TURN
    action.perform(prev_state=prev_state)
    assert action.results == [{'state': prev_state}]


def test_ExitAction__SHOW_STATS_returns_to_HERO_TURN():
    state = config.States.SHOW_STATS
    action = actions.ExitAction(state)

    prev_state = config.States.HERO_TURN
    action.perform(prev_state=prev_state)
    assert action.results == [{'state': prev_state}]


def test_ExitAction__TARGETING_returns_to_HERO_TURN():
    state = config.States.TARGETING
    action = actions.ExitAction(state)

    prev_state = config.States.HERO_TURN
    action.perform(prev_state=prev_state)

    assert action.results == [{
        'state': prev_state,
        'cancel_target': True,
        'msg': 'Targeting cancelled.',
    }]


def test_ExitAction__HERO_TURN_returns_to_MAIN_MENU():
    state = config.States.HERO_TURN
    action = actions.ExitAction(state)

    prev_state = config.States.MAIN_MENU
    action.perform(prev_state=prev_state)
    assert action.results == [{'state': prev_state}]


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
    action = actions.ShowInvAction(prev_state)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False
    assert action.results == []


def test_ShowInvAction():
    prev_state = config.States.HERO_TURN
    action = actions.ShowInvAction(prev_state)
    action.perform()
    assert action.results == [{'state': config.States.SHOW_INV}]


""" Tests for DropInvAction """


def test_DropInvAction__init():
    prev_state = config.States.HERO_TURN
    action = actions.DropInvAction(prev_state)

    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False
    assert action.results == []


def test_DropInvAction():
    prev_state = config.States.HERO_TURN
    action = actions.DropInvAction(prev_state)
    action.perform()
    assert action.results == [{'state': config.States.DROP_INV}]


""" Tests for CharScreenAction """


def test_CharScreenAction__init():
    prev_state = config.States.HERO_TURN
    char_scr = actions.CharScreenAction(prev_state)
    assert isinstance(char_scr, actions.Action)
    assert char_scr.consumes_turn is False
    assert char_scr.results == []


def test_CharScreenAction():
    prev_state = config.States.HERO_TURN
    action = actions.CharScreenAction(prev_state)
    action.perform()
    assert action.results == [{'state': config.States.SHOW_STATS}]


""" Tests for KillMonsterAction """


def test_KillMonsterAction_init(orc):
    action = actions.KillMonsterAction(entity=orc)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False
    assert action.results == []


def test_KillMonsterAction_hero_raises_exception(hero):
    with pytest.raises(ValueError):
        actions.KillMonsterAction(hero)


def test_KillMonsterAction__char_is_corpse(orc):
    action = actions.KillMonsterAction(orc)
    action.perform()
    assert orc.char == '%'


def test_KillMonsterAction__name_changed_to_remains(orc):
    action = actions.KillMonsterAction(orc)
    action.perform()
    assert orc.name == 'remains of Orc'


def test_KillMonsterAction__color_is_darkred(orc):
    action = actions.KillMonsterAction(orc)
    action.perform()
    assert orc.color == tcod.dark_red


def test_KillMonsterAction__blocks_is_False(orc):
    action = actions.KillMonsterAction(orc)
    action.perform()
    assert orc.blocks is False


def test_KillMonsterAction__renderorder_is_CORPSE(orc):
    action = actions.KillMonsterAction(orc)
    action.perform()
    assert orc.render_order == config.RenderOrder.CORPSE


def test_KillMonsterAction__fighter_comp_removed(orc):
    action = actions.KillMonsterAction(orc)
    action.perform()
    assert orc.has_comp('fighter') is False


def test_KillMonsterAction__ai_comp_removed(orc):
    action = actions.KillMonsterAction(orc)
    action.perform()
    assert orc.has_comp('ai') is False


def test_KillMonsterAction__item_comp_added(orc):
    action = actions.KillMonsterAction(orc)
    action.perform()
    assert orc.has_comp('item')


def test_KillMonsterAction__returns_death_msg(orc):
    action = actions.KillMonsterAction(orc)
    action.perform()
    assert action.results == [{'msg': 'The Orc dies!'}]


""" Tests for KillPlayerAction """


def test_KillPlayerAction_init(hero):
    action = actions.KillPlayerAction(hero)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False
    assert action.results == []


def test_KillPlayerAction__not_hero_raises_exception():
    orc = factory.mk_entity('orc', 2, 1)

    with pytest.raises(ValueError):
        actions.KillPlayerAction(orc)


def test_KillPlayerAction_char_is_corpse(hero):
    action = actions.KillPlayerAction(hero)
    action.perform()
    assert hero.char == '%'


def test_KillPlayerAction_color_is_darkred(hero):
    action = actions.KillPlayerAction(hero)
    action.perform()
    assert hero.color == tcod.dark_red


def test_KillPlayerAction_returns_death_msg_and_dead_status(hero):
    action = actions.KillPlayerAction(hero)
    action.perform()
    assert action.results == [{'msg':'You died!', 'state': config.States.HERO_DEAD}]


""" Tests for AddXPAction """


def test_AddXPAction_init():
    action = actions.AddXPAction()
    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False
    assert action.results == []
