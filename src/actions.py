from abc import ABC, abstractmethod
from .config import States


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
        if prev_state == States.HERO_DEAD:
            return

        item = hero.inv.items[inv_index]

        self.results.extend(
            hero.inv.use(item, entities=stage.entities, fov_map=fov_map)
        )


class DropItemAction(Action):
    def perform(self):
        pass

# InvIndexAction  ?
    # Item usage
    # if inv_index is not None and prev_state != States.HERO_DEAD and inv_index < len(hero.inv.items):
        # log.debug('Inventory menu.')
        # item = hero.inv.items[inv_index]

        # if state == States.SHOW_INV:
            # hero_turn_results.extend(
                # hero.inv.use(
                    # item, entities=stage.entities, fov_map=fov_map
                # )
            # )

        # elif state == States.DROP_INV:
            # hero_turn_results.extend(hero.inv.drop(item))


class StairUpAction(Action):
    def perform(self):
        pass


class StairDownAction(Action):
    def perform(self):
        pass

class LevelUpAction(Action):
    def __init__(self, ):
        super().__init__(consumes_turn=False)

    def perform(self):
        pass


class ExitAction(Action):
    def __init__(self, ):
        super().__init__(consumes_turn=False)

    def perform(self):
        pass


class FullScreenAction(Action):
    def __init__(self, ):
        super().__init__(consumes_turn=False)

    def perform(self):
        pass


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
