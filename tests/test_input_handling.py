import pytest
import tcod
from pytest_mock import mocker
from ..src import input_handling
from ..src import config

States = config.States


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


""" Tests for handle_hero_turn_keys """


def test_handle_hero_turn_keys__stair_down():
    result = input_handling.handle_hero_turn_keys('>')
    assert result == {'stair_down': True}


def test_handle_hero_turn_keys__stair_up():
    result = input_handling.handle_hero_turn_keys('<')
    assert result == {'stair_up': True}


def test_handle_hero_turn_keys__pickup():
    result = input_handling.handle_hero_turn_keys(',')
    assert result == {'pickup': True}


def test_handle_hero_turn_keys__inventory():
    result = input_handling.handle_hero_turn_keys('i')
    assert result == {'show_inv': True}


def test_handle_hero_turn_keys__drop_inventory():
    result = input_handling.handle_hero_turn_keys('d')
    assert result == {'drop_inv': True}


def test_handle_hero_turn_keys__char_screen():
    result = input_handling.handle_hero_turn_keys('^x')
    assert result == {'show_char_scr': True}


def test_handle_hero_turn_keys__wait():
    result = input_handling.handle_hero_turn_keys('.')
    assert result == {'wait': True}


def test_handle_hero_turn_keys__move_N():
    result = input_handling.handle_hero_turn_keys('k')
    assert result == {'move': (0, -1)}


def test_handle_hero_turn_keys__move_S():
    result = input_handling.handle_hero_turn_keys('j')
    assert result == {'move': (0, 1)}


def test_handle_hero_turn_keys__move_E():
    result = input_handling.handle_hero_turn_keys('l')
    assert result == {'move': (1, 0)}


def test_handle_hero_turn_keys__move_W():
    result = input_handling.handle_hero_turn_keys('h')
    assert result == {'move': (-1, 0)}


def test_handle_hero_turn_keys__move_NE():
    result = input_handling.handle_hero_turn_keys('u')
    assert result == {'move': (1, -1)}


def test_handle_hero_turn_keys__move_NW():
    result = input_handling.handle_hero_turn_keys('y')
    assert result == {'move': (-1, -1)}


def test_handle_hero_turn_keys__move_SE():
    result = input_handling.handle_hero_turn_keys('n')
    assert result == {'move': (1, 1)}


def test_handle_hero_turn_keys__move_SW():
    result = input_handling.handle_hero_turn_keys('b')
    assert result == {'move': (-1, 1)}


def test_handle_hero_turn_keys__fullscreen():
    result = input_handling.handle_hero_turn_keys('!a')
    assert result == {'full_scr': True}


def test_handle_hero_turn_keys__escape():
    result = input_handling.handle_hero_turn_keys('esc')
    assert result == {'exit': True}


@pytest.mark.skip(reason='look into later')
def test_handle_hero_turn_keys__nothing_press():
    result = input_handling.handle_hero_turn_keys(None)
    assert result == {}


""" Tests for handle_hero_dead_keys """


def test_handle_hero_dead_keys__inventory():
    result = input_handling.handle_hero_dead_keys('i')
    assert result == {'show_inv': True}


@pytest.mark.skip(reason='Fix Alt-Enter on tcod handling first')
def test_handle_hero_dead_keys__fullscreen():
    result = input_handling.handle_hero_dead_keys('!a')
    assert result == {'full_scr': True}


def test_handle_hero_dead_keys__char_scr():
    result = input_handling.handle_hero_dead_keys('^x')
    assert result == {'show_char_scr': True}


def test_handle_hero_dead_keys__esc():
    result = input_handling.handle_hero_dead_keys('esc')
    assert result == {'exit': True}

@pytest.mark.skip(reason='look into later')
def test_handle_hero_dead_keys__nothing_press():
    result = input_handling.handle_hero_dead_keys(None)
    assert result == {}


""" Tests for handle_hero_dead_keys """


# def test_handle_inv_keys__A_equals_0():
# def test_handle_inv_keys__Z_equals_26():


def test_handle_inv_keys__a_equals_0():
    result = input_handling.handle_inv_keys('a')
    assert result == {'inv_index': 0}


def test_handle_inv_keys__z_equals_26():
    result = input_handling.handle_inv_keys('z')
    assert result == {'inv_index': 25}


