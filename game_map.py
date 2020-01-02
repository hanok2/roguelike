from random import randint
import tcod
from tile import Tile
from rect import Rect
from entity import Entity
from components import Fighter, BasicMonster, Item
from render_functions import RenderOrder
from item_functions import heal


class GameMap(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        # tiles = [[Tile(False) for y in range(self.height)] for x in range(self.width)]
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


    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room, max_items_per_room):
        # procedurally generate a dungeon map

        rooms = []
        num_rooms = 0

        for r in range(max_rooms):
            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)

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

                if num_rooms == 0:
                    # If this is the first room, place the player there.
                    player.x = new_x
                    player.y = new_y

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
                    max_monsters_per_room,
                    max_items_per_room
                )

                rooms.append(new_room)
                num_rooms += 1

    def place_entities(self, room, entities, max_monsters_per_room, max_items_per_room):
        # Get a random # of monsters
        num_monsters = randint(0, max_monsters_per_room)
        num_items = randint(0, max_items_per_room)


        for i in range(num_monsters):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):

                if randint(0, 100) < 80:
                    # ORC
                    fighter_comp = Fighter(hp=10, defense=0, power=3)
                    ai_comp = BasicMonster()
                    monster = Entity(
                        x, y,
                        'o',
                        tcod.desaturated_green,
                        'Orc',
                        blocks=True,
                        render_order=RenderOrder.ACTOR,
                        fighter=fighter_comp,
                        ai=ai_comp
                    )

                else:
                    # TROLL
                    fighter_comp = Fighter(hp=16, defense=1, power=4)
                    ai_comp = BasicMonster()
                    monster = Entity(
                        x, y,
                        'T',
                        tcod.darker_green,
                        'Troll',
                        blocks=True,
                        render_order=RenderOrder.ACTOR,
                        fighter=fighter_comp,
                        ai=ai_comp
                    )

                entities.append(monster)

        # Item placement
        for i in range(num_items):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):

                item_comp = Item(use_func=heal, amt=4)
                item = Entity(
                    x, y,
                    '!',
                    tcod.violet,
                    "Healing potion",
                    render_order=RenderOrder.ITEM,
                    item=item_comp,
                )

                entities.append(item)
