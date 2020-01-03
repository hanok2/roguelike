import tcod
from game_states import GameStates


def handle_keys(key, game_state):
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn_keys(key)

    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)

    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)

    elif game_state in (GameStates.INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inv_keys(key)

    elif game_state == GameStates.LEVEL_UP:
        return handle_level_up_menu(key)

    elif game_state == GameStates.CHARACTER_SCREEN:
        return handle_character_screen(key)

    return {}


def handle_player_turn_keys(key):
    key_char = chr(key.c)

    # Actions
    if key_char == 'g' or key_char == ',':
        return {'pickup': True}
    elif key_char == 'i':
        return {'inventory': True}
    elif key_char == 'd':
        return {'drop_inv': True}

    # Trouble shoot > input later
    elif key_char == '>' or key.vk == tcod.KEY_ENTER:
        return {'take_stairs': True}

    elif key_char == '\\':
        return {'show_character_screen': True}

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
        return {'fullscreen': True}

    elif key.vk == tcod.KEY_ESCAPE:
        # Exit
        return {'exit': True}

    # No key was pressed
    return {}


def handle_player_dead_keys(key):
    key_char = chr(key.c)

    if key_char == 'i':
        return {'inventory': True}

    if key.vk == tcod.KEY_ENTER and key.lalt:
        # Alt+Enter: Toggle full screen
        return {'fullscreen': True}

    elif key.vk == tcod.KEY_ESCAPE:
        # Exit
        return {'exit': True}

    return {}


def handle_inv_keys(key):
    # Convert the key pressed to an index. a is 0, b is 1, etc.
    index = key.c - ord('a')

    if index >= 0:
        return {'inv_index': index}

    if key.vk == tcod.KEY_ENTER and key.lalt:
        # Alt+Enter: Toggle full screen
        return {'fullscreen': True}

    elif key.vk == tcod.KEY_ESCAPE:
        # Exit the menu
        return {'exit': True}

    return {}


def handle_main_menu(key):
    key_char = chr(key.c)

    if key_char == 'a':
        return {'new_game': True}
    elif key_char == 'b':
        return {'load_game': True}
    elif key_char == 'c' or key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}

    return {}


def handle_targeting_keys(key):
    if key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}

    return {}


def handle_mouse(mouse):
    (x, y) = (mouse.cx, mouse.cy)

    if mouse.lbutton_pressed:
        return {'left_click': (x, y)}
    elif mouse.rbutton_pressed:
        return {'right_click': (x, y)}

    return {}


def handle_level_up_menu(key):
    if key:
        key_char = chr(key.c)


        if key_char == 'a':
            return {'level_up': 'hp'}
        elif key_char == 'b':
            return {'level_up': 'str'}
        elif key_char == 'c':
            return {'level_up': 'def'}

    return {}


def handle_character_screen(key):
    if key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}
    return {}
