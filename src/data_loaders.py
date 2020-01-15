import shelve

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


def save_game(filepath, dungeon, msg_log, state, turns):
    with shelve.open(filepath, 'n') as data_file:
        data_file['dungeon'] = dungeon
        data_file['msg_log'] = msg_log
        data_file['state'] = state
        data_file['turns'] = turns


def load_game(filepath):
    with shelve.open(filepath, 'r') as data_file:
        dungeon = data_file['dungeon']
        msg_log = data_file['msg_log']
        state = data_file['state']
        turns = data_file['turns']

    return dungeon, msg_log, state, turns
