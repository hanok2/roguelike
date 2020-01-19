from . import config
from . import dungeon
from . import fov
from . import player
from .messages import MsgLog


class Game(object):
    def __init__(self):
        # Create the hero
        new_hero = player.get_hero()

        # Initialize the Dungeon
        new_dungeon = dungeon.Dungeon(new_hero)

        # Initialize the MsgLog
        msg_log = MsgLog(x=1, width=config.scr_width, height=config.msg_height)

        self.hero = new_hero
        self.dungeon = new_dungeon
        self.stage = self.dungeon.get_stage()
        self.msg_log = msg_log
        self.state = config.States.HERO_TURN
        self.prev_state = self.state
        self.turns = 0

        # Keep track of any targeting items that were selected.
        self.targeting_item = None

        # Keep track of any alternate Actions
        self.next_action = None

        self.fov_recompute = True
        self.fov_map = fov.initialize_fov(self.stage)
        self.redraw = False


def get_game_data():
    # Create the hero
    hero = player.get_hero()

    # Initialize the Dungeon
    new_dungeon = dungeon.Dungeon(hero)

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
    return new_dungeon, msg_log, state, turn
