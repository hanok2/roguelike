import math
import random
from . import config
from . import factory
from . import stairs
from .rect import Rect
from .tile import Tile


class Stage(object):
    def __init__(self, width, height, dungeon_lvl=config.DEFAULT_DUNGEON_LVL):
        # Error checking
        if width < config.stage_length_min or height < config.stage_length_min:
            raise ValueError("The minimum map width/height is {}".format(config.stage_length_min))
        elif dungeon_lvl <= 0:
            raise ValueError("The minimum map dungeon_lvl is 1")

        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.entities = []
        self.rooms = []
        self.dungeon_lvl = dungeon_lvl

    def rm_hero(self):
        for e in self.entities:
            if e.has_comp('human'):
                self.entities.remove(e)
                return True
        return False

    def find_stair(self, stair_char):
        for e in self.entities:
            if e.char == stair_char:
                return e
        return None

    def initialize_tiles(self):
        return [[Tile(True) for y in range(self.height)] for x in range(self.width)]

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        return False

    def mk_room(self):
        # random width and height
        w = random.randint(config.room_min_len, config.room_max_len)
        h = random.randint(config.room_min_len, config.room_max_len)

        # Random position w/o going out of the map boundaries
        x = random.randint(0, self.width - w - 1)
        y = random.randint(0, self.height - h - 1)

        # Generate new Rect
        return Rect(x, y, w, h)

    def dig_room(self, rect):
        WALL_OFFSET = 1
        # Go through the tiles in the rectangle and make them passable.
        for x in range(rect.x1 + WALL_OFFSET, rect.x2 - WALL_OFFSET):

            for y in range(rect.y1 + WALL_OFFSET, rect.y2 - WALL_OFFSET):

                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def mk_tunnel_simple(self, room1, room2, horz_first=True):
        x1, y1 = room1.center()
        x2, y2 = room2.center()

        if horz_first:
            # First move horizontally, then vertically.
            self.dig_h_tunnel(x1, x2, y1)
            self.dig_v_tunnel(y1, y2, x2)
        else:
            # First move vertically, then horizontally
            self.dig_v_tunnel(y1, y2, x1)
            self.dig_h_tunnel(x1, x2, y2)

    def dig_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def dig_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def mk_stage(self):
        # Procedurally generate a dungeon map
        for _ in range(config.max_rooms):
            new_room = self.mk_room()

            # Double check the other rooms to make sure there are no intersections.
            for other_room in self.rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # There are no intersections, valid room.
                self.dig_room(new_room)

                # Get center coordinates
                (new_x, new_y) = new_room.center()

                last_room_centerx = new_x
                last_room_centery = new_y

                if self.rooms:
                    # For all rooms after the first: Connect with a tunnel.
                    last_room = self.rooms[-1]

                    # Flip a coin to decide vertical first or horizontal first
                    horz_first = bool(random.randint(0, 1))
                    self.mk_tunnel_simple(last_room, new_room, horz_first)
                else:
                    # Place stairs up in the first room
                    self.place_stairs_up(new_x, new_y)

                self.rooms.append(new_room)

        # Add the Stairs
        self.place_stairs_down(last_room_centerx, last_room_centery)

    def populate(self):
        """Populates the stage with monsters and items.
            Possibly adds other entities: stairs/features/etc.
        """
        self.place_monsters()
        for room in self.rooms:
            self.place_items(room)

    def is_occupied(self, x, y):
        """Returns True if an entity is occupying the tile."""
        return any([entity for entity in self.entities if entity.x == x and entity.y == y])

    def get_random_open_spot(self):
        """Find a random non-wall, non-blocked spot on the stage.
            If we find a valid tile, return the (x, y) tuple for that tile.
            Else, return None
        """
        while True:
            tile = self.get_random_non_wall_loc()
            if not tile:
                return None
            elif not self.is_occupied(*tile):
                return tile

    def get_random_non_wall_loc(self):
        """Find a random spot on the stage that is not a Wall."""
        # Find all of the non-wall tiles
        valid_tiles = []
        for x in range(self.width):
            for y in range(self.height):
                if not self.tiles[x][y].blocked:
                    valid_tiles.append((x, y))

        # Return a random valid tile
        if valid_tiles:
            return random.choice(valid_tiles)
        return None

    def get_random_room_loc(self, room):
        """Find a random spot in a room."""
        x = random.randint(room.x1 + config.NW_OFFSET, room.x2 - config.SE_OFFSET)
        y = random.randint(room.y1 + config.NW_OFFSET, room.y2 - config.SE_OFFSET)
        return x, y

    def place_monsters(self):
        """Generates monsters for the stage. For each monster, we pick a random
            non-wall and non-occupied spot on the stage and places a random monster there.
        """
        # todo: Create a table for monster generation that increases difficulty
        # max_monsters_per_map = from_dungeon_lvl(config.max_monsters_weights, self.dungeon_lvl)

        # Make sure there are value tiles
        if not self.get_random_non_wall_loc():
            return None

        for _ in range(config.max_monsters_per_stage):
            x, y = self.get_random_non_wall_loc()

            if not self.is_occupied(x, y):
                monster = factory.rnd_monster(x, y)
                self.entities.append(monster)

    def place_items(self, room):
        """Places a random set of items in a room. Items can be placed on top of
            other items to create a pile or even where other monsters are.
        """
        # max_items_per_room = from_dungeon_lvl(config.max_items_weights, self.dungeon_lvl)
        max_items_per_room = 5

        num_items = random.randint(0, max_items_per_room)

        for _ in range(num_items):
            x, y = self.get_random_room_loc(room)

            if not self.is_occupied(x, y):
                item = factory.rnd_item(x, y)
                self.entities.append(item)

    def place_stairs_down(self, x, y):
        if self.tiles[x][y].blocked:
            raise ValueError('Stairs cannot go on Wall tile!')

        stair_down = stairs.StairDown(x, y, floor=self.dungeon_lvl + 1)
        self.entities.append(stair_down)
        return stair_down

    def place_stairs_up(self, x, y):
        if self.tiles[x][y].blocked:
            raise ValueError('Stairs cannot go on Wall tile!')

        stair_up = stairs.StairUp(x, y, floor=self.dungeon_lvl - 1)
        self.entities.append(stair_up)
        return stair_up

    def get_blocker_at_loc(self, x, y):
        """Scans through all entities on stage that match the x, y coordinates and
            if an entity matches and blocks - we return it.
            Otherwise, returns None.
        """
        blockers = [e for e in self.entities if e.x == x and e.y == y]
        blockers = [e for e in blockers if e.has_comp('blocks')]

        if blockers:
            return blockers.pop()
        return None

    @classmethod
    def calc_dxdy(cls, src_x, src_y, dest_x, dest_y):
        dx = dest_x - src_x
        dy = dest_y - src_y
        return dx, dy

    @classmethod
    def calc_move(self, x1, y1, x2, y2):
        """Calculates how to get to a target coordinate from the entity's
            coordinates. Returns a (dx, dy) tuple representing the change in
            x and y required to get there.
        """
        dist = self.distance(x1, y1, x2, y2)

        if dist == 0:
            return 0, 0

        dx = int(round((x2 - x1) / dist))
        dy = int(round((y2 - y1) / dist))
        return dx, dy

    @classmethod
    def distance(self, x1, y1, x2, y2):
        """ Returns the distance between the entity and an arbitrary point."""
        dx = x1 - x2
        dy = y1 - y2
        return math.sqrt(dx ** 2 + dy ** 2)

    @classmethod
    def distance_between_entities(self, e1, e2):
        """ Returns the distance between the entity and an arbitrary point."""
        return self.distance(e1.x, e1.y, e2.x, e2.y)
