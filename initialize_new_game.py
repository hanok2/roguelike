import tcod
from entity import Entity
from render_functions import RenderOrder
from game_map import GameMap
from game_states import GameStates
from components import Fighter, Level, Equipment, Equippable
from equipment_slots import EquipmentSlots
from inventory import Inventory
from game_messages import Messagelog

screen_width = 80
screen_height = 50
bar_width = 20
panel_height = 7
panel_y = screen_height - panel_height

msg_x = bar_width + 2
msg_width = screen_width - bar_width - 2
msg_height = panel_height - 1

colors = {
    'dark_wall': tcod.Color(0, 0, 100),
    'dark_ground': tcod.Color(50, 50, 150),
    'light_wall': tcod.Color(130, 110, 50),
    'light_ground': tcod.Color(200, 180, 50)
}

constants = {
    'window_title': 'Roguelike Tutorial Revised',
    'screen_width': screen_width,
    'screen_height': screen_height,
    'map_width': 80,
    'map_height': 43,
    'room_max_size': 10,
    'room_min_size': 4,
    'max_rooms': 30,

    'bar_width': bar_width,
    'panel_height': panel_height,
    'panel_y': panel_y,
    'msg_x': msg_x,
    'msg_width': msg_width,
    'msg_height': msg_height,
    'fov_algorithm': 0,             # 0 is default alg tcod uses
    'fov_light_walls': True,        # Light up walls we see
    'fov_radius': 10,               # How far can we see?
    'max_monsters_per_room': 3,
    'max_items_per_room': 3,
    'colors': colors,
}

# Player components
fighter_comp = Fighter(hp=100, defense=1, power=2)
inv_comp = Inventory(26)
level_comp = Level()
equipment_comp = Equipment()

# Create entities
player = Entity(
    0, 0,
    '@',
    tcod.white,
    'Player',
    blocks=True,
    render_order=RenderOrder.ACTOR,
    fighter=fighter_comp,
    inv=inv_comp,
    level=level_comp,
    equipment=equipment_comp,
)

entities = [player]

equippable_comp = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
dagger = Entity(
    0, 0,
    '(',
    tcod.sky,
    'Dagger',
    equippable=equippable_comp
)
player.inv.add_item(dagger)
player.equipment.toggle_equip(dagger)

# Initialize the game map
game_map = GameMap(
    constants['map_width'],
    constants['map_height']
)

game_map.make_map(
    constants['max_rooms'],
    constants['room_min_size'],
    constants['room_max_size'],
    constants['map_width'],
    constants['map_height'],
    player,
    entities,
)

msg_log = Messagelog(
    constants['msg_x'],
    constants['msg_width'],
    constants['msg_height']
)

game_state = GameStates.PLAYERS_TURN

def get_game_data():
    return player, entities, game_map, msg_log, game_state
