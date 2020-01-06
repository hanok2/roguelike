import tcod

VERSION = 1.1
window_title = 'Infinity Dronez'
game_title = 'Infinity Dronez Version {}'.format(VERSION)
author = 'hackemslashem'

scr_width = 80
scr_height = 50

# Console panels
bar_width = 20
panel_height = 7
panel_y = scr_height - panel_height

msg_x = bar_width + 2
msg_width = scr_width - bar_width - 2
msg_height = panel_height - 1

# Map info
map_width = 80
map_height = 43

# Room generation
room_max_len = 10
room_min_len = 4
max_rooms = 30
max_monsters_per_room = 3
max_items_per_room = 3

fov_algorithm = 0              # 0 is default alg tcod uses
fov_light_walls = True          # Light up walls we see
fov_radius = 10                # How far can we see?

colors = {
    'dark_wall': tcod.Color(0, 0, 100),
    'dark_ground': tcod.Color(50, 50, 150),
    'light_wall': tcod.Color(130, 110, 50),
    'light_ground': tcod.Color(200, 180, 50)
}
