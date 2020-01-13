import tcod
from .states import States

# TCOD - EVENT CONSTANTS:
# https://github.com/libtcod/python-tcod/blob/master/tcod/event_constants.py


def handle_keys(key, state):
    print(key)

    if state == States.HERO_TURN:
        return handle_hero_turn_keys(key)

    elif state == States.HERO_DEAD:
        return handle_hero_dead_keys(key)

    elif state == States.TARGETING:
        return handle_targeting_keys(key)

    elif state in (States.SHOW_INV, States.DROP_INV):
        return handle_inv_keys(key)

    elif state == States.LEVEL_UP:
        return handle_lvl_up_menu(key)

    elif state == States.SHOW_STATS:
        return handle_char_scr(key)

    return {}
    # Raise exception instead?


def handle_hero_turn_keys(key):
    key_char = chr(key.c)

    # Stairs
    # key.shift is a boolean telling you whether Shift is down
    if key.shift and key_char == '.':
        return {'stair_down': True}
    elif key.shift and key_char == ',':
        return {'stair_up': True}

    # Actions
    if key_char == 'g' or key_char == ',':
        return {'pickup': True}
    elif key_char == 'i':
        return {'show_inv': True}
    elif key_char == 'd':
        return {'drop_inv': True}

    if key.lctrl and key_char == 'x':
    # elif key.vk == tcod.KEY_CONTROL: and
    # elif key_char == '\\':
        return {'show_char_scr': True}


    # Wait
    elif key_char == '.':
        return {'wait': True}
    elif key.vk == tcod.KEY_KP5:
        return {'wait': True}

    # Move Up
    if key_char == 'k':
        return {'move': (0, -1)}
    elif key.vk == tcod.KEY_UP:
        return {'move': (0, -1)}
    elif key.vk == tcod.KEY_KP8:
        return {'move': (0, -1)}

    # Move Down
    elif key_char == 'j':
        return {'move': (0, 1)}
    elif key.vk == tcod.KEY_DOWN:
        return {'move': (0, 1)}
    elif key.vk == tcod.KEY_KP2:
        return {'move': (0, 1)}

    # Move Left
    elif key_char == 'h':
        return {'move': (-1, 0)}
    elif key.vk == tcod.KEY_LEFT:
        return {'move': (-1, 0)}
    elif key.vk == tcod.KEY_KP4:
        return {'move': (-1, 0)}

    # Move Right
    elif key_char == 'l':
        return {'move': (1, 0)}
    elif key.vk == tcod.KEY_RIGHT:
        return {'move': (1, 0)}
    elif key.vk == tcod.KEY_KP6:
        return {'move': (1, 0)}

    # Move NW
    elif key_char == 'y':
        return {'move': (-1, -1)}
    elif key.vk == tcod.KEY_KP7:
        return {'move': (-1, -1)}

    # Move NE
    elif key_char == 'u':
        return {'move': (1, -1)}
    elif key.vk == tcod.KEY_KP9:
        return {'move': (1, -1)}

    # Move SW
    elif key_char == 'b':
        return {'move': (-1, 1)}
    elif key.vk == tcod.KEY_KP1:
        return {'move': (-1, 1)}

    # Move SE
    elif key_char == 'n':
        return {'move': (1, 1)}
    elif key.vk == tcod.KEY_KP3:
        return {'move': (1, 1)}

    # Note: Add support for number pad movement


    if key.vk == tcod.KEY_ENTER and key.lalt:
        # Alt+Enter: Toggle full screen
        return {'full_scr': True}

    elif key.vk == tcod.KEY_ESCAPE:
        # Exit
        return {'exit': True}

    # No key was pressed
    return {}


def handle_hero_dead_keys(key):
    key_char = chr(key.c)

    # if key_char == 'i':
        # return {'show_inv': True}

    if key.vk == tcod.KEY_ENTER and key.lalt:
        # Alt+Enter: Toggle full screen
        return {'full_scr': True}

    elif key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}

    return {}


def handle_inv_keys(key):
    # Convert the key pressed to an index. a is 0, b is 1, etc.
    index = key.c - ord('a')

    if index >= 0:
        return {'inv_index': index}

    if key.vk == tcod.KEY_ENTER and key.lalt:
        # Alt+Enter: Toggle full screen
        return {'full_scr': True}

    elif key.vk == tcod.KEY_ESCAPE:
        # Exit the menu
        return {'exit': True}

    return {}


def handle_main_menu(key):
    key_char = chr(key.c)

    if key_char == 'n':
        return {'new_game': True}
    elif key_char == 'c':  # For "Continue"
        return {'load_game': True}
    elif key_char == 'o':
        return {'options': True}
    elif key_char == 'q':
        return {'exit': True}

    return {}


def handle_targeting_keys(key):
    if key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}

    return {}


def handle_mouse(mouse):
    (x, y) = (mouse.cx, mouse.cy)

    if mouse.lbutton_pressed:
        return {'l_click': (x, y)}
    elif mouse.rbutton_pressed:
        return {'r_click': (x, y)}

    return {}


def handle_lvl_up_menu(key):
    if key:
        key_char = chr(key.c)

        if key_char == 'c':                 # Constitution
            return {'lvl_up': 'hp'}
        elif key_char == 's':               # Strength
            return {'lvl_up': 'str'}
        elif key_char == 'd':               # Defense
            return {'lvl_up': 'def'}

    return {}


def handle_char_scr(key):
    if key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}
    return {}


def process_tcod_input(key):
    if key.vk == tcod.KEY_ESCAPE:
        return 'esc'

    key_char = chr(key.c)

    if key.lctrl:
        return '^' + key_char

    if key.shift:
        if key_char == '.':
            return '>'
        elif key_char == ',':
            return '<'

    # Arrow keys
    if key.vk == tcod.KEY_LEFT:
        return 'h'
    elif key.vk == tcod.KEY_RIGHT:
        return 'l'
    elif key.vk == tcod.KEY_UP:
        return 'k'
    elif key.vk == tcod.KEY_DOWN:
        return 'j'

    # NumPad Keys
    if key.vk == tcod.KEY_KP1:
        return 'b'
    elif key.vk == tcod.KEY_KP2:
        return 'j'
    elif key.vk == tcod.KEY_KP3:
        return 'n'
    elif key.vk == tcod.KEY_KP4:
        return 'h'
    elif key.vk == tcod.KEY_KP5:
        return '.'
    elif key.vk == tcod.KEY_KP6:
        return 'l'
    elif key.vk == tcod.KEY_KP7:
        return 'y'
    elif key.vk == tcod.KEY_KP8:
        return 'k'
    elif key.vk == tcod.KEY_KP9:
        return 'u'


    return key_char
