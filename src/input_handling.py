import tcod
from .states import States

# TCOD - EVENT CONSTANTS:
# https://github.com/libtcod/python-tcod/blob/master/tcod/event_constants.py

""" Shorthand:
    # = Windows Key
    ! = Alt
    ^ = Control
    + = Shift
"""


def handle_keys(key, state):
    # Put this here for now... move later when doing other ports
    # key = process_tcod_input(key)

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
    # Stairs
    if key == '>':
        return {'stair_down': True}
    elif key == '<':
        return {'stair_up': True}

    # Actions
    if key == ',':
        return {'pickup': True}
    elif key == 'i':
        return {'show_inv': True}
    elif key == 'd':
        return {'drop_inv': True}

    if key == '^x':
        return {'show_char_scr': True}

    elif key == '.':
        return {'wait': True}

    # Movement
    if key == 'k':
        return {'move': (0, -1)}  # Move Up
    elif key == 'j':
        return {'move': (0, 1)}  # Move Down
    elif key == 'h':
        return {'move': (-1, 0)}  # Move Left
    elif key == 'l':
        return {'move': (1, 0)}  # Move Right
    elif key == 'y':
        return {'move': (-1, -1)}  # Move NW
    elif key == 'u':
        return {'move': (1, -1)}  # Move NE
    elif key == 'b':
        return {'move': (-1, 1)}  # Move SW
    elif key == 'n':
        return {'move': (1, 1)}  # Move SE

    if key == '!a':
        return {'full_scr': True}
    elif key == 'esc':
        return {'exit': True}

    # No key was pressed
    return {}


def handle_hero_dead_keys(key):
    if key == 'i':
        return {'show_inv': True}
    elif key == 'alt-enter':
        return {'full_scr': True}  # Alt+Enter: Toggle full screen
    elif key == '^x':
        return {'show_char_scr': True}
    elif key == 'esc':
        return {'exit': True}

    return {}


def handle_inv_keys(key):
    # Convert the key pressed to an index. a is 0, b is 1, etc.
    if len(key) == 1:
        index = ord(key) - ord('a')

        if index >= 0:
            return {'inv_index': index}

    elif key == 'alt-enter':
        return {'full_scr': True}  # Alt+Enter: Toggle full screen
    elif key == 'esc':
        return {'exit': True}

    return {}


def handle_main_menu(key):
    if key == 'n':
        return {'new_game': True}
    elif key == 'c':  # For "Continue"
        return {'load_game': True}
    elif key == 'o':
        return {'options': True}
    elif key == 'q':
        return {'exit': True}

    return {}


def handle_targeting_keys(key):
    # todo: Add ability to move a cursor to target.

    if key == 'esc':
        return {'exit': True}

    return {}


def handle_lvl_up_menu(key):
    if key == 'c':                 # Constitution
        return {'lvl_up': 'hp'}
    elif key == 's':               # Strength
        return {'lvl_up': 'str'}
    elif key == 'd':               # Defense
        return {'lvl_up': 'def'}

    return {}


def handle_char_scr(key):
    if key == 'esc':
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


def handle_mouse(mouse):
    """ Takes in the mouse object from tcod and returns appropriate info.

        x,y: Absolute position of the mouse cursor in pixels relative to the window
            top-left corner.
        dx, dy: Movement of the mouse cursor since the last call in pixels.
        cx,	cy: Coordinates of the console cell under the mouse cursor
            (pixel coordinates divided by the font size).
        lbutton_pressed: true if the left button was pressed and released.
        rbutton_pressed: true if the right button was pressed and released.
        mbutton_pressed: true if the middle button was pressed and released.
    """
    (x, y) = (mouse.cx, mouse.cy)

    if mouse.lbutton_pressed:
        return {'l_click': (x, y)}
    elif mouse.rbutton_pressed:
        return {'r_click': (x, y)}
    elif mouse.mbutton_pressed:
        return {'m_click': (x, y)}

    return {}
