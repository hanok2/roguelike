import tcod
from game_states import GameStates
from render_functions import RenderOrder
from game_messages import Message


def kill_player(player):
    player.char = '%'
    player.color = tcod.dark_red
    return Message('You died!', tcod.dark_red), GameStates.PLAYER_DEAD


def kill_monster(monster):
    monster.char = '%'
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.render_order = RenderOrder.CORPSE
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name

    death_msg = '{} is dead!'.format(monster.name.capitalize())
    return Message(death_msg, tcod.orange)
