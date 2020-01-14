from . import config
from . import maps
from . import player
from .messages import MsgLog


# todo: Convert to a Game object, tracking all game data....

def get_game_data():
    # Create the hero
    hero = player.get_hero()

    # Initialize the Dungeon
    dungeon = maps.Dungeon(hero)

    # Initialize the MsgLog
    msg_log = MsgLog(
        x=1,
        width=config.scr_width,
        height=config.msg_height
    )

    # Set the initial game state
    state = config.States.HERO_TURN

    # Set the turn counter to 0
    turn = 0

    # Return a tuple to start the game
    return dungeon, msg_log, state, turn
