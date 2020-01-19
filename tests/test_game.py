from ..src import config
from ..src import game
from ..src import dungeon
from ..src import messages
from ..src import player
from ..src import stages
from ..src.config import States


""" Tests for Game class """


def test_Game_init__hero():
    g = game.Game()
    assert isinstance(g.hero, player.Player)


def test_Game_init__dungeon_is_None():
    g = game.Game()
    assert isinstance(g.dungeon, dungeon.Dungeon)
    assert g.dungeon.current_stage == 0


def test_Game_init__stage():
    g = game.Game()
    assert isinstance(g.stage, stages.Stage)


def test_Game_init__msg_log_is_None():
    g = game.Game()
    assert isinstance(g.msg_log, messages.MsgLog)


def test_Game_init__state_is_None():
    g = game.Game()
    assert g.state == config.States.HERO_TURN


def test_Game_init__prev_state_equals_state():
    g = game.Game()
    assert g.prev_state == g.state


def test_Game_init__turns_is_0():
    g = game.Game()
    assert g.turns == 0


def test_Game_init__targeting_item_is_None():
    g = game.Game()
    assert g.targeting_item is None


def test_Game_init__next_action_is_None():
    g = game.Game()
    assert g.next_action is None


def test_Game_init__fov_recompute_is_True():
    g = game.Game()
    assert g.fov_recompute


def test_Game_init__fov_map():
    g = game.Game()
    assert g.fov_map


def test_Game_init__redraw_is_False():
    g = game.Game()
    assert g.redraw is False


""" Tests for get_game_data."""


def test_get_game_data__Dungeon():
    _dungeon, msg_log, state, turn = game.get_game_data()
    assert isinstance(_dungeon, dungeon.Dungeon)


def test_get_game_data__MsgLog():
    _dungeon, msg_log, state, turn = game.get_game_data()
    assert isinstance(msg_log, messages.MsgLog)


def test_get_game_data__State_is_HERO_TURN():
    _dungeon, msg_log, state, turn = game.get_game_data()
    assert state == States.HERO_TURN


def test_get_game_data__turn_is_0():
    _dungeon, msg_log, state, turn = game.get_game_data()
    assert turn == 0
