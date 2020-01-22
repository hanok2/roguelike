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

    def calc_move(self, target_x, target_y):
        """Calculates how to get to a target coordinate from the entity's
            coordinates. Returns a (dx, dy) tuple representing the change in
            x and y required to get there.
        """
        dist = self.distance(target_x, target_y)
        if dist == 0:
            return 0, 0

        dx = int(round((target_x - self.x) / dist))
        dy = int(round((target_y - self.y) / dist))
        return dx, dy

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

    def move_astar(self, target, game_map):
        # Create a FOV map that has the dimensions of the map
        fov = tcod.map_new(game_map.width, game_map.height)

        # Scan the current map each turn and set all the walls as unwalkable
        for y1 in range(game_map.height):
            for x1 in range(game_map.width):
                tcod.map_set_properties(
                    fov,
                    x1,
                    y1,
                    not game_map.tiles[x1][y1].block_sight,
                    not game_map.tiles[x1][y1].blocked
                )

        # Scan all the objects to see if there are objects that must be navigated around
        # Check also that the object isn't self or the target (so that the start and the end points are free)
        # The AI class handles the situation if self is next to the target so it will not use this A* function anyway

        for entity in game_map.entities:
            if entity.blocks and entity != self and entity != target:
                # Set the tile as a wall so it must be navigated around
                tcod.map_set_properties(fov, entity.x, entity.y, True, False)

        # Allocate a A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited

        my_path = tcod.path_new_using_map(fov, 1.41)

        # Compute the path between self's coordinates and the target's coordinates
        tcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
        # It makes sense to keep path size relatively low to keep the monsters from running around the map if there's an alternative path really far away

        if not tcod.path_is_empty(my_path) and tcod.path_size(my_path) < 25:
            # Find the next coordinates in the computed full path
            x, y = tcod.path_walk(my_path, True)
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            # Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
            # it will still try to move towards the player (closer to the corridor opening)
            self.move_towards(target.x, target.y, game_map)

            # Delete the path to free memory
        tcod.path_delete(my_path)

    def distance(self, x, y):
        """ Returns the distance between the entity and an arbitrary point."""
        dx = x - self.x
        dy = y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance_to(self, entity):
        """A wrapper for self.distance - Returns the distance from this entity
            to the passed entity.
        """
        return self.distance(entity.x, entity.y)
