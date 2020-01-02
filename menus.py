import tcod

MAX_MENU_ITEMS = 26


def menu(con, header, options, width, screen_width, screen_height):
    if len(options) > MAX_MENU_ITEMS:
        raise ValueError('Cannot have a menu with more than 26 options.')

    # Calculate total height for the header (after auto-wrap) and one line per option
    header_height = tcod.console_get_height_rect(
        con,
        0, 0,
        width,
        screen_height,
        header
    )

    height = len(options) + header_height

    # Create an off-screen console that represents the menu's window
    window = tcod.console_new(width, height)

    # Print the header, with auto-wrap
    tcod.console_set_default_foreground(window, tcod.white)

    tcod.console_print_rect_ex(
        window,
        0, 0,
        width,
        height,
        tcod.BKGND_NONE,
        tcod.LEFT,
        header
    )

    # Print all the options
    y = header_height
    letter_index = ord('a')

    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text

        tcod.console_print_ex(
            window,
            0, y,
            tcod.BKGND_NONE,
            tcod.LEFT,
            text
        )
        y += 1
        letter_index += 1

    # Blit the contents of "window" to the root console
    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)

    tcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)


def inv_menu(con, header, inv, inv_width, screen_width, screen_height):
    # Show a menu w/ each item of the inventory as an option
    if len(inv.items) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in inv.items]

    menu(con, header, options, inv_width, screen_width, screen_height)
