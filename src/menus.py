from .states import States


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


# Move to player/entity class?
def list_inv_items(hero):
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


def lvl_up_options(hero):
    """Displays a menu for the player when they reach a level-up. Gives them
        choice of different stat boosts to pick from.
    """
    header = 'Level up! Choose a stat to raise:'

    options = {
        'c': 'Constitution (+20 HP, from {})'.format(hero.fighter.max_hp),
        's': 'Strength (+1 attack, from {})'.format(hero.fighter.power),
        'a': 'Agility (+1 defense, from {})'.format(hero.fighter.defense)
    }
    return header, options


def inv_options(hero, state):
    """ Show a menu with each item of the inventory as an option """
    if state == States.SHOW_INV:
        header = 'Press the key next to an item to use it, or ESC to cancel.\n'
    else:
        header = 'Press the key next to an item to drop it, or ESC to cancel.\n'

    if len(hero.inv.items) == 0:
        options = ['Inventory is empty.']
    else:
        options = list_inv_items(hero)
        options = default_lettering_dict(options)

    return header, options


def hero_info(hero):
    info = [
        'Character Information',
        'Level: {}'.format(hero.lvl.current_lvl),
        'Experience: {}'.format(hero.lvl.current_xp),
        'Experience to Level: {}'.format(hero.lvl.xp_to_next_lvl),
        'Maximum HP: {}'.format(hero.fighter.max_hp),
        'Attack: {}'.format(hero.fighter.power),
        'Defense: {}'.format(hero.fighter.defense),
    ]
    return info

def main_menu_options():
    return {
        'n': 'New game',
        'c': 'Continue last game',
        'o': 'Options',
        'q': 'Quit'
    }
