import tcod
from . import config
from .components import Fighter, ApproachingBehavior
from .entity import Entity
from .random_utils import rnd_choice_from_dict, from_dungeon_lvl
from .render_functions import RenderOrder
"""
    Monster database:
        1. create a list of monsters, then it's picked from randomly
        2. Create a dictionary of monsters, which is picked from randomly.
        3. Have an external JSON file which contains the data for all monsters.
"""


monster_chances = {
    'spider': 80,
    'orc': 80,
    'troll': 40,
    # 'troll': from_dungeon_lvl(config.troll_chances, dungeon_lvl)
}


def get_random_monster(x, y):
    if x < 0 or y < 0:
        raise ValueError('x and y coordinates must be 0 or greater!')

    monster_choice = rnd_choice_from_dict(monster_chances)

    return mk_monster(monster_choice, x, y)


def mk_monster(monster, x, y):
    if monster == 'spider':
        return Entity(
            x, y,
            's',
            tcod.desaturated_green,
            'Spider',
            blocks=True,
            render_order=RenderOrder.ACTOR,
            fighter=Fighter(hp=5, defense=0, power=2, xp=5),
            ai=ApproachingBehavior()
        )
    elif monster == 'orc':
        return Entity(
            x, y,
            'o',
            tcod.desaturated_green,
            'Orc',
            blocks=True,
            render_order=RenderOrder.ACTOR,
            fighter=Fighter(hp=10, defense=1, power=3, xp=35),
            ai=ApproachingBehavior()
        )
    elif monster == 'troll':
        return Entity(
            x, y,
            'T',
            tcod.darker_green,
            'Troll',
            blocks=True,
            render_order=RenderOrder.ACTOR,
            fighter=Fighter(hp=10, defense=2, power=4, xp=100),
            ai=ApproachingBehavior()
        )
    else:
        raise ValueError('Unknown monster selected: {}'.format(monster))
