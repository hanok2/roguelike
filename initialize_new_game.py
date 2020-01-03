import tcod

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

CONSTANTS = {
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
