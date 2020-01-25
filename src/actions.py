from abc import ABC, abstractmethod
import tcod
from . import config
from . import components
from . import stages
from .config import States


class Action(ABC):
    def __init__(self, consumes_turn=True):
        self.consumes_turn = consumes_turn

    @abstractmethod
    def perform(self, *args, **kwargs):
        pass

    def __str__(self):
        return self.__class__.__name__

class ActionResult(object):
    # Implement contains for alternate actions?
    def __init__(self, success=False, alt=None, new_state=None, msg=None):
        self.success = success
        self.new_state = new_state
        self.msg = msg

        # todo: Remove after overhaul
        if isinstance(alt, list):
            raise ValueError('no lists!!!')

        self.alt = alt

    def __contains__(self, action):
        """Checks if the passed action's class is in the list of alt actions."""
        if isinstance(action, str):
            return str(self.alt) == action

        return isinstance(self.alt, action)


class WalkAction(Action):
    def __init__(self, dx, dy):
        super().__init__(consumes_turn=True)
        if abs(dx) > 1 or abs(dy) > 1:
            raise ValueError('WalkAction dx or dy cannot be < -1 or > 1.')
        self.dx = dx
        self.dy = dy

        # redraw_fov_on_success?

    def perform(self, *args, **kwargs):
        entity = kwargs['entity']
        stage = kwargs['stage']
        _game = kwargs['game']

        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        # Check for wall
        if stage.is_blocked(dest_x, dest_y):
            # There is a wall blocking our path
            return ActionResult(
                success=False,
                msg='You cannot walk into the wall...'
            )

        # Check for attacker
        target = stage.get_blocker_at_loc(dest_x, dest_y)
        if target:
            # return ActionResult(alt=AttackAction(attacker=entity, defender=target))

            return ActionResult(
                success=False,
                msg='You cannot walk into the actor!...'
            )

        # log.debug('Moving.')
        entity.move(self.dx, self.dy)

        # Need to redraw FOV
        _game.fov_recompute = True

        # Add walk into door
        # Add walk into water/lava/etc
        # Add walk over items

        return ActionResult(success=True)


class AttackAction(Action):
    def __init__(self, attacker, defender):
        super().__init__()
        if not attacker.has_comp('fighter'):
            raise ValueError('AttackAction requires attacker with Fighter component!')
        elif not defender.has_comp('fighter'):
            raise ValueError('AttackAction requires defender with Fighter component!')

        self.attacker = attacker
        self.defender = defender

    def perform(self, *args, **kwargs):

        dmg = self.attacker.fighter.power - self.defender.fighter.defense

        if dmg > 0:
            msg = '{} attacks {}!'.format(self.attacker.name, self.defender.name)

            return ActionResult(
                success=True,
                alt=TakeDmgAction(self.attacker, self.defender, dmg),
                msg=msg
            )

        msg = '{} attacks {}... But does no damage.'.format(self.attacker.name, self.defender.name)
        return ActionResult(success=True, msg=msg)



class WaitAction(Action):
    def perform(self, *args, **kwargs):
        return ActionResult(success=True)


class PickupAction(Action):
    def perform(self, *args, **kwargs):
        stage = kwargs['stage']
        entity = kwargs['entity']

        # todo: Move this functionality to stage....
        for e in stage.entities:
            item_pos_at_our_pos = e.x == entity.x and e.y == entity.y

            if e.has_comp('item') and item_pos_at_our_pos:
                success = entity.inv.add_item(e)

                if success:
                    return ActionResult(
                        success=True,
                        msg='You pick up the {}.'.format(e.name)
                    )

                return ActionResult(
                    success=False,
                    msg='You cannot carry any more, your inventory is full.'
                )

        return ActionResult(
            success=False,
            msg='There is nothing here to pick up.'
        )


