import tcod
from .config import States
from . import actions

# TCOD - EVENT CONSTANTS:
# https://github.com/libtcod/python-tcod/blob/master/tcod/event_constants.py

""" Shorthand:
    # = Windows Key
    ! = Alt
    ^ = Control
    + = Shift
"""


def handle_keys(state, key):
    # Put this here for now... move later when doing other ports
    # key = process_tcod_input(key)

    if state == States.ACTOR_TURN:
        return handle_hero_turn_keys(state, key)

    elif state == States.HERO_DEAD:
        return handle_hero_dead_keys(state, key)

    elif state == States.TARGETING:
        return handle_targeting_keys(state, key)

    elif state in (States.SHOW_INV, States.DROP_INV):
        return handle_inv_keys(state, key)

    elif state == States.LEVEL_UP:
        return handle_lvl_up_menu(state, key)

    elif state == States.SHOW_STATS:
        return handle_char_scr(state, key)

    # return {}
    return actions.NullAction()


def handle_hero_turn_keys(state, key):
    # Stairs
    if key == '>':
        return actions.StairDownAction()
    elif key == '<':
        return actions.StairUpAction()

    # Actions
    if key == ',':
        return actions.PickupAction()

    elif key == 'i':
        return actions.ShowInvAction(prev_state=state)

    elif key == 'd':
        return actions.DropInvAction(prev_state=state)

    if key == '^x':
        return actions.CharScreenAction(prev_state=state)

    elif key == '.':
        return actions.WaitAction()

    # Movement
    if key == 'k':
        return actions.WalkAction(0, -1)  # Move Up
    elif key == 'j':
        return actions.WalkAction(0, 1)  # Move Down
    elif key == 'h':
        return actions.WalkAction(-1, 0) # Move Left
    elif key == 'l':
        return actions.WalkAction(1, 0) # Move Right
    elif key == 'y':
        return actions.WalkAction(-1, -1)  # Move NW
    elif key == 'u':
        return actions.WalkAction(1, -1)  # Move NE
    elif key == 'b':
        return actions.WalkAction(-1, 1)  # Move SW
    elif key == 'n':
        return actions.WalkAction(1, 1) # Move SE

    if key == '!a':
        return actions.FullScreenAction()  # Alt+Enter: Toggle full screen

    elif key == 'esc':
        return actions.ExitAction(state=state)

    return actions.NullAction()


def handle_hero_dead_keys(state, key):
    if key == 'i':
        return actions.ShowInvAction(prev_state=state)

    elif key == 'alt-enter':
        return actions.FullScreenAction()  # Alt+Enter: Toggle full screen

    elif key == '^x':
        return actions.CharScreenAction(prev_state=state)

    elif key == 'esc':
        return actions.ExitAction(state=state)

    return actions.NullAction()



def handle_inv_keys(state, key):
    if key == 'alt-enter':
        return actions.FullScreenAction()  # Alt+Enter: Toggle full screen

    elif key == 'esc':
        return actions.ExitAction(state=state)

    index = key_to_index(key)

    if index >= 0:
        if state == States.SHOW_INV:
            return actions.UseItemAction(inv_index=index)

        elif state == States.DROP_INV:
            return actions.DropItemAction(inv_index=index)

    return actions.NullAction()


def handle_main_menu(state, key):
    if key == 'n':
        return {'new_game': True}
    elif key == 'c':  # For "Continue"
        return {'load_game': True}
    elif key == 'o':
        return {'options': True}
    elif key == 'q':
        return {'exit': True}

    return {}
    # return actions.NullAction()


def handle_targeting_keys(state, key):
    # todo: Add ability to move a cursor to target.

    if key == 'esc':
        return actions.ExitAction(state=state)

    return actions.NullAction()


def handle_lvl_up_menu(state, key):
    if key == 'c':                 # Constitution
        return actions.LevelUpAction('hp')
    elif key == 's':               # Strength
        return actions.LevelUpAction('str')
    elif key == 'd':               # Defense
        return actions.LevelUpAction('def')

    return actions.NullAction()


def handle_char_scr(state, key):
    if key == 'esc':
        return actions.ExitAction(state=state)

    return actions.NullAction()


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


def handle_mouse(state, mouse):
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

    if state == States.TARGETING:
        if mouse.lbutton_pressed:
            return actions.TargetAction(x, y, lclick=True)
        elif mouse.rbutton_pressed:
            return actions.ExitAction(state=state)

        # elif mouse.mbutton_pressed:
            # return {'m_click': (x, y)}
            # return {'m_click': (x, y)}

    return None

def key_to_index(key):
    # Convert the key pressed to an index. a is 0, b is 1, etc.
    # todo: Do we need to constrain this to just letters?

    if len(key) == 1:
        return ord(key) - ord('a')

    return -1
