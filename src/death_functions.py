import tcod
from . import components
from .states import States
from .render_functions import RenderOrder


def kill_hero(hero):
    hero.char = '%'
    hero.color = tcod.dark_red
    return 'You died!', States.HERO_DEAD


def kill_monster(monster):
    monster.char = '%'
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.render_order = RenderOrder.CORPSE
    monster.fighter = None
    monster.ai = None

    # Change to an item so we can pick it up!
    monster.item = components.Item()

    death_msg = 'The {} dies!'.format(monster.name.capitalize())
    monster.name = 'remains of ' + monster.name

    return death_msg
