from pytest_mock import mocker
from ..src import input_handling
from ..src import states

States = states.States


def test_handle_keys__invalid_state():
    result = input_handling.handle_keys(key='a', state=None)
    assert result == {}


def test_handle_keys__HERO_TURN__calls_handle_hero_turn_keys(mocker):
    mocker.patch.object(input_handling, 'handle_hero_turn_keys')
    input_handling.handle_keys(key='a', state=States.HERO_TURN)

    input_handling.handle_hero_turn_keys.assert_called_with('a')


def test_handle_keys__HERO_DEAD__calls_handle_hero_dead_keys(mocker):
    mocker.patch.object(input_handling, 'handle_hero_dead_keys')
    input_handling.handle_keys(key='a', state=States.HERO_DEAD)

    input_handling.handle_hero_dead_keys.assert_called_with('a')


def test_handle_keys__TARGETING__calls_handle_targeting_keys(mocker):
    mocker.patch.object(input_handling, 'handle_targeting_keys')
    input_handling.handle_keys(key='a', state=States.TARGETING)

    input_handling.handle_targeting_keys.assert_called_with('a')


def test_handle_keys__SHOW_INV__calls_handle_inv_keys(mocker):
    mocker.patch.object(input_handling, 'handle_inv_keys')
    input_handling.handle_keys(key='a', state=States.SHOW_INV)

    input_handling.handle_inv_keys.assert_called_with('a')


def test_handle_keys__DROP_INV__calls_handle_inv_keys(mocker):
    mocker.patch.object(input_handling, 'handle_inv_keys')
    input_handling.handle_keys(key='a', state=States.DROP_INV)

    input_handling.handle_inv_keys.assert_called_with('a')


def test_handle_keys__LEVEL_UP__calls_handle_lvl_up_menu(mocker):
    mocker.patch.object(input_handling, 'handle_lvl_up_menu')
    input_handling.handle_keys(key='a', state=States.LEVEL_UP)

    input_handling.handle_lvl_up_menu.assert_called_with('a')


def test_handle_keys__SHOW_STATS__calls_handle_char_scr(mocker):
    mocker.patch.object(input_handling, 'handle_char_scr')
    input_handling.handle_keys(key='a', state=States.SHOW_STATS)

    input_handling.handle_char_scr.assert_called_with('a')




# def test_handle_hero_turn_keys(key):
# def test_handle_hero_dead_keys(key):
# def test_handle_inv_keys(key):
# def test_handle_main_menu(key):
# def test_handle_targeting_keys(key):
# def test_handle_mouse(mouse):
# def test_handle_lvl_up_menu(key):
# def test_handle_char_scr(key):
