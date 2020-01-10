import os
import shelve
from . import config

def save_game(dungeon, msg_log, state, turns):
    with shelve.open(config.savefile, 'n') as data_file:
        data_file['dungeon'] = dungeon
        data_file['msg_log'] = msg_log
        data_file['state'] = state
        data_file['turns'] = turns


def load_game():
    if not os.path.isfile(config.savefile):
        raise FileNotFoundError

    with shelve.open(config.savefile, 'r') as data_file:
        dungeon = data_file['dungeon']
        msg_log = data_file['msg_log']
        state = data_file['state']
        turns = data_file['turns']

    return dungeon, msg_log, state, turns
