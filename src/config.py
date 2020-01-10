import tcod

VERSION = 1.1
window_title = 'Infinity Dronez'
game_title = 'Infinity Dronez Version {}'.format(VERSION)
author = 'hackemslashem'

savefile = 'savegame.dat'
tileset_file = 'images/arial10x10.png'
menu_img = 'images/menu_bg.png'

scr_width = 80
scr_height = 50

# Console panels
bar_width = 20
panel_height = 7
panel_y = scr_height - panel_height

msg_x = bar_width + 2
# msg_width = scr_width - bar_width - 2  # Same as scr_width
msg_height = 5

char_scr_width = 30
char_scr_height = 10

# Map info
DEFAULT_DUNGEON_LVL = 1
min_map_length = 3
map_width = 60
map_height = scr_height - panel_height - msg_height

# Room generation
room_max_len = 15
room_min_len = 3
NW_OFFSET = 1
SE_OFFSET = 2
max_rooms = 10
max_items_weights = [[1, 1], [2, 4]]

# Monster data
max_monsters_per_map = 20
max_monsters_weights = [[2, 1], [3, 4], [5, 6]]
troll_chances = [[15, 3], [30, 5], [60, 7]]

fov_algorithm = 0              # 0 is default alg tcod uses
fov_light_walls = True          # Light up walls we see
fov_radius = 10                # How far can we see?

colors = {
    # 'dark_wall': tcod.Color(0, 0, 100),
    # 'dark_ground': tcod.Color(50, 50, 150),
    'dark_wall': tcod.darker_gray,
    'dark_ground': tcod.darkest_gray,
    'light_wall': tcod.Color(130, 110, 50),
    'light_ground': tcod.Color(200, 180, 50)
}
