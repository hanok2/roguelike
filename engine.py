import tcod
from entity import Entity
from render_functions import clear_all, render_all
from game_map import GameMap


def main():
    img_file = 'images/arial10x10.png'
    screen_width = 80
    screen_height = 50
    map_width= 80
    map_height = 45

    colors = {
        'dark_wall': tcod.Color(0, 0, 100),
        'dark_ground': tcod.Color(50, 50, 150)
    }

    # Create entities
    player = Entity(
        x=screen_width // 2,
        y=screen_height // 2,
        char='@',
        color=tcod.white
    )

    npc = Entity(
        x=screen_width // 2 - 5,
        y=screen_height // 2,
        char='@',
        color=tcod.yellow
    )

    entities = [npc, player]

    tcod.console_set_custom_font(img_file, tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

    # Creates the screen. (Boolean specifies full screen)
    tcod.console_init_root(screen_width, screen_height, 'libtcod tutorial revised', False)

    # Initialize the console
    con = tcod.console_new(screen_width, screen_height)

    # Initialize the game map
    game_map = GameMap(map_width, map_height)

    key = tcod.Key()
    mouse = tcod.Mouse()

    # Game loop
    while not tcod.console_is_window_closed():
        # Capture new user input
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)

        # Render all entities
        render_all(con, entities, game_map, screen_width, screen_height, colors)

        # Presents everything on screen
        tcod.console_flush()

        # Clear all entities
        clear_all(con, entities)

        # Get keyboard input
        action = handle_keys(key)

        move = action.get('move')
        gameexit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move:
            dx, dy = move

            if not game_map.is_blocked(player.x + dx, player.y +dy):
                player.move(dx, dy)

        if gameexit:
            return True

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())


def handle_keys(key):
    # Movement
    if key.vk == tcod.KEY_UP:
        return {'move': (0, -1)}
    elif key.vk == tcod.KEY_DOWN:
        return {'move': (0, 1)}
    elif key.vk == tcod.KEY_LEFT:
        return {'move': (-1, 0)}
    elif key.vk == tcod.KEY_RIGHT:
        return {'move': (1, 0)}

    if key.vk == tcod.KEY_ENTER and key.lalt:
        # Alt+Enter: Toggle full screen
        return {'fullscreen': True}

    elif key.vk == tcod.KEY_ESCAPE:
        # Exit
        return {'exit': True}

    # No key was pressed
    return {}


if __name__ == "__main__":
    main()