class UseItemAction(Action):
    # todo: Let UseItemAction work on items NOT in an entity's inventory
    # todo: Use item on ground
    # todo: Use item that was thrown, etc.

    def __init__(self, inv_index, target_x=None, target_y=None):
        super().__init__()
        self.inv_index = inv_index
        self.target_x = target_x
        self.target_y = target_y

    def perform(self, *args, **kwargs):
        stage = kwargs['stage']
        fov_map = kwargs['fov_map']
        entity = kwargs['entity']
        item_entity = entity.inv.items[self.inv_index]
        item_comp = item_entity.item

        if item_comp.use_func is None:
            equippable_comp = item_entity.equippable if item_entity.has_comp('equippable') else None

            # If item is equippable, return an EquipAction
            if equippable_comp:
                return ActionResult(alt=EquipAction(entity, item_entity))

            # This item doesn't have a use function!
            return [ActionResult(
                success=False,
                msg='The {} cannot be used.'.format(item_entity.name)
            )]

        else:
            have_target = self.target_x and self.target_y

            # If the item requires a target, return a GetTargetAction
            if item_comp.targeting and not have_target:
                return ActionResult(alt=GetTargetAction(item_entity))

            kwargs.update(item_comp.func_kwargs)
            results = item_comp.use_func.use(entity, **kwargs)

            # Use the item - was it consumed?
            # item_use_results = entity.inv.use(
                # item_entity,
                # entities=stage.entities,
                # fov_map=fov_map,
                # target_x=self.target_x,
                # target_y=self.target_y
            # )

            # If the item was consumed - remove it from inventory.
            if results[0].success:
                entity.inv.rm_item(item_entity)

            else:
                # Not consumed
                pass
            return results


class EquipAction(Action):
    def __init__(self, e, item):
        super().__init__()
        self.e = e
        self.item = item

    def perform(self, *args, **kwargs):
        entity = kwargs['entity']
        if not self.item.has_comp('equippable'):
            return ActionResult(
                success=False,
                msg='You cannot equip the {}'.format(self.item.name)
            )
        else:
            equip_results = entity.equipment.toggle_equip(self.item)

            for equip_result in equip_results:
                equipped = equip_result.get('equipped')
                dequipped = equip_result.get('dequipped')

                if equipped:
                    return ActionResult(
                        success=True,
                        msg='You equipped the {}'.format(equipped.name)
                    )

                if dequipped:
                    return ActionResult(
                        success=True,
                        msg='You dequipped the {}'.format(dequipped.name)
                    )


# class UnequipAction():
    # def __init__(self, e, item):
        # pass


class DropItemAction(Action):
    def __init__(self, inv_index):
        super().__init__()
        self.inv_index = inv_index

    def perform(self, *args, **kwargs):
        entity = kwargs['entity']
        item = entity.inv.items[self.inv_index]

        if item not in entity.inv.items:
            raise ValueError('Cannot drop an item that is not in inventory!')

        # Dequip equipped items before dropping
        if item.has_comp('equippable'):
            if entity.equipment.main_hand == item or entity.equipment.off_hand == item:

                # todo: This might also benefit from an Action replacement
                entity.equipment.toggle_equip(item)

        item.x = entity.x
        item.y = entity.y

        entity.inv.rm_item(item)

        return ActionResult(
            success=True,
            msg='You dropped the {}.'.format(item.name)
        )


class StairUpAction(Action):
    def perform(self, *args, **kwargs):
        dungeon = kwargs['dungeon']
        entity = kwargs['entity']
        game = kwargs['game']

        stage = dungeon.get_stage()

        for entity in stage.entities:
            if entity.has_comp('stair_up'):
                hero_at_stairs = entity.x == entity.x and entity.y == entity.y
                if hero_at_stairs:

                    if dungeon.current_stage == 0:

                        return ActionResult(
                            success=False,
                            alt=LeaveGameAction(),
                            msg='You go up the stairs and leave the dungeon forever...',
                            new_state=States.HERO_DEAD
                        )

                    elif dungeon.move_upstairs():
                        stage = dungeon.get_stage()
                        game.redraw = True

                        return ActionResult(
                            success=True,
                            msg='You ascend the stairs up.'
                        )
                    else:
                        raise ValueError("Something weird happened with going upstairs!")

        return ActionResult(
            success=False,
            msg='There are no stairs here.'
        )


