from . import actionqueue
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
        self.state = config.States.ACTOR_TURN
        self.prev_state = self.state
        self.turns = 0

        # Keep track of any targeting items that were selected.
        self.targeting_item = None

        self.action_queue = actionqueue.ActionQueue()

        self.fov_recompute = True
        self.fov_map = fov.initialize_fov(self.stage)
        self.redraw = False

    def load_game(self, data_file):
        self.hero = data_file['hero']
        self.dungeon = data_file['dungeon']
        self.stage = data_file['stage']
        self.msg_log = data_file['msg_log']
        self.state = data_file['state']
        self.prev_state = data_file['prev_state']
        self.turns = data_file['turns']
        self.targeting_item = data_file['targeting_item']
        self.action_queue = data_file['action_queue']
        self.fov_recompute = data_file['fov_recompute']
        self.fov_map = data_file['fov_map']
        self.redraw = data_file['redraw']

        # Fix double hero - on load we have a problem with a copy on the stage
        self.stage.rm_hero()
        self.stage.entities.append(self.hero)
