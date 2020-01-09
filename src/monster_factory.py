import tcod
from . import config
from .components import Fighter, ApproachingBehavior
from .entity import Entity
from .random_utils import rnd_choice_from_dict, from_dungeon_lvl
from .render_functions import RenderOrder


def monster_chances(dungeon_lvl):
    return {
        'spider': 80,
        'orc': 80,
        'troll': 40,
        # 'troll': from_dungeon_lvl(config.troll_chances, dungeon_lvl)
    }

def get_random_monster(x, y, monster_chances):
    monster_choice = rnd_choice_from_dict(monster_chances)

    if monster_choice == 'spider':
        fighter_comp = Fighter(hp=5, defense=0, power=2, xp=5)
        ai_comp = ApproachingBehavior()
        monster = Entity(
            x, y,
            's',
            tcod.desaturated_green,
            'Spider',
            blocks=True,
            render_order=RenderOrder.ACTOR,
            fighter=fighter_comp,
            ai=ai_comp
        )
    elif monster_choice == 'orc':
        fighter_comp = Fighter(hp=10, defense=1, power=3, xp=35)
        ai_comp = ApproachingBehavior()
        monster = Entity(
            x, y,
            'o',
            tcod.desaturated_green,
            'Orc',
            blocks=True,
            render_order=RenderOrder.ACTOR,
            fighter=fighter_comp,
            ai=ai_comp
        )
    elif monster_choice == 'troll':
        fighter_comp = Fighter(hp=10, defense=2, power=4, xp=100)
        ai_comp = ApproachingBehavior()
        monster = Entity(
            x, y,
            'T',
            tcod.darker_green,
            'Troll',
            blocks=True,
            render_order=RenderOrder.ACTOR,
            fighter=fighter_comp,
            ai=ai_comp
        )
    else:
        raise ValueError('Unknown monster selected: {}'.format(monster_choice))

    return monster
