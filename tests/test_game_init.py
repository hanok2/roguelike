from ..src import game_init
from ..src import maps
from ..src import messages
from ..src import states


def test_get_game_data__Dungeon():
    dungeon, msg_log, state, turn = game_init.get_game_data()
    assert isinstance(dungeon, maps.Dungeon)


def test_get_game_data__MsgLog():
    dungeon, msg_log, state, turn = game_init.get_game_data()
    assert isinstance(msg_log, messages.MsgLog)


def test_get_game_data__State_is_HERO_TURN():
    dungeon, msg_log, state, turn = game_init.get_game_data()
    assert state == states.States.HERO_TURN


def test_get_game_data__turn_is_0():
    dungeon, msg_log, state, turn = game_init.get_game_data()
    assert turn == 0
