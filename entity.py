import math

class Entity(object):
    """ A generic object to represent players, enemies, items, etc."""

    def __init__(self, x, y, char, color, name, blocks=False, fighter=None, ai=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter
        self.ai = ai

        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

    def move(self, dx, dy):
        # Move the entity by a given amount
        self.x += dx
        self.y += dy

    def move_towards(self, target_x, target_y, game_map, entities):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx ** 2 + dy ** 2)


        dx = int(round(dx / dist))
        dy = int(round(dy / dist))

        blocked_at = game_map.is_blocked(self.x + dx, self.y + dy)
        occupied = get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)

        if not (blocked_at or occupied):
            self.move(dx, dy)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

def get_blocking_entities_at_location(entities, dest_x, dest_y):
    for entity in entities:
        matching_coords = entity.x == dest_x and entity.y == dest_y

        if entity.blocks and matching_coords:
            return entity

    return None
