import os
import shelve

def save_game(dungeon, msg_log, state, turns):
    with shelve.open('savegame.dat', 'n') as data_file:
        # data_file['hero_index'] = entities.index(hero)
        # data_file['entities'] = entities
        data_file['dungeon'] = dungeon
        # data_file['current_map'] = current_map
        data_file['msg_log'] = msg_log
        data_file['state'] = state
        data_file['turns'] = turns


def load_game():
    if not os.path.isfile('savegame.dat'):
        raise FileNotFoundError

    with shelve.open('savegame.dat', 'r') as data_file:
        # hero_index = data_file['hero_index']
        # entities = data_file['entities']
        dungeon = data_file['dungeon']
        # current_map = data_file['current_map']
        msg_log = data_file['msg_log']
        state = data_file['state']
        turns = data_file['turns']

    # hero = entities[hero_index ]

    return dungeon, msg_log, state, turns
