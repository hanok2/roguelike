import os
import shelve

def save_game(hero, entities, game_map, msg_log, state):
    with shelve.open('savegame.dat', 'n') as data_file:
        data_file['hero_index'] = entities.index(hero)
        data_file['entities'] = entities
        data_file['game_map'] = game_map
        data_file['msg_log'] = msg_log
        data_file['state'] = state


def load_game():
    if not os.path.isfile('savegame.dat'):
        raise FileNotFoundError

    with shelve.open('savegame.dat', 'r') as data_file:
        hero_index = data_file['hero_index']
        entities = data_file['entities']
        game_map = data_file['game_map']
        msg_log = data_file['msg_log']
        state = data_file['state']

    hero = entities[hero_index ]

    return hero, entities, game_map, msg_log, state
