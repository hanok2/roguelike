import shelve
import os
from . import game

# Flags
# r: read-only
# w: open for reading and writing
# n: delete old and write new file
# c: open for reading adn writing, but also create new file if it DNE

# Protocols
# By default the call to shelve.open() uses the oldest, least efficient version.
# ensures that it will be the most widely supported
# For more efficiency, pass the integer 2 for this parameter (the versions are
# currently 0, 1, and 2). Or if you have "import pickle" in your script, you can
# pass pickle.HIGHEST_PROTOCOL and this will always use the latest version of the
# pickling protocol. But be warned, earlier versions of Python may not be able to
# read the shelf files produced by later versions of Python running your game script.


def save_game(filepath, game):
    with shelve.open(filepath, 'n') as data_file:
        data_file['hero'] = game.hero
        data_file['dungeon'] = game.dungeon
        data_file['stage'] = game.stage
        data_file['msg_log'] = game.msg_log
        data_file['state'] = game.state
        data_file['prev_state'] = game.prev_state
        data_file['turns'] = game.turns
        data_file['targeting_item'] = game.targeting_item
        data_file['action_queue'] = game.action_queue
        data_file['fov_recompute'] = game.fov_recompute
        data_file['fov_map'] = game.fov_map
        data_file['redraw'] = game.redraw


def load_game(filepath):
    if os.path.exists(filepath):
        with shelve.open(filepath, 'r') as data_file:
            _game = game.Game()
            _game.load_game(data_file)
        return _game

    # Could not find file
    return None
