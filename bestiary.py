import config
import tcod
from components import Fighter, ApproachingBehavior, Item, EquipmentSlots, Equippable
from entity import Entity
from random_utils import rnd_choice_from_dict, from_dungeon_lvl
from render_functions import RenderOrder


def monster_chances(dungeon_lvl):
    return {
        'orc': 80,
        # 'troll': 20,
        'troll': from_dungeon_lvl(config.troll_chances, dungeon_lvl)
    }

def get_random_monster(x, y, monster_chances):
    monster_choice = rnd_choice_from_dict(monster_chances)

    if monster_choice == 'orc':
        # ORC
        fighter_comp = Fighter(hp=20, defense=0, power=4, xp=35)
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
        # TROLL
        fighter_comp = Fighter(hp=30, defense=2, power=8, xp=100)
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


