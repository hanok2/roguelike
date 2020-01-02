import tcod


def main():
    # print("Hello Steampunk World!!!")

    screen_width = 80
    screen_height = 50
    img_file = 'images/arial10x10.png'

    tcod.console_set_custom_font(img_file, tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

    # Creates the screen.
    # Boolean specifies full screen
    tcod.console_init_root(screen_width, screen_height, 'libtcod tutorial revised', False)

    # Game loop
    while not tcod.console_is_window_closed():
        tcod.console_set_default_foreground(0, tcod.white)

        # Game symbol
        tcod.console_put_char(0, 1, 1, '@', tcod.BKGND_NONE)

        # Presents everything on screen
        tcod.console_flush()

        # Get keyboard input
        key = tcod.console_check_for_keypress()

        # Check input
        if key.vk == tcod.KEY_ESCAPE:
            return True

if __name__ == "__main__":
    main()
