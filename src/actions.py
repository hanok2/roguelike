from abc import ABC, abstractmethod
import tcod
from . import config
from .config import States


class Action(ABC):
    # todo: Implement a performed boolean - we can't perform an Action more
    # than one time.

    def __init__(self, consumes_turn=True):
        self.consumes_turn = consumes_turn
        self.results = []

    @abstractmethod
    def perform(self, *args, **kwargs):
        # We can return alternate Actions
        # We can return True or False to indicate success
        # Do the parameters need to be (*args, **kwargs)?
        pass


class ActionResult(object):
    def __init__(self, success=False, alternative=None):
        if success and alternative:
            raise ValueError('ActionResult cannot have succeeded and provide an alternative Action!')

        self.success = success
        self.alternative = alternative


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
        # Do we really need to check state?

        # log.debug('Attempting move.')
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        # Check for wall
        if stage.is_blocked(dest_x, dest_y):
            # There is a wall blocking our path
            self.consumes_turn = False
            self.results.append({'msg': 'You cannot walk into the wall...'})
            return

        # Check for attacker
        target = stage.get_blocker_at_loc(dest_x, dest_y)

        if target:
            self.consumes_turn = False
            self.results.append({'alternate': AttackAction(entity, self.dx, self.dy)})
            return

        # log.debug('Moving.')
        entity.move(self.dx, self.dy)

        # Need to redraw FOV
        self.results.append({'fov_recompute': True})

        # Add walk into door
        # Add walk into water/lava/etc
        # Add walk over items


class AttackAction(Action):
    def __init__(self, entity, dx, dy):
        if abs(dx) > 1 or abs(dy) > 1:
            raise ValueError('AttackAction dx or dy cannot be < -1 or > 1.')

        super().__init__()
        self.entity = entity
        self.dx = dx
        self.dy = dy

    def perform(self, *args, **kwargs):
        stage = kwargs['stage']
        dest_x = self.entity.x + self.dx
        dest_y = self.entity.y + self.dy

        if stage.is_blocked(dest_x, dest_y):
            self.results.append({'msg': 'You cannot attack the wall!'})
            return

        target = stage.get_blocker_at_loc(dest_x, dest_y)

        if target:
            attack_results = self.entity.fighter.attack(target)
            self.results.extend(attack_results)
        else:
            self.results.append({'msg': 'There is nothing to attack at that position.'})



class WaitAction(Action):
    def perform(self, *args, **kwargs):
        return


class PickupAction(Action):
    def perform(self, *args, **kwargs):
        stage = kwargs['stage']
        entity = kwargs['entity']

        # todo: Move this functionality to stage....
        for e in stage.entities:
            item_pos_at_our_pos = e.x == entity.x and e.y == entity.y

            if e.has_comp('item') and item_pos_at_our_pos:
                self.results.extend(entity.inv.add_item(e))
                break

        else:
            self.results.append({'msg': 'There is nothing here to pick up.'})


class UseItemAction(Action):
    def __init__(self, inv_index):
        super().__init__()
        self.inv_index = inv_index

    def perform(self, *args, **kwargs):
        stage = kwargs['stage']
        fov_map = kwargs['fov_map']
        entity = kwargs['entity']
        prev_state = kwargs['prev_state']

        # Check this in the input handler??
        if prev_state == States.HERO_DEAD:
            return

        item = entity.inv.items[self.inv_index]

        self.results.extend(
            entity.inv.use(item, entities=stage.entities, fov_map=fov_map)
        )


class DropItemAction(Action):
    def __init__(self, inv_index):
        super().__init__()
        self.inv_index = inv_index

    def perform(self, *args, **kwargs):
        entity = kwargs['entity']
        prev_state = kwargs['prev_state']

        # Check this in the input handler??
        if prev_state == States.HERO_DEAD:
            return

        item = entity.inv.items[self.inv_index]

        self.results.extend(entity.inv.drop(item))


