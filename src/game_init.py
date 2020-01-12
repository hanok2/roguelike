from . import config
from . import maps
from . import player
from .messages import MsgLog
from .states import States


# todo: Convert to a Game object, tracking all game data....
def get_game_data():
    # Create the hero
    hero = player.get_hero()

    # Initialize the Dungeon
    dungeon = maps.Dungeon(hero)

    msg_log = MsgLog(
        x=1,
        width=config.scr_width,
        height=config.msg_height
    )

    state = States.HERO_TURN
    turn = 0

    return dungeon, msg_log, state, turn
