import tcod
from game_states import GameStates
from render_functions import RenderOrder


def kill_player(player):
    player.char = '%'
    player.color = tcod.dark_red
    return 'You died!', GameStates.PLAYER_DEAD


def kill_monster(monster):
    death_msg = '{} is dead!'.format(monster.name.capitalize())

    monster.char = '%'
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.render_order = RenderOrder.CORPSE
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name

    return death_msg
