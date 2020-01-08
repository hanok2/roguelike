from random import randint
import tcod
import config
import item_factory
import monster_factory
import stairs
from entity import Entity
from random_utils import from_dungeon_lvl
from render_functions import RenderOrder
from rect import Rect
from tile import Tile


class Dungeon(object):
    def __init__(self, hero):
        self.hero = hero
        self.levels = []
        self.current_lvl = 0

        # Generate the first level on initialization
        self.generate_next_level()
        self.place_hero(self.current_lvl)
        self.current_map().populate()

    def current_map(self):
        return self.levels[self.current_lvl]

    def place_hero(self, level):
        x, y = self.levels[level].rooms[0].center()
        self.hero.x = x
        self.hero.y = y
        self.levels[level].entities.append(self.hero)

    def generate_next_level(self):
        # Generate next dungeon level
        # place up stair in the first room
        level_depth = len(self.levels) + 1
        new_map = Map(config.map_width, config.map_height, level_depth)
        new_map.make_map()
        self.levels.append(new_map)

    def move_downstairs(self):
        # Remove the hero from the current level
        if self.current_map().rm_hero(self.hero):
            self.current_lvl += 1

            # Place the hero on the next level
            self.place_hero(self.current_lvl)

            return True
        return False

    def move_upstairs(self):
        if self.current_map().rm_hero(self.hero):
            self.current_lvl -= 1

            # todo: Find where the up-stair is on the next level
            x, y = self.levels[self.current_lvl].rooms[-1].center()
            self.hero.x = x
            self.hero.y = y
            self.levels[self.current_lvl].entities.append(self.hero)
            return True
        return False

class Map(object):
    def __init__(self, width, height, dungeon_lvl=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.entities = []
        self.rooms = []
        self.dungeon_lvl = dungeon_lvl

    def rm_hero(self, hero):
        if hero in self.entities:
            self.entities.remove(hero)
            return True
        return False

    def find_down_stair(self):
        for e in self.entities:
            if e.name == 'Stairs':
                return e
        return None

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        return False

    def mk_room(self):
        # random width and height
        w = randint(config.room_min_len, config.room_max_len)
        h = randint(config.room_min_len, config.room_max_len)

        # Random position w/o going out of the map boundaries
        x = randint(0, self.width - w - 1)
        y = randint(0, self.height - h - 1)

        # Generate new Rect
        new_room = Rect(x, y, w, h)

        return new_room

    def dig_room(self, rect):
        # Go through the tiles in the rectangle and make them passable.
        for x in range(rect.x1 + 1, rect.x2):
            for y in range(rect.y1 + 1, rect.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def mk_tunnel_simple(self, new_x, new_y):
        old_x, old_y = self.get_last_room_center()

        # Flip a coin to decide vertical first or horizontal first
        if randint(0, 1) == 1:
            # First move horizontally, then vertically.
            self.dig_h_tunnel(old_x, new_x, old_y)
            self.dig_v_tunnel(old_y, new_y, new_x)
        else:
            self.dig_v_tunnel(old_y, new_y, old_x)
            self.dig_h_tunnel(old_x, new_x, new_y)

    def dig_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def dig_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def get_last_room_center(self):
        # Center coordinates of previous room
        return self.rooms[-1].center()

    def make_map(self):
        # Procedurally generate a dungeon map
        num_rooms = 0

        last_room_centerx = None
        last_room_centery = None

        for r in range(config.max_rooms):
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

                if num_rooms > 0:
                    # For all rooms after the first: Connect with a tunnel.
                    self.mk_tunnel_simple(new_x, new_y)
                else:
                    # Add the up-stair
                    self.place_stairs_up(new_x, new_y)

                self.rooms.append(new_room)
                num_rooms += 1

        # Add the Stairs
        self.place_stairs_down(last_room_centerx, last_room_centery)

    def populate(self):
        for room in self.rooms:
            self.place_entities(room)

    def place_entities(self, room):
        max_monsters_per_room = from_dungeon_lvl(
            config.max_monsters_weights, self.dungeon_lvl
        )
        max_items_per_room = from_dungeon_lvl(
            config.max_items_weights, self.dungeon_lvl
        )

        # Monster placement
        num_monsters = randint(0, max_monsters_per_room)
        monster_chances = monster_factory.monster_chances(self.dungeon_lvl)

        for i in range(num_monsters):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in self.entities if entity.x == x and entity.y == y]):
                monster = monster_factory.get_random_monster(x, y, monster_chances)
                self.entities.append(monster)

        # Item placement
        num_items = randint(0, max_items_per_room)
        item_chances = item_factory.item_chances(self.dungeon_lvl)

        for i in range(num_items):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in self.entities if entity.x == x and entity.y == y]):
                item = item_factory.get_rnd_item(x, y, item_chances)
                self.entities.append(item)

    def place_stairs_down(self, x, y):
        stairs_comp = stairs.Stairs(floor=self.dungeon_lvl + 1)

        self.entities.append(Entity(
            x, y,
            '>',
            tcod.white,
            'Stairs Down',
            render_order=RenderOrder.STAIRS,
            stair_down=stairs_comp
        ))

    def place_stairs_up(self, x, y):
        stairs_comp = stairs.Stairs(floor=self.dungeon_lvl - 1)

        self.entities.append(Entity(
            x, y,
            '<',
            tcod.white,
            'Stairs Up',
            render_order=RenderOrder.STAIRS,
            stair_up=stairs_comp
        ))
