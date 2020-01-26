import pytest
import tcod
from ..src import actions
from ..src import config
from ..src import dungeon
from ..src import factory
from ..src import game
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
def test_game():
    return game.Game()


@pytest.fixture
def potion():
    return factory.mk_entity('healing_potion', 0, 0)


@pytest.fixture
def sword():
    return factory.mk_entity('sword', 0, 0)


@pytest.fixture
def walk_map():
    m = stages.Stage(3, 3)
    # Set all tiles to non-blocking
    m.tiles = [[tile.Tile(False) for y in range(10)] for x in range(10)]
    m.tiles[1][2].blocks = True  # Add a wall

    orc = factory.mk_entity('orc', 2, 1)
    potion = factory.mk_entity('healing_potion', 1, 0)
    m.entities.extend([potion, orc])
    m.potion_ref = potion  # Easy ref for testing

    return m

@pytest.fixture
def fov_stage():
    # todo: When we revamp map - revise this fixture!!!!!!!!!!!!!!!!!!!!!!!!
    m = stages.Stage(10, 10)
    # All open
    m.tiles = [[tile.Tile(False) for y in range(10)] for x in range(10)]
    wall_coordinates = [
        (1, 1), (2, 1), (3, 1), (4, 1),
        (1, 2),
        (1, 3),
    ]
    # Set up some wall for testing
    for x, y in wall_coordinates:
        m.tiles[x][y].blocks = True

    hero = player.Player(x=0, y=0)
    orc = factory.mk_entity('orc', 1, 0)

    m.entities.append(orc)
    m.entities.append(hero)

    m.orc_ref = orc
    m.hero_ref = hero

    return m


@pytest.fixture
def open_map():
    # todo: When we revamp map - remove this fixture!!!!!!!!!!!!!!!!!!!!!!!!
    m = stages.Stage(10, 10)
    m.tiles = [[tile.Tile(False) for y in range(10)] for x in range(10)]
    return m


""" Tests for ActionResult """


def test_ActionResult__action_succeeded():
    result = actions.ActionResult(success=True)
    assert result.success
    assert result.alt is None


def test_ActionResult__action_failed():
    result = actions.ActionResult(success=False)
    assert result.success is False
    assert result.alt is None


def test_ActionResult__contains_alt_using_class():
    result = actions.ActionResult(alt=actions.WaitAction())
    assert result.success is False
    assert actions.WaitAction in result


def test_ActionResult__contains_alt_using_str():
    result = actions.ActionResult(alt=actions.WaitAction())
    assert result.success is False
    assert 'WaitAction' in result


def test_ActionResult__new_state__success_defaults_None():
    result = actions.ActionResult(success=True)
    assert result.new_state is None


def test_ActionResult__new_state__fail_defaults_None():
    result = actions.ActionResult(success=False)
    assert result.new_state is None


def test_ActionResult__new_state__alt_defaults_None():
    result = actions.ActionResult(alt=actions.WaitAction())
    assert result.new_state is None



""" Tests for NullAction """


def test_NullAction__init():
    action = actions.NullAction()
    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False


def test_NullAction__results():
    action = actions.NullAction()
    result = action.perform()
    assert result.success is False
    assert result.msg is None
    assert result.alt is None
    assert result.new_state is None



""" Tests for WalkAction """


def test_WalkAction__init():
    action = actions.WalkAction(dx=1, dy=0)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn
    assert str(action) == 'WalkAction'


def test_WalkAction__into_monster__returns_AttackAction(test_game, walk_map, hero):
    walk_map.entities.append(hero)

    action = actions.WalkAction(dx=1, dy=0)
    result = action.perform(stage=walk_map, entity=hero, game=test_game)

    assert actions.AttackAction in result
    assert result.success is False

    # alt action doesn't change consumes_turn
    assert action.consumes_turn


def test_WalkAction__blocked_by_wall__fails(test_game, walk_map, hero):
    walk_map.entities.append(hero)
    action = actions.WalkAction(dx=0, dy=1)
    result = action.perform(stage=walk_map, entity=hero, game=test_game)

    assert result.success is False
    assert result.msg == 'You cannot walk into the wall...'


def test_WalkAction__success(test_game, walk_map, hero):
    walk_map.entities.append(hero)
    action = actions.WalkAction(dx=-1, dy=-1)

    result = action.perform(stage=walk_map, entity=hero, game=test_game)
    assert result.success


def test_WalkAction__success__recomputes_fov(test_game, walk_map, hero):
    walk_map.entities.append(hero)
    action = actions.WalkAction(dx=-1, dy=-1)

    action.perform(stage=walk_map, entity=hero, game=test_game)
    assert test_game.fov_recompute


