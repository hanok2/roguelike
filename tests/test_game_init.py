from ..src import game_init
from ..src import dungeon
from ..src import messages
from ..src.config import States


def test_get_game_data__Dungeon():
    _dungeon, msg_log, state, turn = game_init.get_game_data()
    assert isinstance(_dungeon, dungeon.Dungeon)


def test_get_game_data__MsgLog():
    _dungeon, msg_log, state, turn = game_init.get_game_data()
    assert isinstance(msg_log, messages.MsgLog)


def test_get_game_data__State_is_HERO_TURN():
    _dungeon, msg_log, state, turn = game_init.get_game_data()
    assert state == States.HERO_TURN


def test_get_game_data__turn_is_0():
    _dungeon, msg_log, state, turn = game_init.get_game_data()
    assert turn == 0
