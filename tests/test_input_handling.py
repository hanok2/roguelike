from pytest_mock import mocker
import tcod
from ..src import input_handling
from ..src import states

""" Shorthand:
    # = Windows Key
    ! = Alt
    ^ = Control
    + = Shift
"""
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


def test_process_tcod_input__h_returns_h():
    key = tcod.Key()
    key.c = ord('h')
    assert  input_handling.process_tcod_input(key) == 'h'


def test_process_tcod_input__ESC_returns_esc():
    esc_key = tcod.Key(pressed=True, vk=tcod.KEY_ESCAPE, c=ord('\x1b'))
    assert input_handling.process_tcod_input(esc_key) == 'esc'


def test_process_tcod_input__control_x_returns_carrot_x():
    ctrl_x = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('x'), lctrl=True)
    assert input_handling.process_tcod_input(ctrl_x) == '^x'


def test_process_tcod_input__H_returns_H():
    # Check that capslock is not on??
    H_key = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('H'))
    assert input_handling.process_tcod_input(H_key) == 'H'


def test_process_tcod_input_ranglebracket():
    rangle_bracket = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('>'))
    assert input_handling.process_tcod_input(rangle_bracket) == '>'


def test_process_tcod_input__shift_dot_returns_ranglebracket():
    shift_dot = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('.'), shift=True)
    assert input_handling.process_tcod_input(shift_dot) == '>'



# <
# ,
# .
# \
# Numpad keys
# Arrow keys
# Numbers?
