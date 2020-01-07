import tcod
import config

MAX_MENU_ITEMS = 26



def menu(root, con, header, options, width):
    """ Display a menu of options. Each option has a letter to the left side."""
    if len(options) > MAX_MENU_ITEMS:
        raise ValueError('Cannot have a menu with more than 26 options.')

    # Calculate total height for the header (after auto-wrap) and one line per option
    header_height = tcod.console_get_height_rect(
        con=con,
        x=0, y=0,
        w=width,
        h=config.scr_height,
        fmt=header
    )

    height = len(options) + header_height

    # Create an off-screen console that represents the menu's window
    window = tcod.console_new(w=width, h=height)

    # Print the header, with auto-wrap
    tcod.console_set_default_foreground(con=window, col=tcod.white)

    # Print a string constrained to a rectangle with blend and alignment.
    tcod.console_print_rect_ex(
        con=window,
        x=0, y=0,
        w=width,
        h=height,
        flag=tcod.BKGND_NONE,
        alignment=tcod.LEFT,
        fmt=header
    )

    # Print all the options
    y = header_height

    for k, v in options.items():
        text = '({}) {}'.format(k, v)

        tcod.console_print_ex(
            con=window,
            x=0, y=y,
            flag=tcod.BKGND_NONE,
            alignment=tcod.LEFT,
            fmt=text
        )
        y += 1

    x = int(config.scr_width / 2 - width / 2)
    # y = int(config.scr_height / 2 - height / 2)
    y = 5

    # Blit the contents of "window" to the root console
    window.blit(
        dest=root,
        dest_x=x, dest_y=y,
        src_x=0, src_y=0,
        width=width,
        height=height,
        fg_alpha=1.0,
        bg_alpha=0.7,
    )


def default_lettering_dict(options):
    """Create a default set of letters (starting from 'a') for a list of options.
        Returns a dict with the letters as keys and options as values.
    """
    letter_index = ord('a')
    option_dict = {}
    for o in options:
        new_char = chr(letter_index)
        option_dict[new_char] = o
        letter_index += 1
    return option_dict


def list_all_inv_items(hero):
    """ Returns a list of all items the hero currently has in inventory.
        If the hero has an item equipped, it will display the slot the item is
        equipped in parentheses.
    """

    options = []

    for item in hero.inv.items:
        if hero.equipment.main_hand == item:
            options.append('{} (on main hand)'.format(item.name))
        elif hero.equipment.off_hand == item:
            options.append('{} (on off hand)'.format(item.name))
        else:
            options.append(item.name)

    return options


def inv_menu(root, con, header, hero, inv_width):
    """ Show a menu with each item of the inventory as an option """

    if len(hero.inv.items) == 0:
        options = ['Inventory is empty.']
    else:
        options = list_all_inv_items(hero)
        options = default_lettering_dict(options)

        menu(root, con, header, options, inv_width)


def main_menu(root, con, menu_img):
    """ Displays the main menu for the game."""

    tcod.image_blit_2x(
        image=menu_img,
        console=root,
        dx=0,
        dy=0
    )

    root.default_fg=tcod.light_yellow

    # Display game title
    title_x = int(config.scr_width / 2)

    # title_y = int(config.scr_height / 2) - 4
    title_y = 3

    root.print(
        x=title_x, y=title_y,
        string=config.game_title,
        alignment=tcod.CENTER
    )

    # Display author
    author_x = int(config.scr_width / 2)
    author_y = int(config.scr_height - 2)
    # author_y = int(config.scr_height - 2)

    root.print(
        x=author_x, y=author_y,
        string='By {}'.format(config.author),
        alignment=tcod.CENTER,
    )

    # Display main menu options
    options = {
        'n': 'New game',
        'c': 'Continue last game',
        'o': 'Options',
        'q': 'Quit'
    }

    menu(root, con, '', options, 24)


def msg_box(con, header, width):
    menu(con, header, [], width, config.scr_width, config.scr_height)


def lvl_up_menu(root, con, header, hero, menu_width):
    """Displays a menu for the player when they reach a level-up. Gives them
        choice of different stat boosts to pick from.
    """
    options = {
        'c': 'Constitution (+20 HP, from {})'.format(hero.fighter.max_hp),
        's': 'Strength (+1 attack, from {})'.format(hero.fighter.power),
        'a': 'Agility (+1 defense, from {})'.format(hero.fighter.defense)
    }

    menu(root, con, header, options, menu_width, config.scr_width, config.scr_height)


def char_scr(root, hero):
    """ Displays a windows showing the hero's current stats and experience."""
    window = tcod.console.Console(
        width=config.char_scr_width,
        height=config.char_scr_height
    )

    window.default_fg = tcod.white

    # todo: Add a loop here
    info = [
        'Character Information',
        'Level: {}'.format(hero.lvl.current_lvl),
        'Experience: {}'.format(hero.lvl.current_xp),
        'Experience to Level: {}'.format(hero.lvl.xp_to_next_lvl),
        'Maximum HP: {}'.format(hero.fighter.max_hp),
        'Attack: {}'.format(hero.fighter.power),
        'Defense: {}'.format(hero.fighter.defense),
    ]

    for i, row in enumerate(info):
        window.print_box(
            x=0, y=i+1,
            width=config.char_scr_width,
            height=config.char_scr_height,
            string=row,
            alignment=tcod.LEFT,
        )

    x = config.scr_width // 2 - config.char_scr_width // 2
    # y = config.scr_height // 2 - config.char_scr_height // 2
    y = 5

    window.blit(
        dest=root,
        dest_x=x, dest_y=y,
        src_x=0, src_y=0,
        width=config.char_scr_width,
        height=config.char_scr_height,
        fg_alpha=1.0,
        bg_alpha=0.7
    )