class StairDownAction(Action):
    def perform(self, *args, **kwargs):
        dungeon = kwargs['dungeon']
        entity = kwargs['entity']
        game = kwargs['game']
        stage = dungeon.get_stage()

        for entity in stage.entities:
            if entity.has_comp('stair_down'):
                hero_at_stairs = entity.x == entity.x and entity.y == entity.y

                if hero_at_stairs:
                    dungeon.mk_next_stage()

                    if dungeon.move_downstairs():
                        stage = dungeon.get_stage()
                        stage.populate()
                        game.redraw = True
                        return ActionResult(
                            success=True,
                            msg='You carefully descend the stairs down.',
                        )
                    else:
                        raise ValueError("Something weird happened with going downstairs!")

        return ActionResult(
            success=False,
            msg='There are no stairs here.'
        )


class LevelUpAction(Action):
    def __init__(self, stat):
        super().__init__(consumes_turn=False)
        valid_stats = ['hp', 'str', 'def']
        if stat in valid_stats:
            self.stat = stat
        else:
            raise ValueError('stat not valid! Must be one of: {}'.format(valid_stats))

    def perform(self, *args, **kwargs):
        entity = kwargs['entity']
        prev_state = kwargs['prev_state']

        if self.stat == 'hp':
            entity.fighter.base_max_hp += 20
            entity.fighter.hp += 20
            return ActionResult(success=True, msg='Boosted max HP!', new_state=States.ACTOR_TURN)


        elif self.stat == 'str':
            entity.fighter.base_power += 1
            return ActionResult(success=True, msg='Boosted strength!', new_state=States.ACTOR_TURN)

        elif self.stat == 'def':
            entity.fighter.base_defense += 1
            return ActionResult(success=True, msg='Boosted defense!', new_state=States.ACTOR_TURN)

        else:
            raise ValueError('invalid stat!')


class ExitAction(Action):
    def __init__(self, state):
        super().__init__(consumes_turn=False)
        self.state = state

    def perform(self, *args, **kwargs):
        prev_state = kwargs['prev_state']

        if self.state in (States.SHOW_INV, States.DROP_INV, States.SHOW_STATS):
            return ActionResult(success=True, new_state=prev_state)

        elif self.state == States.TARGETING:
            return ActionResult(
                success=True,
                new_state=prev_state,
                msg='Targeting cancelled.',
            )

        else:
            return ActionResult(success=True, new_state=States.MAIN_MENU)


class FullScreenAction(Action):
    def __init__(self):
        super().__init__(consumes_turn=False)

    def perform(self, *args, **kwargs):
        # Toggle fullscreen on/off
        tcod.console_set_fullscreen(fullscreen=not tcod.console_is_fullscreen())
        return ActionResult(success=True)


class GetTargetAction(Action):
    def __init__(self, item):
        super().__init__(consumes_turn=False)
        self.item = item

    def perform(self, *args, **kwargs):
        return ActionResult(
            success=True,
            new_state=States.TARGETING
        )


class TargetAction(Action):
    def __init__(self, x, y, lclick=None, rclick=None):
        if not lclick and not rclick:
            raise ValueError('TargetAction requires exactly 1 mouse button to be clicked.')
        elif lclick and rclick:
            raise ValueError('TargetAction requires exactly 1 mouse button to be clicked.')

        super().__init__(consumes_turn=False)
        self.x = x
        self.y = y
        self.lclick = lclick
        self.rclick = rclick

    def perform(self, *args, **kwargs):
        targeting_item = kwargs['targeting_item']
        state = kwargs['state']

        if self.lclick:
            # note: Due to the message console - we have to offset the y.
            self.y -= config.msg_height
            use_item_action = UseItemAction(targeting_item, target_x=self.x, target_y=self.y)
            return ActionResult(alt=use_item_action)

        elif self.rclick:
            return ActionResult(
                success=False,
                alt=ExitAction(state)
            )

class ShowInvAction(Action):
    def __init__(self, prev_state):
        super().__init__(consumes_turn=False)
        self.prev_state = prev_state

    def perform(self, *args, **kwargs):
        return ActionResult(
            success=True,
            new_state=States.SHOW_INV
        )

class DropInvAction(Action):
    def __init__(self, prev_state):
        super().__init__(consumes_turn=False)
        self.prev_state = prev_state

    def perform(self, *args, **kwargs):
        return ActionResult(
            success=True,
            new_state=States.DROP_INV
        )