@pytest.mark.skip(reason='we do not have an item checking method yet for stages.')
def test_WalkAction__over_item__returns_walkover_msg(test_game, walk_map, hero):
    walk_map.entities.append(hero)
    action = actions.WalkAction(dx=0, dy=-1)
    result = action.perform(stage=walk_map, entity=hero, game=test_game)
    assert result == 'you see a healing position'


def test_WalkAction__more_than_1_sq_away__raise_exception(walk_map):
    walk_map.entities.append(hero)
    with pytest.raises(ValueError):
        actions.WalkAction(dx=-2, dy=-1)


""" Tests for AttackAction """


def test_AttackAction__init(hero, orc):
    attack = actions.AttackAction(attacker=hero, defender=orc)
    assert isinstance(attack, actions.Action)
    assert attack.consumes_turn


def test_AttackAction__init__instance_variables(hero, orc):
    attack = actions.AttackAction(attacker=hero, defender=orc)
    assert attack.attacker == hero
    assert attack.defender == orc


def test_AttackAction__invalid_attacker__raises_exception(orc, potion):
    # Entities must have Fighter component
    with pytest.raises(ValueError):
        actions.AttackAction(attacker=potion, defender=orc)


def test_AttackAction__invalid_defender__raises_exception(hero, potion):
    # Entities must have Fighter component
    with pytest.raises(ValueError):
        actions.AttackAction(attacker=hero, defender=potion)


def test_AttackAction__dmg_returns_TakeDmgAction(hero, orc):
    attack = actions.AttackAction(attacker=hero, defender=orc)
    result = attack.perform()

    assert result.success
    assert result.msg == 'Player attacks Orc!'
    assert actions.TakeDmgAction in result


def test_AttackAction__no_dmg(hero, orc):
    attack = actions.AttackAction(attacker=hero, defender=orc)
    hero.fighter.base_power = 1
    dmg = hero.fighter.power - orc.fighter.defense

    assert dmg == 0
    expected_hp = orc.fighter.hp
    result = attack.perform(stage=walk_map)

    assert result.msg == 'Player attacks Orc... But does no damage.'
    assert result.success
    assert orc.fighter.hp == expected_hp



""" Tests for WaitAction """


def test_WaitAction__init():
    action = actions.WaitAction()
    assert isinstance(action, actions.Action)
    assert action.consumes_turn


def test_WaitAction__returns_None():
    action = actions.WaitAction()
    result = action.perform()
    assert result.success


""" Tests for PickupAction """


def test_PickupAction__init():
    action = actions.PickupAction()
    assert isinstance(action, actions.Action)
    assert action.consumes_turn


def test_PickupAction__item(walk_map, hero):
    hero.x, hero.y = 1, 0   # Move the player to the same tile as the potion
    walk_map.entities.append(hero)
    action = actions.PickupAction()
    result = action.perform(stage=walk_map, entity=hero)

    # todo: Fix this later - use a Stage.get_entities function instead
    potion = walk_map.potion_ref
    assert potion.name == 'Healing potion'

    assert result.success
    assert result.msg == 'You pick up the Healing potion.'
    assert potion not in walk_map.entities
    # [{'item_added': potion,


@pytest.mark.skip(reason='we dont have a Multiple Pickup Menu yet.')
def test_PickupAction__multiple_items(walk_map, hero):
    walk_map.entities.append(hero)
    # Add another potion to the same tile
    walk_map.entities.append(factory.mk_entity('healing_potion', 1, 0))
    action = actions.PickupAction()
    result = action.perform(stage=walk_map, entity=hero)

    # action.results[0] = {'item_added': None, 'msg': INV_FULL_MSG}
    assert result.alt == 'pickup menu'


def test_PickupAction__no_items_at_entity_location(walk_map, hero):
    walk_map.entities.append(hero)
    action = actions.PickupAction()
    result = action.perform(stage=walk_map, entity=hero)

    assert result.msg == 'There is nothing here to pick up.'
    assert result.success is False


""" Tests for UseItemAction """


def test_UseItemAction__init():
    action = actions.UseItemAction(0)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn


def test_UseItemAction__negative_inv_index(walk_map, hero):
    action = actions.UseItemAction(inv_index=-1)
    with pytest.raises(IndexError):
        action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=config.States.ACTOR_TURN)


def test_UseItemAction__inv_index_out_of_bounds__fails(walk_map, hero):
    action = actions.UseItemAction(inv_index=100)
    result = action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=config.States.ACTOR_TURN)
    assert result.success is False


