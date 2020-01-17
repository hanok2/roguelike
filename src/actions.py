import tcod
from abc import ABC, abstractmethod
from .config import States
from . import render_functions


class Action(ABC):
    # todo: Implement a performed boolean - we can't perform an Action more
    # than one time.

    def __init__(self, consumes_turn=True):
        self.consumes_turn = consumes_turn
        self.results = []

    @abstractmethod
    def perform(self):
        # We can return alternate Actions
        # We can return True or False to indicate success
        # Do the parameters need to be (*args, **kwargs)?
        pass


class WalkAction(Action):
    def __init__(self, dx, dy):
        super().__init__(consumes_turn=True)
        if abs(dx) > 1 or abs(dy) > 1:
            raise ValueError('WalkAction dx or dy cannot be < -1 or > 1.')
        self.dx = dx
        self.dy = dy

        # redraw_fov_on_success?

    def perform(self, stage, entity):
        # Do we really need to check state?

        # log.debug('Attempting move.')
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        # Check for wall
        if stage.is_blocked(dest_x, dest_y):
            # There is a wall blocking our path
            self.results.append({'msg': 'You walk into the wall...'})

        # Check for attacker
        target = stage.get_blocker_at_loc(dest_x, dest_y)
        if target:
            self.results.append({'alternate': 'AttackAction'})

        # log.debug('Moving.')
        entity.move(self.dx, self.dy)

        # Need to redraw FOV
        fov_recompute = True

        # Add walk into door
        # Add walk into water/lava/etc
        # Add walk over items


class WaitAction(Action):
    def perform(self):
        return True


class PickupAction(Action):
    def perform(self, stage, hero):

        # todo: Move this functionality to stage....
        for entity in stage.entities:
            item_pos_at_our_pos = entity.x == hero.x and entity.y == hero.y

            if entity.has_comp('item') and item_pos_at_our_pos:
                self.results.extend(hero.inv.add_item(entity))
                break

        else:
            self.results.append({'msg': 'There is nothing here to pick up.'})


class UseItemAction(Action):
    def perform(self, stage, fov_map, inv_index, hero, prev_state):
        # Check this in the input handler??
        if prev_state == States.HERO_DEAD:
            return

        item = hero.inv.items[inv_index]

        self.results.extend(
            hero.inv.use(item, entities=stage.entities, fov_map=fov_map)
        )


class DropItemAction(Action):
    def perform(self, stage, hero, inv_index, prev_state):
        # Check this in the input handler??
        if prev_state == States.HERO_DEAD:
            return

        item = hero.inv.items[inv_index]

        self.results.extend(hero.inv.drop(item))


class StairUpAction(Action):
    def perform(self, dungeon, hero):
        stage = dungeon.get_stage()

        for entity in stage.entities:
            if entity.has_comp('stair_up'):
                hero_at_stairs = entity.x == hero.x and entity.y == hero.y
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
                            'recompute_fov': True,
                            'reset_rendering': True
                        })
                        break
                    else:
                        raise ValueError("Something weird happened with going upstairs!")

        else:
            self.results.append({'msg': 'There are no stairs here.'})


class StairDownAction(Action):
    def perform(self, dungeon, hero):
        stage = dungeon.get_stage()

        for entity in stage.entities:
            if entity.has_comp('stair_down'):
                hero_at_stairs = entity.x == hero.x and entity.y == hero.y

                if hero_at_stairs:
                    dungeon.mk_next_stage()

                    if dungeon.move_downstairs():
                        stage = dungeon.get_stage()
                        stage.populate()

                        self.results.append({
                            'msg': 'You carefully descend the stairs down.',
                            'recompute_fov': True,
                            'reset_rendering': True
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

    def perform(self, entity):
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

        # state = prev_state
        self.results.append({'state': 'previous state'})




class ExitAction(Action):
    def __init__(self, prev_state):
        super().__init__(consumes_turn=False)
        self.prev_state = prev_state

    def perform(self, state):
        if state in (States.SHOW_INV, States.DROP_INV, States.SHOW_STATS):
            self.results.append({'state': self.prev_state})

        elif state == States.TARGETING:
            self.results.append({
                'state': self.prev_state,
                'cancel_target': True,
                'msg': 'Targeting cancelled.',
            })

        else:
            self.results.append({'state': States.MAIN_MENU})
            # save_game(config.savefile, dungeon, msg_log, state, turns)
            # return True


class FullScreenAction(Action):
    def __init__(self, ):
        super().__init__(consumes_turn=False)

    def perform(self):
        # Toggle fullscreen on/off
        tcod.console_set_fullscreen(fullscreen=not tcod.console_is_fullscreen())


class LClickAction(Action):
    def __init__(self, ):
        super().__init__(consumes_turn=False)

    def perform(self):
        pass


class RClickAction(Action):
    def __init__(self, ):
        super().__init__(consumes_turn=False)

    def perform(self):
        pass


class ShowInvAction(Action):
    def __init__(self, ):
        super().__init__(consumes_turn=False)

    def perform(self):
        pass


class DropInvAction(Action):
    def __init__(self, ):
        super().__init__(consumes_turn=False)

    def perform(self):
        pass


class ShowCharScreenAction(Action):
    def __init__(self, ):
        super().__init__(consumes_turn=False)

    def perform(self):
        pass