class StairUpAction(Action):
    def perform(self, *args, **kwargs):
        dungeon = kwargs['dungeon']
        entity = kwargs['entity']

        stage = dungeon.get_stage()

        for entity in stage.entities:
            if entity.has_comp('stair_up'):
                hero_at_stairs = entity.x == entity.x and entity.y == entity.y
                if hero_at_stairs:

                    if dungeon.current_stage == 0:
                        self.results.append({
                            'msg': 'You go up the stairs and leave the dungeon forever...',
                            'state': States.HERO_DEAD
                        })
                        break

                    elif dungeon.move_upstairs():
                        stage = dungeon.get_stage()
                        self.results.append({
                            'msg': 'You ascend the stairs up.',
                            'redraw': True
                        })
                        break
                    else:
                        raise ValueError("Something weird happened with going upstairs!")

        else:
            self.results.append({'msg': 'There are no stairs here.'})


class StairDownAction(Action):
    def perform(self, *args, **kwargs):
        dungeon = kwargs['dungeon']
        entity = kwargs['entity']
        stage = dungeon.get_stage()

        for entity in stage.entities:
            if entity.has_comp('stair_down'):
                hero_at_stairs = entity.x == entity.x and entity.y == entity.y

                if hero_at_stairs:
                    dungeon.mk_next_stage()

                    if dungeon.move_downstairs():
                        stage = dungeon.get_stage()
                        stage.populate()

                        self.results.append({
                            'msg': 'You carefully descend the stairs down.',
                            'redraw': True
                        })
                        break
                    else:
                        raise ValueError("Something weird happened with going downstairs!")

        else:
            self.results.append({'msg': 'There are no stairs here.'})


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
            self.results.append({'msg': 'Boosted max HP!'})

        elif self.stat == 'str':
            entity.fighter.base_power += 1
            self.results.append({'msg': 'Boosted strength!'})

        elif self.stat == 'def':
            entity.fighter.base_defense += 1
            self.results.append({'msg': 'Boosted defense!'})

        # Just go back to HERO_TURN by default.
        # self.results.append({'state': States.HERO_TURN})
        self.results.append({'state': prev_state})


class ExitAction(Action):
    def __init__(self, state):
        super().__init__(consumes_turn=False)
        self.state = state

    def perform(self, *args, **kwargs):
        prev_state = kwargs['prev_state']

        if self.state in (States.SHOW_INV, States.DROP_INV, States.SHOW_STATS):
            self.results.append({'state': prev_state})

        elif self.state == States.TARGETING:
            self.results.append({
                'state': prev_state,
                'cancel_target': True,
                'msg': 'Targeting cancelled.',
            })

        else:
            self.results.append({'state': States.MAIN_MENU})
            # save_game(config.savefile, dungeon, msg_log, state, turns)
            # return True


class FullScreenAction(Action):
    def __init__(self):
        super().__init__(consumes_turn=False)

    def perform(self, *args, **kwargs):
        # Toggle fullscreen on/off
        tcod.console_set_fullscreen(fullscreen=not tcod.console_is_fullscreen())


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
        entity = kwargs['entity']
        targeting_item = kwargs['targeting_item']
        stage = kwargs['stage']
        fov_map = kwargs['fov_map']

        if self.lclick:
            # note: Due to the message console - we have to offset the y.
            self.y -= config.msg_height

            # todo: Replace with UseItemAction?

            item_use_results = entity.inv.use(
                targeting_item,
                entities=stage.entities,
                fov_map=fov_map,
                target_x=self.x,
                target_y=self.y
            )
            self.results.extend(item_use_results)

        elif self.rclick:
            # todo: Replace with ExitAction?
            self.results.append({'cancel_target': True})


class ShowInvAction(Action):
    def __init__(self, prev_state):
        super().__init__(consumes_turn=False)
        self.prev_state = prev_state

    def perform(self, *args, **kwargs):
        self.results = [{'state': States.SHOW_INV}]


class DropInvAction(Action):
    def __init__(self, prev_state):
        super().__init__(consumes_turn=False)
        self.prev_state = prev_state

    def perform(self, *args, **kwargs):
        self.results = [{'state': States.DROP_INV}]


class CharScreenAction(Action):
    def __init__(self, prev_state):
        super().__init__(consumes_turn=False)
        self.prev_state = prev_state

    def perform(self, *args, **kwargs):
        self.results = [{'state': States.SHOW_STATS}]
