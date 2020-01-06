import tcod
import config

MAX_MENU_ITEMS = 26


def menu(con, header, options, width, scr_width, scr_height):
    if len(options) > MAX_MENU_ITEMS:
        raise ValueError('Cannot have a menu with more than 26 options.')

    # Calculate total height for the header (after auto-wrap) and one line per option
    header_height = tcod.console_get_height_rect(
        con,
        0, 0,
        width,
        scr_height,
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

    for k, v in options.items():
        text = '({}) {}'.format(k, v)

        tcod.console_print_ex(
            window,
            0, y,
            tcod.BKGND_NONE,
            tcod.LEFT,
            text
        )
        y += 1

    # Blit the contents of "window" to the root console
    x = int(scr_width / 2 - width / 2)
    # y = int(scr_height / 2 - height / 2)
    y = 5

    tcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)


def default_lettering_dict(options):
    letter_index = ord('a')
    option_dict = {}
    for o in options:
        new_char = chr(letter_index)
        option_dict[new_char] = o
        letter_index += 1
    return option_dict


def list_all_inv_items(hero):
    options = []

    for item in hero.inv.items:
        if hero.equipment.main_hand == item:
            options.append('{} (on main hand)'.format(item.name))
        elif hero.equipment.off_hand == item:
            options.append('{} (on off hand)'.format(item.name))
        else:
            options.append(item.name)

    return options


def inv_menu(con, header, hero, inv_width, scr_width, scr_height):
    # Show a menu w/ each item of the inventory as an option
    if len(hero.inv.items) == 0:
        options = ['Inventory is empty.']
    else:
        options = list_all_inv_items(hero)
        options = default_lettering_dict(options)

        menu(con, header, options, inv_width, scr_width, scr_height)


def main_menu(con, bg_img, scr_width, scr_height):
    tcod.image_blit_2x(bg_img, 0, 0, 0)

    tcod.console_set_default_foreground(0, tcod.light_yellow)

    # Display game title
    title_x = int(scr_width / 2)
    # title_y = int(scr_height / 2) - 4
    title_y = 3
    tcod.console_print_ex( 0, title_x, title_y, tcod.BKGND_NONE, tcod.CENTER, config.game_title,)

    # Display author
    author_x = int(scr_width / 2)
    author_y = int(scr_height - 2)
    # author_y = int(scr_height - 2)

    tcod.console_print_ex(0, author_x, author_y, tcod.BKGND_NONE, tcod.CENTER, 'By {}'.format(config.author))

    # Display main menu options
    options = {
        'n': 'New game',
        'c': 'Continue last game',
        'o': 'Options',
        'q': 'Quit'
    }

    menu(con, '', options, 24, scr_width, scr_height)


def msg_box(con, header, width, scr_width, scr_height):
    menu(con, header, [], width, scr_width, scr_height)


def lvl_up_menu(con, header, hero, menu_width, scr_width, scr_height):
    options = {
        'c': 'Constitution (+20 HP, from {})'.format(hero.fighter.max_hp),
        's': 'Strength (+1 attack, from {})'.format(hero.fighter.power),
        'a': 'Agility (+1 defense, from {})'.format(hero.fighter.defense)
    }

    menu(con, header, options, menu_width, scr_width, scr_height)


def char_scr(hero, char_scr_width, char_scr_height, scr_width, scr_height):
    window = tcod.console_new(char_scr_width, char_scr_height)

    tcod.console_set_default_foreground(window, tcod.white)

    tcod.console_print_rect_ex(window, 0, 1, char_scr_width, char_scr_height,
        tcod.BKGND_NONE, tcod.LEFT, 'Character Information')
    tcod.console_print_rect_ex( window, 0, 2, char_scr_width, char_scr_height,
        tcod.BKGND_NONE, tcod.LEFT, 'Level: {0}'.format(hero.lvl.current_lvl))
    tcod.console_print_rect_ex(window, 0, 3, char_scr_width, char_scr_height,
        tcod.BKGND_NONE, tcod.LEFT, 'Experience: {0}'.format(hero.lvl.current_xp))
    tcod.console_print_rect_ex(window, 0, 4, char_scr_width, char_scr_height,
        tcod.BKGND_NONE, tcod.LEFT, 'Experience to Level: {0}'.format(hero.lvl.xp_to_next_lvl))
    tcod.console_print_rect_ex(window, 0, 6, char_scr_width, char_scr_height,
        tcod.BKGND_NONE, tcod.LEFT, 'Maximum HP: {0}'.format(hero.fighter.max_hp))
    tcod.console_print_rect_ex(window, 0, 7, char_scr_width, char_scr_height,
        tcod.BKGND_NONE, tcod.LEFT, 'Attack: {0}'.format(hero.fighter.power))
    tcod.console_print_rect_ex(window, 0, 8, char_scr_width, char_scr_height,
        tcod.BKGND_NONE, tcod.LEFT, 'Defense: {0}'.format(hero.fighter.defense))

    x = scr_width // 2 - char_scr_width // 2
    y = scr_height // 2 - char_scr_height // 2

    tcod.console_blit(
        window,
        0, 0,
        char_scr_width,
        char_scr_height,
        0,
        x, y,
        1.0,
        0.7
    )
