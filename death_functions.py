import tcod
from states import States
from render_functions import RenderOrder
from messages import Msg


def kill_hero(hero):
    hero.char = '%'
    hero.color = tcod.dark_red
    return Msg('You died!', tcod.dark_red), States.HERO_DEAD


def kill_monster(monster):
    monster.char = '%'
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.render_order = RenderOrder.CORPSE
    monster.fighter = None
    monster.ai = None

    death_msg = 'The {} dies!'.format(monster.name.capitalize())
    monster.name = 'remains of ' + monster.name

    return Msg(death_msg, tcod.orange)