def test_UseItemAction__equippable__returns_EquipAction(walk_map, hero):
    shield = factory.mk_entity('shield', 1, 0)
    hero.inv.add_item(shield)

    action = actions.UseItemAction(inv_index=0)  # Assume shield is at index 0
    result = action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)

    # assert result == [{'alternate': actions.EquipAction}]
    # assert isinstance(result.alt, actions.EquipAction)
    assert result.success is False
    assert actions.EquipAction in result


def test_UseItemAction__targets__returns_GetTargetAction(walk_map, hero):
    confusion_scroll = factory.mk_entity('confusion_scroll', 1, 0)
    hero.inv.add_item(confusion_scroll)

    action = actions.UseItemAction(inv_index=0)  # Assume shield is at index 0

    result = action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)

    assert result.success is False
    assert actions.GetTargetAction in result

    # assert isinstance(result.alt, actions.GetTargetAction)


@pytest.mark.skip('lazy')
def test_UseItemAction__consumed_item(walk_map, hero):
    # Damage the hero a little so we can use the potion
    hero.fighter.take_dmg(10)

    potion = factory.mk_entity('healing_potion', 1, 0)
    hero.inv.add_item(potion)

    action = actions.UseItemAction(inv_index=0)  # Assume potion is at index 0
    results = action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)
    assert len(results) == 1

    assert results.success
    # assert result.msg == 'You are already at full health'
    assert potion not in hero.inv.items


def test_UseItemAction__did_not_consume_item(walk_map, hero):
    potion = factory.mk_entity('healing_potion', 1, 0)
    hero.inv.add_item(potion)

    action = actions.UseItemAction(inv_index=0)  # Assume potion is at index 0
    results = action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)
    assert len(results) == 1

    assert results[0].success is False
    # assert result[0].msg == 'You are already at full health'
    assert potion in hero.inv.items

    # assert action.results == [{ 'consumed': False, }]


def test_UseItemAction__invalid_item(walk_map, hero):
    rock = factory.mk_entity('rock', 1, 0)
    hero.inv.add_item(rock)

    action = actions.UseItemAction(inv_index=0)  # Assume rock is at index 0
    results = action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)

    assert results[0].success is False
    assert results[0].msg == 'The {} cannot be used.'.format(rock.name)


""" Tests for EquipAction """


def test_EquipAction__init(hero):
    action = actions.EquipAction(e=hero, item=None)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn


def test_EquipAction__non_equippable_item(hero):
    potion = factory.mk_entity('healing_potion', 1, 0)
    hero.inv.add_item(potion)

    action = actions.EquipAction(e=hero, item=potion)  # Assume shield is at index 0
    result = action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)

    # assert action.results[0]['equipped'] is False
    assert result.success is False
    assert result.msg == 'You cannot equip the {}'.format(potion.name)


def test_EquipAction__already_equipped__dequips_item(hero):
    shield = factory.mk_entity('shield', 1, 0)
    hero.inv.add_item(shield)
    hero.equipment.toggle_equip(shield)  # Equip the thing

    action = actions.EquipAction(e=hero, item=shield)  # Assume shield is at index 0
    result = action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)

    assert result.success
    assert result.msg == 'You dequipped the {}'.format(shield.name)
    # {'dequipped': shield}, ]


def test_EquipAction__not_equipped__equips_item(hero):
    shield = factory.mk_entity('shield', 1, 0)
    hero.inv.add_item(shield)

    action = actions.EquipAction(e=hero, item=shield)  # Assume shield is at index 0
    result = action.perform(stage=walk_map, fov_map=None, entity=hero, prev_state=None)

    assert result.success
    assert result.msg == 'You equipped the {}'.format(shield.name)
    # {'equipped': shield},


""" Tests for class GetTargetAction """



""" Tests for DropItemAction """


def test_DropItemAction__init():
    action = actions.DropItemAction(inv_index=0)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn


# def test_DropItemAction__item_DNE_raise_exception(potion, hero):
    # with pytest.raises(ValueError):
        # hero.inv.drop(potion)


def test_DropItemAction__inv_index_out_of_bounds(walk_map, hero):
    action = actions.DropItemAction(inv_index=-1)
    with pytest.raises(IndexError):
        action.perform(stage=walk_map, entity=hero, prev_state=config.States.ACTOR_TURN)


