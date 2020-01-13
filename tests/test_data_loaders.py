import shelve
from pytest_mock import mocker
from ..src import data_loaders


def test_save_game__calls_shelve(mocker):
    mocker.patch('shelve.open')
    data_loaders.save_game(dungeon=None, msg_log=None, state=None, turns=0)

    shelve.open.assert_called_once()
    shelve.open.assert_called_with('savegame.dat', 'n')


def test_load_game__calls_shelve(mocker):
    mocker.patch('shelve.open')
    data_loaders.load_game()

    shelve.open.assert_called_with('savegame.dat', 'r')
