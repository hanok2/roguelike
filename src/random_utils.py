from random import randint


def rnd_choice_index(chances):
    """Takes a list of integers that represent weights and takes a random pick.
        Returns the index of the weight that was picked.
    """
    # Generate a random # up to the sum of all chance weights
    rnd_chance = randint(1, sum(chances))

    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        if rnd_chance <= running_sum:
            return choice
        choice += 1


def rnd_choice_from_dict(choice_dict):
    choices = list(choice_dict.keys())
    chances = list(choice_dict.values())

    return choices[rnd_choice_index(chances)]


def from_dungeon_lvl(table, dungeon_lvl):
    """ Takes a table of [value, level] pairs in a list, and a dungeon level to query.
        Returns the weight value appropriate for the dungeon lvl.
        If the exact level is not listed, it finds the lower level and returns that value.
    """
    if dungeon_lvl < 0:
        raise ValueError('dungeon_lvl cannot be less than 0!')

    for (value, lvl) in reversed(table):
        if dungeon_lvl >= lvl:
            return value

    # If the level is less than any listed levels, it return 0.
    return 0