def test_DropItemAction__valid_item(walk_map, hero):
    potion = factory.mk_entity('healing_potion', 1, 0)
    hero.inv.add_item(potion)

    action = actions.DropItemAction(inv_index=0)  # Assume potion is at index 0
    result = action.perform(stage=walk_map, entity=hero, prev_state=None)
    assert result.success
    assert result.msg == 'You dropped the {}.'.format(potion.name)
    assert potion not in hero.inv.items
    assert potion in walk_map.entities
    assert potion.x == hero.x
    assert potion.y == hero.y


def test_DropItemAction__equipped_item(walk_map, sword, hero):
    hero.inv.add_item(sword)
    hero.equipment.toggle_equip(sword)

    action = actions.DropItemAction(inv_index=0)  # Assume sword is at index 0
    result = action.perform(stage=walk_map, entity=hero, prev_state=None)

    # Should we request the EquipAction??
    # assert results[0]['dequipped'] == sword
    assert result.success
    assert result.msg == 'You dropped the Sword.'

    assert sword not in hero.inv.items
    assert sword in walk_map.entities
    assert sword.x == hero.x
    assert sword.y == hero.y


""" Tests for StairUpAction """


def test_StairUpAction__init():
    action = actions.StairUpAction()
    assert isinstance(action, actions.Action)
    assert action.consumes_turn


def test_StairUpAction__not_at_stairs(hero, test_game):
    d = test_game.dungeon
    stage = d.get_stage()

    # Remove the stair up for testing
    stage.entities.remove(stage.find_stair('<'))

    action = actions.StairUpAction()
    result = action.perform(dungeon=d, entity=hero, game=test_game)
    assert result.success is False
    assert result.msg == 'There are no stairs here.'


def test_StairUpAction__top_stage__returns_LeaveGameAction(test_game, hero):
    d = test_game.dungeon
    action = actions.StairUpAction()
    result = action.perform(dungeon=d, entity=hero, game=test_game)

    assert result.success is False
    # todo: Move these to LeaveGameAction
    # assert result.msg == 'You go up the stairs and leave the dungeon forever...'
    # assert result.state == config.States.HERO_DEAD
    # assert isinstance(result.alt, actions.LeaveGameAction)
    assert actions.LeaveGameAction in result


def test_StairUpAction__success_on_lower_level(test_game, hero):
    d = test_game.dungeon

    # Create another stage, then move the hero to that stage's upstair
    d.mk_next_stage()
    s = d.stages[1].find_stair('<')
    d.move_hero(1, s.x, s.y)

    action = actions.StairUpAction()
    result = action.perform(dungeon=d, entity=hero, game=test_game)
    assert result.success
    assert result.msg == 'You ascend the stairs up.'
    assert test_game.redraw


""" Tests for StairDownAction """


def test_StairDownAction__init():
    action = actions.StairDownAction()
    assert isinstance(action, actions.Action)
    assert action.consumes_turn


def test_StairDownAction__not_at_stairs(test_game, hero):
    d = test_game.dungeon
    stage = d.get_stage()

    # Remove the stair up for testing
    stage.entities.remove(stage.find_stair('>'))

    action = actions.StairDownAction()
    result = action.perform(dungeon=d, entity=hero, game=test_game)
    assert result.success is False
    assert result.msg == 'There are no stairs here.'


def test_StairDownAction__next_stage_DNE(test_game, hero):
    d = test_game.dungeon
    prev_stages = len(d.stages)

    s = d.get_stage().find_stair('>')
    d.move_hero(0, s.x, s.y)

    # Find the stairs down and put the hero there for testing
    action = actions.StairDownAction()
    result = action.perform(dungeon=d, entity=hero, game=test_game)

    assert result.success
    assert len(d.stages) == prev_stages + 1
    assert test_game.redraw


def test_StairDownAction__next_stage_exists(test_game, hero):
    d = test_game.dungeon

    s = d.get_stage().find_stair('>')
    d.move_hero(0, s.x, s.y)

    # Create the next stage
    d.mk_next_stage()

    # Find the stairs down and put the hero there for testing
    action = actions.StairDownAction()
    result = action.perform(dungeon=d, entity=hero, game=test_game)

    assert result.success
    assert result.msg == 'You carefully descend the stairs down.'
    assert test_game.redraw


""" Tests for LevelUpAction """


def test_LevelUpAction__init():
    action = actions.LevelUpAction('hp')

    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False


def test_LevelUpAction__invalid_stat():
    with pytest.raises(ValueError):
        actions.LevelUpAction(stat='boogers')


def test_LevelUpAction__boost_hp(hero):
    prev_state = config.States.ACTOR_TURN
    action = actions.LevelUpAction(stat='hp')
    result = action.perform(entity=hero, prev_state=prev_state)

    assert result.success
    assert result.msg == 'Boosted max HP!'
    assert result.new_state == prev_state


