import math
import tcod
from .config import RenderOrder
from .components import Item


class Entity(object):
    """ A generic object to represent players, enemies, items, etc.
        We use a dictionary to manage the entity's Components.
    """

    def __init__(self, **kwargs):
        self.components = kwargs

    def __getattr__(self, name):
        if name in self.components:
            return self.components[name]

        raise AttributeError('Entity has no component with attribute {}'.format(name))

    def __setattr__(self, key, value):
        if key == 'components':
            # self.components = value
            super().__setattr__('components', value)
        else:
            self.components[key] = value

    def __getstate__(self):
        """But if we try to pickle our d instance, we get RecursionError because
            of that __getattr__ which does the magic conversion of attribute
            access to key lookup. We can overcome that by providing the class
            with __getstate__ and __setstate__ methods.
            https://stackoverflow.com/questions/50156118/recursionerror-maximum-recursion-depth-exceeded-while-calling-a-python-object-w/50158865#50158865
        """
        return self.components

    def __setstate__(self, state):
        """See comment for __getstate__"""
        self.components = state

    def add_comp(self, **kwargs):
        for k, v in kwargs.items():
            self.components[k] = v

    def has_comp(self, component):
        if component in self.components:
            return True
        return False

    def rm_comp(self, component):
        if component in self.components:
            self.components.pop(component)
            return True
        return False

    def move(self, dx, dy):
        # Move the entity by a given amount
        dest_x = self.x + dx
        dest_y = self.y + dy

        if dest_x < 0 or dest_y < 0:
            raise ValueError('move cannot place entity in a negative x or y: ({}, {})'.format(dest_x, dest_y))
        self.x += dx
        self.y += dy

    def move_towards(self, target_x, target_y, game_map):
        """Very simple movement function to take the most direct path toward
            the hero.
        """
        if target_x < 0 or target_y < 0:
            raise ValueError('Target coordinates cannot be negative! ({}, {})'.format(target_x, target_y))

        dx, dy = self.calc_move(target_x, target_y)

        dest_x = self.x + dx
        dest_y = self.y + dy

        blocked_at = game_map.is_blocked(dest_x, dest_y)
        occupied = game_map.get_blocker_at_loc(dest_x, dest_y)

        if not (blocked_at or occupied):
            self.move(dx, dy)
