import os
import shelve
from pytest_mock import mocker
from ..src import data_loaders
from ..src import game

TEMP_DIR = 'temp'
TEMP_FILE = TEMP_DIR + '/savegame.dat'


def test_save_game():
    g = game.Game()
    # dungeon, msg_log, state, turns = game.get_game_data()

    # Check if temp dir exists
    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)

    data_loaders.save_game(TEMP_FILE, g)

    assert os.path.exists(TEMP_FILE)

    # clean up the file
    os.remove(TEMP_FILE)


def test_save_game__calls_shelve(mocker):
    mocker.patch('shelve.open')
    data_loaders.save_game(TEMP_FILE, game=None)

    shelve.open.assert_called_once()
    shelve.open.assert_called_with(TEMP_FILE, 'n')


def test_load_game__calls_shelve(mocker):
    mocker.patch('shelve.open')
    data_loaders.load_game('savegame.dat')

    shelve.open.assert_called_with('savegame.dat', 'r')