def test_LevelUpAction__boost_strength(hero):
    prev_state = config.States.ACTOR_TURN
    action = actions.LevelUpAction(stat='str')
    result = action.perform(entity=hero, prev_state=prev_state)

    assert result.success
    assert result.msg == 'Boosted strength!'
    assert result.new_state == prev_state


def test_LevelUpAction__boost_defense(hero):
    prev_state = config.States.ACTOR_TURN
    action = actions.LevelUpAction(stat='def')
    result = action.perform(entity=hero, prev_state=prev_state)

    assert result.success
    assert result.msg == 'Boosted defense!'
    assert result.new_state == prev_state


""" Tests for ExitAction """


def test_ExitAction__init():
    state = config.States.SHOW_INV
    action = actions.ExitAction(state)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False


def test_ExitAction__SHOW_INV_returns_to_ACTOR_TURN():
    state = config.States.SHOW_INV
    action = actions.ExitAction(state)

    prev_state = config.States.ACTOR_TURN
    result = action.perform(prev_state=prev_state)

    assert result.success
    assert result.new_state == prev_state


def test_ExitAction__DROP_INV_returns_to_ACTOR_TURN():
    state = config.States.DROP_INV
    action = actions.ExitAction(state)

    prev_state = config.States.ACTOR_TURN
    result = action.perform(prev_state=prev_state)
    assert result.new_state == prev_state


def test_ExitAction__SHOW_STATS_returns_to_ACTOR_TURN():
    state = config.States.SHOW_STATS
    action = actions.ExitAction(state)

    prev_state = config.States.ACTOR_TURN
    result = action.perform(prev_state=prev_state)
    assert result.new_state == prev_state


def test_ExitAction__TARGETING_returns_to_ACTOR_TURN():
    state = config.States.TARGETING
    action = actions.ExitAction(state)

    prev_state = config.States.ACTOR_TURN
    result = action.perform(prev_state=prev_state)

    assert result.new_state == prev_state
    assert result.msg == 'Targeting cancelled.'
    # 'cancel_target': True,


def test_ExitAction__ACTOR_TURN_returns_to_MAIN_MENU():
    state = config.States.ACTOR_TURN
    action = actions.ExitAction(state)

    prev_state = config.States.MAIN_MENU
    result = action.perform(prev_state=prev_state)
    assert result.new_state == prev_state


""" Tests for FullScreenAction """


def test_FullScreenAction__init():
    fullscreen = actions.FullScreenAction()
    assert isinstance(fullscreen, actions.Action)
    assert fullscreen.consumes_turn is False


def test_FullScreenAction__calls_tcod_console_set_fullscreen(mocker):
    mocker.patch('tcod.console_set_fullscreen')

    fullscreen = actions.FullScreenAction()
    result = fullscreen.perform()

    assert result.success
    tcod.console_set_fullscreen.assert_called_with(fullscreen=not tcod.console_is_fullscreen())


""" Tests for GetTargetAction """


def test_GetTargetAction_init():
    target = actions.GetTargetAction(item=None)
    assert isinstance(target, actions.Action)
    assert target.consumes_turn is False


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


def test_TargetAction__no_click_raises_exception():
    with pytest.raises(ValueError):
        actions.TargetAction(x=0, y=0)


def test_TargetAction__both_clicks_raises_exception():
    with pytest.raises(ValueError):
        actions.TargetAction(x=0, y=0, lclick=True, rclick=True)


""" Tests for ShowInvAction """


def test_ShowInvAction__init():
    prev_state = config.States.ACTOR_TURN
    action = actions.ShowInvAction(prev_state)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False


def test_ShowInvAction():
    prev_state = config.States.ACTOR_TURN
    action = actions.ShowInvAction(prev_state)
    result = action.perform()
    assert result.success
    assert result.new_state == config.States.SHOW_INV


""" Tests for DropInvAction """


def test_DropInvAction__init():
    prev_state = config.States.ACTOR_TURN
    action = actions.DropInvAction(prev_state)

    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False


def test_DropInvAction():
    prev_state = config.States.ACTOR_TURN
    action = actions.DropInvAction(prev_state)
    result = action.perform()
    assert result.new_state == config.States.DROP_INV


""" Tests for CharScreenAction """


def test_CharScreenAction__init():
    prev_state = config.States.ACTOR_TURN
    char_scr = actions.CharScreenAction(prev_state)
    assert isinstance(char_scr, actions.Action)
    assert char_scr.consumes_turn is False