@pytest.mark.skip(reason='Fix Alt-Enter on tcod handling first')
def test_handle_inv_keys__fullscreen():
    result = input_handling.handle_inv_keys('alt-enter')
    assert result == {'full_scr': True}


def test_handle_inv_keys__esc():
    result = input_handling.handle_inv_keys('esc')
    assert result == {'exit': True}


@pytest.mark.skip(reason='look into later')
def test_handle_inv_keys__nothing_press():
    result = input_handling.handle_inv_keys(None)
    assert result == {}


""" Tests for test_handle_main_menu(key) """


def test_handle_main_menu__new_game():
    result = input_handling.handle_main_menu('n')
    assert result == {'new_game': True}


def test_handle_main_menu__load_game():
    result = input_handling.handle_main_menu('c')
    assert result == {'load_game': True}


def test_handle_main_menu__options():
    result = input_handling.handle_main_menu('o')
    assert result == {'options': True}


def test_handle_main_menu__exit():
    result = input_handling.handle_main_menu('q')
    assert result == {'exit': True}


@pytest.mark.skip(reason='look into later')
def test_handle_main_menu__esc__continues_game():
    result = input_handling.handle_main_menu('esc')
    assert result == {'exit': True}


@pytest.mark.skip(reason='look into later')
def test_handle_main_menu__not_valid_key():
    result = input_handling.handle_main_menu(None)
    assert result == {}


""" Tests for test_handle_targeting_keys(key)"""


def test_handle_targeting_keys__esc__exits_targeting():
    result = input_handling.handle_targeting_keys('esc')
    assert result == {'exit': True}


def test_handle_targeting_keys__non_valid():
    result = input_handling.handle_targeting_keys('z')
    assert result == {}

""" Tests for test_handle_lvl_up_menu(key)"""


def test_handle_lvl_up_menu__pick_constitution():
    result = input_handling.handle_lvl_up_menu('c')
    assert result == {'lvl_up': 'hp'}


def test_handle_lvl_up_menu__pick_strength():
    result = input_handling.handle_lvl_up_menu('s')
    assert result == {'lvl_up': 'str'}


def test_handle_lvl_up_menu__pick_defense():
    result = input_handling.handle_lvl_up_menu('d')
    assert result == {'lvl_up': 'def'}


def test_handle_lvl_up_menu__invalid():
    result = input_handling.handle_lvl_up_menu('z')
    assert result == {}


""" Tests for test_handle_char_scr(key):"""


def test_handle_char_scr__esc__exits():
    result = input_handling.handle_char_scr('esc')
    assert result == {'exit': True}


def test_handle_char_scr__invalid():
    result = input_handling.handle_char_scr('z')
    assert result == {}


""" Tests for process_tcod_input"""


def test_process_tcod_input__a_returns_a():
    a_key = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('a'))
    assert  input_handling.process_tcod_input(a_key) == 'a'


def test_process_tcod_input__A_returns_A():
    A_key = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('A'))
    assert input_handling.process_tcod_input(A_key) == 'A'


def test_process_tcod_input__1_returns_1():
    one_key = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('1'))
    assert input_handling.process_tcod_input(one_key) == '1'


def test_process_tcod_input__control_x_returns_carrot_x():
    ctrl_x = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('x'), lctrl=True)
    assert input_handling.process_tcod_input(ctrl_x) == '^x'


def test_process_tcod_input__ESC_returns_esc():
    esc_key = tcod.Key(pressed=True, vk=tcod.KEY_ESCAPE, c=ord('\x1b'))
    assert input_handling.process_tcod_input(esc_key) == 'esc'


def test_process_tcod_input__comma_returns_comma():
    comma = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord(','))
    assert input_handling.process_tcod_input(comma) == ','


def test_process_tcod_input__dot_returns_dot():
    dot = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('.'))
    assert input_handling.process_tcod_input(dot) == '.'


def test_process_tcod_input_question():
    question = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('?'))
    assert input_handling.process_tcod_input(question) == '?'


def test_process_tcod_input_backslash():
    backslash = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('\\'))
    assert input_handling.process_tcod_input(backslash) == '\\'


def test_process_tcod_input_ranglebracket():
    rangle_bracket = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('>'))
    assert input_handling.process_tcod_input(rangle_bracket) == '>'


