import tcod
from states import States

# TCOD - EVENT CONSTANTS:
# https://github.com/libtcod/python-tcod/blob/master/tcod/event_constants.py


def handle_keys(key, state):
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


def handle_hero_turn_keys(key):
    key_char = chr(key.c)

    # Actions
    if key_char == 'g' or key_char == ',':
        return {'pickup': True}
    elif key_char == 'i':
        return {'show_inv': True}
    elif key_char == 'd':
        return {'drop_inv': True}

    # Trouble shoot > input later
    # key.shift is a boolean telling you whether Shift is down
    # elif key.shift and key_char == '.':

    elif key.vk == tcod.KEY_ENTER:
        return {'take_stairs': True}

    elif key_char == '\\':
        return {'show_char_scr': True}

    if key_char == '.':
        return {'wait': True}

    # Movement
    # Note: Add support for number pad movement
    if key.vk == tcod.KEY_UP or key_char == 'k':
        return {'move': (0, -1)}
    elif key.vk == tcod.KEY_DOWN or key_char == 'j':
        return {'move': (0, 1)}
    elif key.vk == tcod.KEY_LEFT or key_char == 'h':
        return {'move': (-1, 0)}
    elif key.vk == tcod.KEY_RIGHT or key_char == 'l':
        return {'move': (1, 0)}
    elif key_char == 'y':
        return {'move': (-1, -1)}
    elif key_char == 'u':
        return {'move': (1, -1)}
    elif key_char == 'b':
        return {'move': (-1, 1)}
    elif key_char == 'n':
        return {'move': (1, 1)}

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