def test_CharScreenAction():
    prev_state = config.States.ACTOR_TURN
    action = actions.CharScreenAction(prev_state)
    result = action.perform()
    assert result.success
    assert result.new_state == config.States.SHOW_STATS


""" Tests for KillMonsterAction """


def test_KillMonsterAction_init(orc):
    action = actions.KillMonsterAction(attacker=None, defender=orc)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False


def test_KillMonsterAction_hero_raises_exception(hero):
    with pytest.raises(ValueError):
        action = actions.KillMonsterAction(attacker=None, defender=hero)


def test_KillMonsterAction__success(orc):
    action = actions.KillMonsterAction(attacker=None, defender=orc)
    result = action.perform()
    assert result.success
    assert result.msg == 'The Orc dies!'


def test_KillMonsterAction__char_is_corpse(orc):
    action = actions.KillMonsterAction(attacker=None, defender=orc)
    action.perform()
    assert orc.char == '%'


def test_KillMonsterAction__name_changed_to_remains(orc):
    action = actions.KillMonsterAction(attacker=None, defender=orc)
    action.perform()
    assert orc.name == 'remains of Orc'


def test_KillMonsterAction__color_is_darkred(orc):
    action = actions.KillMonsterAction(attacker=None, defender=orc)
    action.perform()
    assert orc.color == tcod.dark_red


def test_KillMonsterAction__blocks_is_False(orc):
    action = actions.KillMonsterAction(attacker=None, defender=orc)
    action.perform()
    assert orc.blocks is False


def test_KillMonsterAction__renderorder_is_CORPSE(orc):
    action = actions.KillMonsterAction(attacker=None, defender=orc)
    action.perform()
    assert orc.render_order == config.RenderOrder.CORPSE


def test_KillMonsterAction__fighter_comp_removed(orc):
    action = actions.KillMonsterAction(attacker=None, defender=orc)
    action.perform()
    assert orc.has_comp('fighter') is False


def test_KillMonsterAction__ai_comp_removed(orc):
    action = actions.KillMonsterAction(attacker=None, defender=orc)
    action.perform()
    assert orc.has_comp('ai') is False


def test_KillMonsterAction__item_comp_added(orc):
    action = actions.KillMonsterAction(attacker=None, defender=orc)
    action.perform()
    assert orc.has_comp('item')


# Is this really necessary?
# def test_KillMonsterAction__monster_already_dead(orc):


""" Tests for KillPlayerAction """


def test_KillPlayerAction_init(hero):
    action = actions.KillPlayerAction(attacker=None, defender=hero)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False


def test_KillPlayerAction__not_hero_raises_exception():
    orc = factory.mk_entity('orc', 2, 1)

    with pytest.raises(ValueError):
        action = actions.KillPlayerAction(attacker=None, defender=orc)


def test_KillPlayerAction_success(hero, orc):
    action = actions.KillPlayerAction(attacker=orc, defender=hero)
    result = action.perform()
    assert result.success
    assert result.msg == 'You died!  Killed by the Orc.'
    assert result.new_state == config.States.HERO_DEAD


def test_KillPlayerAction_char_is_corpse(hero, orc):
    action = actions.KillPlayerAction(attacker=orc, defender=hero)
    action.perform()
    assert hero.char == '%'


def test_KillPlayerAction_color_is_darkred(hero, orc):
    action = actions.KillPlayerAction(attacker=orc, defender=hero)
    action.perform()
    assert hero.color == tcod.dark_red


""" Tests for AddXPAction """


def test_AddXPAction_init(hero):
    action = actions.AddXPAction(entity=hero, xp=1)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False


def test_AddXPAction__adds_xp(hero):
    prev_xp = hero.lvl.current_xp
    xp_amt = 1
    action = actions.AddXPAction(entity=hero, xp=1)
    result = action.perform()

    assert result.success
    assert hero.lvl.current_xp == prev_xp + xp_amt


def test_AddXPAction__leveled_up(hero):
    xp_amt = hero.lvl.xp_to_next_lvl + 1  # make sure we go over the threshold
    action = actions.AddXPAction(entity=hero, xp=xp_amt)
    result = action.perform()

    assert result.success
    assert result.new_state == config.States.LEVEL_UP
    assert result.msg == 'Your battle skills grow stronger! You reached level {}!'.format(hero.lvl.current_lvl)


""" Tests for LeaveGameAction """


def test_LeaveGameAction_init():
    action = actions.LeaveGameAction()
    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False

# msg
# new_state is hero dead


""" Tests for TakeDmgAction """