class CharScreenAction(Action):
    def __init__(self, prev_state):
        super().__init__(consumes_turn=False)
        self.prev_state = prev_state

    def perform(self, *args, **kwargs):
        return ActionResult(
            success=True,
            new_state=States.SHOW_STATS
        )


class KillMonsterAction(Action):
    def __init__(self, attacker, defender):
        super().__init__(consumes_turn=False)
        if defender.has_comp('human'):
            raise ValueError('KillPlayerAction requires the entity to be a Monster!')

        self.attacker = attacker
        self.defender = defender

    def perform(self, *args, **kwargs):
        self.defender.char = '%'
        self.defender.color = tcod.dark_red
        self.defender.blocks = False
        self.defender.render_order = config.RenderOrder.CORPSE
        self.defender.rm_comp('fighter')
        self.defender.rm_comp('ai')

        # Change to an item so we can pick it up!
        self.defender.item = components.Item(owner=self.defender)

        death_msg = 'The {} dies!'.format(self.defender.name.capitalize())
        self.defender.name = 'remains of ' + self.defender.name

        if self.attacker:
            return ActionResult(
                success=True,
                alt=AddXPAction(self.attacker, self.defender.fighter.xp),
                msg=death_msg
            )

        return ActionResult(
            success=True,
            msg=death_msg
        )


class KillPlayerAction(Action):
    def __init__(self, attacker, defender):
        super().__init__(consumes_turn=False)
        if not defender.has_comp('human'):
            raise ValueError('KillPlayerAction requires the entity to be a Player!')

        self.attacker = attacker
        self.defender = defender

    def perform(self, *args, **kwargs):
        self.defender.char = '%'
        self.defender.color = tcod.dark_red

        return ActionResult(
            success=True,
            msg='You died!  Killed by the {}.'.format(self.attacker.name),
            new_state=States.HERO_DEAD
        )


class AddXPAction(Action):
    def __init__(self, entity, xp):
        super().__init__(consumes_turn=False)
        self.entity = entity
        self.xp = xp

    def perform(self, *args, **kwargs):
        result = self.entity.lvl.add_xp(self.xp)

        if result:
            msg = 'Your battle skills grow stronger! You reached level {}!'.format(self.entity.lvl.current_lvl)
            return ActionResult(
                success=True,
                new_state=States.LEVEL_UP,
                msg=msg
            )
        return ActionResult(success=True)


class LeaveGameAction(Action):
    def __init__(self):
        super().__init__(consumes_turn=False)

    def perform(self, *args, **kwargs):
        pass


class TakeDmgAction(Action):
    def __init__(self, attacker, defender, dmg):
        super().__init__(consumes_turn=False)
        if dmg < 0:
            raise ValueError('TakeDmgAction: dmg must be a positive number!')

        self.attacker = attacker
        self.defender = defender
        self.dmg = dmg

    def perform(self, *args, **kwargs):
        self.defender.fighter.hp -= self.dmg

        if self.defender.fighter.hp <= 0:
            # Kill the correct entity
            if self.defender.has_comp('human'):
                return ActionResult(success=True, alt=KillPlayerAction(self.attacker, self.defender))

            return ActionResult(success=True, alt=KillMonsterAction(self.attacker, self.defender))

        return ActionResult(success=True)


class HealAction(Action):
    def __init__(self, entity, amt):
        if amt < 0:
            raise ValueError('HealAction: amt must be a positive number!')

        super().__init__(consumes_turn=False)
        self.entity = entity
        self.amt = amt

    def perform(self, *args, **kwargs):
        fighter = self.entity.fighter

        # Can't heal if the entity is not damaged
        if fighter.hp == fighter.max_hp:
            return ActionResult(success=False)

        fighter.hp += self.amt

        if fighter.hp > fighter.max_hp:
            fighter.hp = fighter.max_hp

        return ActionResult(success=True)


