from random import randint
import tcod
import monster_factory
import config
import item_factory
from entity import Entity
from random_utils import from_dungeon_lvl
from render_functions import RenderOrder
from rect import Rect
from stairs import Stairs
from tile import Tile


class GameMap(object):
    def __init__(self, width, height, dungeon_lvl=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

        self.dungeon_lvl = dungeon_lvl

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        return False

    def create_room(self, rect):
        # go through the tiles in the rectangle and make them passable.

        for x in range(rect.x1 + 1, rect.x2):
            for y in range(rect.y1 + 1, rect.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def make_map(self, max_rooms, room_min_len, room_max_len, map_width, map_height, hero, entities):
        # Procedurally generate a dungeon map
        rooms = []
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range(max_rooms):
            # random width and height
            w = randint(room_min_len, room_max_len)
            h = randint(room_min_len, room_max_len)

            # Random position w/o going out of the map boundaries
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height- h - 1)

            # Generate new Rect
            new_room = Rect(x, y, w, h)

            # Double check the other rooms to make sure there are no
            # intersections.
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break

            else:
                # There are no intersections, valid room.
                self.create_room(new_room)

                # Get center coordinates
                (new_x, new_y) = new_room.center()

                center_of_last_room_x = new_x
                center_of_last_room_y = new_y

                if num_rooms == 0:
                    # If this is the first room, place the hero there.
                    hero.x = new_x
                    hero.y = new_y

                else:
                    # For all rooms after the first:
                    # Connect it to the previous room with a tunnel.

                    # Center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    # Flip a coin
                    if randint(0, 1) == 1:
                        # First move horizontally, then vertically.
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)


                # Add entities/monsters
                self.place_entities(
                    new_room,
                    entities,
                )

                rooms.append(new_room)
                num_rooms += 1

        # Add the Stairs
        stairs_comp = Stairs(self.dungeon_lvl + 1)
        down_stairs = Entity(
            center_of_last_room_x,
            center_of_last_room_y,
            '>',
            tcod.white,
            'Stairs',
            render_order=RenderOrder.STAIRS,
            stairs=stairs_comp
        )
        entities.append(down_stairs)

    def place_entities(self, room, entities):
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

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                monster = monster_factory.get_random_monster(x, y, monster_chances)
                entities.append(monster)

        # Item placement
        num_items = randint(0, max_items_per_room)
        item_chances = item_factory.item_chances(self.dungeon_lvl)

        for i in range(num_items):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item = item_factory.get_rnd_item(x, y, item_chances)
                entities.append(item)

    def next_floor(self, hero, msg_log):
        self.dungeon_lvl += 1
        entities = [hero]

        self.tiles = self.initialize_tiles()

        self.make_map(
            config.max_rooms,
            config.room_min_len,
            config.room_max_len,
            config.map_width,
            config.map_height,
            hero,
            entities,
        )

        # Heal the hero
        hero.fighter.heal(hero.fighter.max_hp // 2)

        msg_log.add('You take a moment to rest, and recover your strength.')

        return entities
