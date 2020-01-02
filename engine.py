import tcod
from entity import Entity
from render_functions import clear_all, render_all


def main():
    # print("Hello Steampunk World!!!")

    img_file = 'images/arial10x10.png'
    screen_width = 80
    screen_height = 50

    # player_x = int(screen_width / 2)
    # player_y = int(screen_height / 2)

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

    con = tcod.console_new(screen_width, screen_height)

    key = tcod.Key()
    mouse = tcod.Mouse()

    # Game loop
    while not tcod.console_is_window_closed():
        # Capture new user input
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)

        # tcod.console_set_default_foreground(0, tcod.white)
        # tcod.console_set_default_foreground(con, tcod.white)

        # Game symbol
        # tcod.console_put_char(0, 1, 1, '@', tcod.BKGND_NONE)
        # tcod.console_put_char(0, player_x, player_y, '@', tcod.BKGND_NONE)
        # tcod.console_put_char(con, player_x, player_y, '@', tcod.BKGND_NONE)
        # tcod.console_put_char(con, player.x, player.y, '@', tcod.BKGND_NONE)

        # tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

        # Render all entities
        render_all(con, entities, screen_width, screen_height)

        # Presents everything on screen
        tcod.console_flush()

        # tcod.console_put_char(con, player_x, player_y, ' ', tcod.BKGND_NONE)
        # tcod.console_put_char(con, player.x, player.y, ' ', tcod.BKGND_NONE)

        # Clear all entities
        clear_all(con, entities)

        # Get keyboard input
        # key = tcod.console_check_for_keypress()
        action = handle_keys(key)

        move = action.get('move')
        gameexit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move:
            dx, dy = move
            # player_x += dx
            # player_y += dy
            player.move(dx, dy)


        # if key.vk == tcod.KEY_ESCAPE:
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