class MoveAStarAction(Action):
    def __init__(self, stage, entity, target):
        super().__init__(consumes_turn=True)
        self.stage = stage
        self.entity = entity
        self.target = target

    def perform(self, *args, **kwargs):
        # Create a FOV map that has the dimensions of the map
        # DeprecationWarning: Call tcod.map.Map(width, height) instead.
        # fov = tcod.map_new(self.stage.width, self.stage.height)

        fov = tcod.map.Map(width=self.stage.width, height=self.stage.height)

        # Scan the current map each turn and set all the walls as unwalkable
        for y1 in range(self.stage.height):
            for x1 in range(self.stage.width):
                # DeprecationWarning: Set properties using the m.transparent and m.walkable arrays.
                # tcod.map_set_properties( fov, x1, y1, not self.stage.tiles[x1][y1].block_sight, not self.stage.tiles[x1][y1].blocked)

                fov.transparent[y1, x1] = not self.stage.tiles[x1][y1].block_sight
                fov.walkable[y1, x1] = not self.stage.tiles[x1][y1].blocked

        # Scan all the objects to see if there are objects that must be navigated
        # around. Check also that the object isn't self or the target (so that
        # the start and the end points are free). The AI class handles the
        # situation if self is next to the target so it will not use this A* function
        # anyway

        for entity in self.stage.entities:
            if entity.blocks and entity != self and entity != self.target:
                # Set the tile as a wall so it must be navigated around
                # tcod.map_set_properties(fov, entity.x, entity.y, True, False)

                fov.walkable[entity.y, entity.x] = False

        # Allocate a A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0
        # if diagonal moves are prohibited

        # PendingDeprecationWarning: This function may be deprecated in the future.
        my_path = tcod.path_new_using_map(m=fov, dcost=1.41)

        # Compute the path between self's coordinates and the target's coordinates

        # PendingDeprecationWarning: This function may be deprecated in the future.
        # Returns a boolean...
        tcod.path_compute(
            p=my_path,
            ox=self.entity.x,
            oy=self.entity.y,
            dx=self.target.x,
            dy=self.target.y
        )

        # Check if the path exists, and in this case, also the path is shorter
        # than 25 tiles. The path size matters if you want the monster to use
        # alternative longer paths (for example through other rooms) if for
        # example the player is in a corridor. It makes sense to keep path size
        # relatively low to keep the monsters from running around the map if
        # there's an alternative path really far away

        # PendingDeprecationWarning: This function may be deprecated in the future.
        print(tcod.path_size(my_path))
        print(my_path)

        if not tcod.path_is_empty(my_path) and tcod.path_size(my_path) < 25:

            # Find the next coordinates in the computed full path

            # PendingDeprecationWarning: This function may be deprecated in the future.
            x, y = tcod.path_walk(my_path, True)
            if x or y:

                # Set self's coordinates to the next path tile
                dx, dy = self.stage.calc_dxdy(self.entity.x, self.entity.y, x, y)
                print(dx, dy)

                # DeprecationWarning: libtcod objects are deleted automatically.
                # tcod.path_delete(my_path)

                return ActionResult(
                    success=True,
                    alt=WalkAction(dx, dy)
                )

        # Keep the old move function as a backup so that if there are no paths
        # (for example another monster blocks a corridor) it will still try to
        # move towards the player (closer to the corridor opening)
        # self.move_towards(self.target.x, self.target.y, self.stage)

        # DeprecationWarning: libtcod objects are deleted automatically.
        # tcod.path_delete(my_path)

        return ActionResult(
            success=True,
            alt=MoveTowardAction(self.stage, self.entity, self.target)
        )


class MoveTowardAction(Action):
    def __init__(self, stage, entity, target):
        super().__init__(consumes_turn=True)
        self.stage = stage
        self.entity = entity
        self.target = target

    def perform(self, *args, **kwargs):
        """Very simple movement function to take the most direct path toward the hero.  """
        dx, dy = stages.Stage.calc_move(
            self.entity.x,
            self.entity.y,
            self.target.x,
            self.target.y
        )

        dest_x = self.entity.x + dx
        dest_y = self.entity.y + dy

        blocked_at = self.stage.is_blocked(dest_x, dest_y)
        occupied = self.stage.get_blocker_at_loc(dest_x, dest_y)

        if not (blocked_at or occupied):
            return ActionResult(success=True, alt=WalkAction(dx, dy))

        return ActionResult(success=False)