def test_TakeDmgAction_init(orc):
    action = actions.TakeDmgAction(attacker=None, defender=orc, dmg=1)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False


def test_TakeDmgAction_reduces_hp(orc):
    action = actions.TakeDmgAction(attacker=None, defender=orc, dmg=1)
    result = action.perform()

    assert result.success
    assert orc.fighter.hp == orc.fighter.max_hp - 1


def test_TakeDmgAction_negative_dmg_raises_exception(orc):
    with pytest.raises(ValueError):
        actions.TakeDmgAction(attacker=None, defender=orc, dmg=-1)


def test_TakeDmgAction_lethal_dmg_to_monster_returns_KillMonsterAction(orc):
    lethal_dmg = orc.fighter.max_hp
    action = actions.TakeDmgAction(attacker=None, defender=orc, dmg=lethal_dmg)
    result = action.perform()

    assert result.success
    assert actions.KillMonsterAction in result


def test_TakeDmgAction_lethal_dmg_to_hero_returns_KillPlayerAction(hero):
    lethal_dmg = hero.fighter.max_hp
    action = actions.TakeDmgAction(attacker=None, defender=hero, dmg=lethal_dmg)
    result = action.perform()

    assert result.success
    assert actions.KillPlayerAction in result


""" Tests for HealAction """


def test_HealAction_init(orc):
    action = actions.HealAction(entity=orc, amt=1)
    assert isinstance(action, actions.Action)
    assert action.consumes_turn is False


def test_HealAction__success_hp_is_recovered(orc):
    prev_hp = orc.fighter.hp
    dmg = 2
    action = actions.HealAction(entity=orc, amt=dmg)

    # Inflict a little damage for the heal to work
    orc.fighter.hp -= dmg

    result = action.perform()

    assert result.success
    assert orc.fighter.hp == prev_hp


def test_HealAction__excess_hp_doesnt_go_over_max(orc):
    amt = orc.fighter.max_hp + 100
    action = actions.HealAction(entity=orc, amt=amt)

    # Inflict a little damage for the heal to work
    orc.fighter.hp -= 2

    result = action.perform()

    assert result.success
    assert orc.fighter.hp == orc.fighter.max_hp


def test_HealAction__hp_already_max__returns_False(orc):
    action = actions.HealAction(entity=orc, amt=10)
    result = action.perform()

    assert result.success is False


def test_HealAction__negative_amt_raises_exception(orc):
    with pytest.raises(ValueError):
        actions.HealAction(entity=orc, amt=-1)


""" Tests for MoveAStarAction """


def test_MoveAStarAction_init(fov_stage):
    action = actions.MoveAStarAction(
        stage=fov_stage,
        entity=orc,
        target=hero
    )
    assert isinstance(action, actions.Action)
    assert action.consumes_turn


def test_MoveAStarAction__target_next_sq(fov_stage):
    fov_stage.hero_ref.x = 2
    fov_stage.hero_ref.y = 0

    action = actions.MoveAStarAction(
        stage=fov_stage,
        entity=fov_stage.orc_ref,
        target=fov_stage.hero_ref
    )
    result = action.perform()
    assert isinstance(result.alt, actions.WalkAction)
    assert result.alt.dx == 1
    assert result.alt.dy == 0


def test_MoveAStarAction__target_knights_jump_away(fov_stage):
    fov_stage.hero_ref.x = 0
    fov_stage.hero_ref.y = 2

    action = actions.MoveAStarAction(
        stage=fov_stage,
        entity=fov_stage.orc_ref,
        target=fov_stage.hero_ref
    )
    result = action.perform()
    assert isinstance(result.alt, actions.WalkAction)
    assert result.alt.dx == -1
    assert result.alt.dy == 1

def test_MoveAStarAction__target_around_wall(fov_stage):
    fov_stage.hero_ref.x = 1
    fov_stage.hero_ref.y = 4

    action = actions.MoveAStarAction(
        stage=fov_stage,
        entity=fov_stage.orc_ref,
        target=fov_stage.hero_ref
    )
    result = action.perform()
    assert isinstance(result.alt, actions.WalkAction)
    assert result.alt.dx == -1
    assert result.alt.dy == 1


def test_MoveAStarAction__target_behind_wall(fov_stage):
    fov_stage.hero_ref.x = 2
    fov_stage.hero_ref.y = 2

    action = actions.MoveAStarAction(
        stage=fov_stage,
        entity=fov_stage.orc_ref,
        target=fov_stage.hero_ref
    )
    result = action.perform()
    assert isinstance(result.alt, actions.WalkAction)
    assert result.alt.dx == -1
    assert result.alt.dy == 1


