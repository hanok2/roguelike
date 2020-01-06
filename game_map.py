from random import randint
import tcod
from tile import Tile
from rect import Rect
from entity import Entity
from components import Fighter, ApproachingBehavior, Item, EquipmentSlots, Equippable
from render_functions import RenderOrder
from item_functions import heal, cast_confuse, cast_lightning, cast_fireball
from stairs import Stairs
from random_utils import rnd_choice_from_dict, from_dungeon_lvl


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
        # procedurally generate a dungeon map

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
            [[2, 1], [3, 4], [5, 6]], self.dungeon_lvl
        )
        max_items_per_room = from_dungeon_lvl(
            [[1, 1], [2, 4]], self.dungeon_lvl
        )

        # Get a random # of monsters
        num_monsters = randint(0, max_monsters_per_room)
        num_items = randint(0, max_items_per_room)

        monster_chances = {
            'orc': 80,
            # 'troll': 20,
            'troll': from_dungeon_lvl([[15, 3], [30, 5], [60, 7]], self.dungeon_lvl)
        }

        item_chances = {
            'healing_potion': 35,
            'lightning_scroll': from_dungeon_lvl([[25, 4]], self.dungeon_lvl),
            'fireball_scroll': from_dungeon_lvl([[25, 6]], self.dungeon_lvl),
            'confusion_scroll': from_dungeon_lvl([[10, 2]], self.dungeon_lvl),
            'sword': 35,
            'shield': 35,
            # 'sword': from_dungeon_lvl([[5, 4]], self.dungeon_lvl),
            # 'shield': from_dungeon_lvl([[15, 8]], self.dungeon_lvl),
        }

        for i in range(num_monsters):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):

                monster_choice = rnd_choice_from_dict(monster_chances)

                if monster_choice == 'orc':
                    # ORC
                    fighter_comp = Fighter(hp=20, defense=0, power=4, xp=35)
                    ai_comp = ApproachingBehavior()
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
                    fighter_comp = Fighter(hp=30, defense=2, power=8, xp=100)
                    ai_comp = ApproachingBehavior()
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

                item_choice = rnd_choice_from_dict(item_chances)

                if item_choice == 'healing_potion':
                    item_comp = Item(use_func=heal, amt=40)
                    item = Entity(
                        x, y,
                        '!',
                        tcod.violet,
                        "Healing potion",
                        render_order=RenderOrder.ITEM,
                        item=item_comp,
                    )

                elif item_choice == 'sword':
                    equippable_comp = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
                    item = Entity(
                        x, y,
                        '(',
                        tcod.sky,
                        'Sword',
                        equippable=equippable_comp
                    )
                elif item_choice == 'shield':
                    equippable_comp = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=2)
                    item = Entity(
                        x, y,
                        '[',
                        tcod.darker_orange,
                        'Shield',
                        equippable=equippable_comp
                    )

                elif item_choice == 'fireball_scroll':
                    item_comp = Item(
                        use_func=cast_fireball,
                        targeting=True,
                        targeting_msg='Left-click a target tile for the fireball, or right-click to cancel.',
                        dmg=25,
                        radius=3
                    )

                    item = Entity(
                        x, y,
                        '?',
                        tcod.yellow,
                        "Fireball Scroll",
                        render_order=RenderOrder.ITEM,
                        item=item_comp,
                    )

                elif item_choice == 'confusion_scroll':
                    item_comp = Item(
                        use_func=cast_confuse,
                        targeting=True,
                        targeting_msg='Left-click an enemy to confuse it, or right-click to cancel.',
                    )

                    item = Entity(
                        x, y,
                        '?',
                        tcod.yellow,
                        "Confuse Scroll",
                        render_order=RenderOrder.ITEM,
                        item=item_comp,
                    )

                else:
                    # Scroll of lightning bolt
                    item_comp = Item(use_func=cast_lightning, dmg=40, max_range=5)
                    item = Entity(
                        x, y,
                        '?',
                        tcod.yellow,
                        "Lightning Scroll",
                        render_order=RenderOrder.ITEM,
                        item=item_comp,
                    )
                entities.append(item)

    def next_floor(self, hero, msg_log, constants):
        self.dungeon_lvl += 1
        entities = [hero]

        self.tiles = self.initialize_tiles()

        self.make_map(
            constants['max_rooms'],
            constants['room_min_len'],
            constants['room_max_len'],
            constants['map_width'],
            constants['map_height'],
            hero,
            entities,
        )

        # Heal the hero
        hero.fighter.heal(hero.fighter.max_hp // 2)

        msg_log.add('You take a moment to rest, and recover your strength.')

        return entities