def test_process_tcod_input__shift_dot_returns_ranglebracket():
    shift_dot = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('.'), shift=True)
    assert input_handling.process_tcod_input(shift_dot) == '>'


def test_process_tcod_input_langlebracket():
    langle_bracket = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('<'))
    assert input_handling.process_tcod_input(langle_bracket) == '<'


def test_process_tcod_input__shift_comma_returns_langlebracket():
    shift_comma = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord(','), shift=True)
    assert input_handling.process_tcod_input(shift_comma) == '<'


def test_process_tcod_input__up_arrow_returns_k():
    up_arrow = tcod.Key(pressed=True, vk=tcod.KEY_UP)
    assert input_handling.process_tcod_input(up_arrow) == 'k'


def test_process_tcod_input__down_arrow_returns_j():
    down_arrow = tcod.Key(pressed=True, vk=tcod.KEY_DOWN)
    assert input_handling.process_tcod_input(down_arrow) == 'j'


def test_process_tcod_input__left_arrow_returns_h():
    left_arrow = tcod.Key(pressed=True, vk=tcod.KEY_LEFT)
    assert input_handling.process_tcod_input(left_arrow) == 'h'


def test_process_tcod_input__right_arrow_returns_l():
    right_arrow = tcod.Key(pressed=True, vk=tcod.KEY_RIGHT)
    assert input_handling.process_tcod_input(right_arrow) == 'l'


def test_process_tcod_input__numpad1__returns_b():
    numpad1 = tcod.Key(pressed=True, vk=tcod.KEY_KP1)
    assert input_handling.process_tcod_input(numpad1) == 'b'


def test_process_tcod_input__numpad2__returns_j():
    numpad2 = tcod.Key(pressed=True, vk=tcod.KEY_KP2)
    assert input_handling.process_tcod_input(numpad2) == 'j'


def test_process_tcod_input__numpad3__returns_n():
    numpad3 = tcod.Key(pressed=True, vk=tcod.KEY_KP3)
    assert input_handling.process_tcod_input(numpad3) == 'n'


def test_process_tcod_input__numpad4__returns_h():
    numpad4 = tcod.Key(pressed=True, vk=tcod.KEY_KP4)
    assert input_handling.process_tcod_input(numpad4) == 'h'


def test_process_tcod_input__numpad5__returns_dot():
    numpad5 = tcod.Key(pressed=True, vk=tcod.KEY_KP5)
    assert input_handling.process_tcod_input(numpad5) == '.'


def test_process_tcod_input__numpad6__returns_l():
    numpad6 = tcod.Key(pressed=True, vk=tcod.KEY_KP6)
    assert input_handling.process_tcod_input(numpad6) == 'l'


def test_process_tcod_input__numpad7__returns_y():
    numpad7 = tcod.Key(pressed=True, vk=tcod.KEY_KP7)
    assert input_handling.process_tcod_input(numpad7) == 'y'


def test_process_tcod_input__numpad8__returns_k():
    numpad8 = tcod.Key(pressed=True, vk=tcod.KEY_KP8)
    assert input_handling.process_tcod_input(numpad8) == 'k'


def test_process_tcod_input__numpad9__returns_u():
    numpad9 = tcod.Key(pressed=True, vk=tcod.KEY_KP9)
    assert input_handling.process_tcod_input(numpad9) == 'u'


""" Tests for test_handle_mouse()"""


def test_handle_mouse__rclick():
    rclick = tcod.Mouse(x=202, y=116, cx=16, cy=9, rbutton_pressed=True)
    result = input_handling.handle_mouse(rclick)

    # Test cx/cy because that is the cell the cursor is over in the console
    assert result == {'r_click': (16, 9)}


def test_handle_mouse__lclick():
    mclick = tcod.Mouse(x=202, y=116, cx=16, cy=9, lbutton_pressed=True)
    result = input_handling.handle_mouse(mclick)

    # Test cx/cy because that is the cell the cursor is over in the console
    assert result == {'l_click': (16, 9)}


def test_handle_mouse__mclick():
    mclick = tcod.Mouse(x=191, y=102, cx=15, cy=8, mbutton_pressed=True)
    result = input_handling.handle_mouse(mclick)

    # Test cx/cy because that is the cell the cursor is over in the console
    assert result == {'m_click': (15, 8)}