def test_MoveAStarAction__target_in_opposite_corner(fov_stage):
    fov_stage.hero_ref.x = 6
    fov_stage.hero_ref.y = 5

    action = actions.MoveAStarAction(
        stage=fov_stage,
        entity=fov_stage.orc_ref,
        target=fov_stage.hero_ref
    )
    result = action.perform()
    assert isinstance(result.alt, actions.WalkAction)
    assert result.alt.dx == 1
    assert result.alt.dy == 0


def test_MoveAStarAction__target_to_side(fov_stage):
    fov_stage.hero_ref.x = 6
    fov_stage.hero_ref.y = 1

    action = actions.MoveAStarAction(
        stage=fov_stage,
        entity=fov_stage.orc_ref,
        target=fov_stage.hero_ref
    )
    result = action.perform()
    assert isinstance(result.alt, actions.WalkAction)
    assert result.alt.dx == 1
    assert result.alt.dy == 0

# def test_MoveAStarAction__target_is_same_as_origin(fov_stage):


""" Tests for MoveTowardAction"""


def test_MoveTowardAction__init(open_map, hero, orc):
    action = actions.MoveTowardAction(
        stage=open_map,
        entity=orc,
        target=hero
    )
    assert isinstance(action, actions.Action)
    assert action.consumes_turn


def test_MoveTowardAction__blocked__fails(open_map, hero, orc):
    open_map.tiles[6][6].blocks = True
    open_map.entities.extend([hero, orc])
    orc.x, orc.y = 5, 5
    hero.x, hero.y = 7, 7

    action = actions.MoveTowardAction(stage=open_map, entity=orc, target=hero)
    result = action.perform()

    assert result.success is False


# def test_MoveTowardAction__target_1_sq_N__returns_AttackAction(open_map, hero, orc):
    # open_map.entities.extend([hero, orc])
    # orc.x, orc.y = 5, 5
    # hero.x, hero.y = 5, 4
    # action = actions.MoveTowardAction(stage=open_map, entity=orc, target=hero)
    # result = action.perform()
    # assert actions.AttackAction in result
    # assert result.success is False
    # assert result.alt.entity == orc
    # assert result.alt.target == hero


def test_MoveTowardAction__target_2_sq_N__returns_WalkAction(open_map, hero, orc):
    open_map.entities.extend([hero, orc])
    orc.x, orc.y = 5, 5
    hero.x, hero.y = 5, 3

    action = actions.MoveTowardAction(stage=open_map, entity=orc, target=hero)
    result = action.perform()

    assert actions.WalkAction in result
    assert result.success is True
    assert result.alt.dx == 0
    assert result.alt.dy == -1


def test_MoveTowardAction__target_3_sq_N__returns_WalkAction(open_map, hero, orc):
    open_map.entities.extend([hero, orc])
    orc.x, orc.y = 5, 5
    hero.x, hero.y = 5, 2

    action = actions.MoveTowardAction(stage=open_map, entity=orc, target=hero)
    result = action.perform()

    assert actions.WalkAction in result
    assert result.success is True
    assert result.alt.dx == 0
    assert result.alt.dy == -1



# def test_MoveTowardAction__target_1_sq_SE_returns_AttackAction(open_map, hero, orc):
    # open_map.entities.extend([hero, orc])
    # orc.x, orc.y = 5, 5
    # hero.x, hero.y = 6, 6

    # action = actions.MoveTowardAction(stage=open_map, entity=orc, target=hero)
    # result = action.perform()

    # assert actions.AttackAction in result
    # assert result.success is False
    # assert result.alt.entity == orc
    # assert result.alt.target == hero


def test_MoveTowardAction__target_2_sq_SE_returns_WalkAction(open_map, hero, orc):
    open_map.entities.extend([hero, orc])
    orc.x, orc.y = 5, 5
    hero.x, hero.y = 7, 7

    action = actions.MoveTowardAction(stage=open_map, entity=orc, target=hero)
    result = action.perform()

    assert actions.WalkAction in result
    assert result.success
    assert result.alt.dx == 1
    assert result.alt.dy == 1


def test_MoveTowardAction__target_knights_jump_SE_returns_WalkAction(open_map, hero, orc):
    open_map.entities.extend([hero, orc])
    orc.x, orc.y = 5, 5
    hero.x, hero.y = 6, 7

    action = actions.MoveTowardAction(stage=open_map, entity=orc, target=hero)
    result = action.perform()

    assert actions.WalkAction in result
    assert result.success
    assert result.alt.dx == 0
    assert result.alt.dy == 1
