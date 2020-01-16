from abc import ABC, abstractmethod
from .config import States


class Action(ABC):
    @abstractmethod
    def perform(self):
        # We can return alternate Actions
        # We can return True or False to indicate success
        pass


class WalkAction(Action):
    def __init__(self, dx, dy):
        if abs(dx) > 1 or abs(dy) > 1:
            raise ValueError('WalkAction dx or dy cannot be < -1 or > 1.')
        self.dx = dx
        self.dy = dy
        self.consumes_turn = True

        # redraw_fov_on_success?

    def perform(self, stage, entity):
        # Do we really need to check state?

        # log.debug('Attempting move.')
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        # Check for wall
        if stage.is_blocked(dest_x, dest_y):
            # There is a wall blocking our path
            return False

        # Check for attacker
        target = stage.get_blocker_at_loc(dest_x, dest_y)
        if target:
            return 'attack!'

        # log.debug('Moving.')
        entity.move(self.dx, self.dy)

        # Need to redraw FOV
        fov_recompute = True
        return True

        # Add walk into door
        # Add walk into water/lava/etc
        # Add walk over items


class WaitAction(Action):
    def __init__(self):
        self.consumes_turn = True

    def perform(self):
        return True

# PickupAction
# ShowInvAction
# DropInvAction
# InvIndexAction  ?
# StairUpAction
# StairDownAction
# LevelUpAction
# ShowCharScreenAction
# ExitAction
# FullScreenAction
# LClickAction
# RClickAction

