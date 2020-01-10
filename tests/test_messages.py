import pytest
from ..src import messages

char_20 = '01234567890123456789'
char_21 = '012345678901234567890'
char_40 = '0123456789012345678901234567890123456789'
char_45 = '012345678901234567890123456789012345678901234'

@pytest.fixture
def loaded_msglog():
    ml = messages.MsgLog(x=0, width=20, height=5)
    for i in range(6):
        ml.add('test{}'.format(i + 1))
    return ml


""" Tests for MsgLog """


def test_msglog_init():
    ml = messages.MsgLog(x=0, width=20, height=5)
    assert ml.messages == []
    assert ml.x == 0
    assert ml.width == 20
    assert ml.height == 5


def test_msglog_init__height_lt_1_raises_Exception():
    with pytest.raises(ValueError):
        messages.MsgLog(x=0, width=20, height=0)


def test_msglog_add__short_msg_is_in_messages():
    ml = messages.MsgLog(x=0, width=20, height=5)
    ml.add(char_20)

    assert char_20 in ml.messages
    assert len(ml.messages) == 1


def test_msglog_add__long_msg_gets_broken_up():
    ml = messages.MsgLog(x=0, width=20, height=5)
    ml.add(char_21)

    assert char_20 in ml.messages
    assert '0' in ml.messages
    assert len(ml.messages) == 2


def test_msglog_add__msgs_beyond_height(loaded_msglog):
    assert len(loaded_msglog.messages) == 6


def test_get_current_msgs__returns_most_recent(loaded_msglog):
    result = loaded_msglog.current_msgs()
    assert len(result) == loaded_msglog.height

    assert result[0] == 'test2'
    assert result[4] == 'test6'


def test_get_current_msgs__less_msgs_than_height():
    ml = messages.MsgLog(x=0, width=20, height=5)
    test_str = 'test'
    ml.add(test_str)
    result = ml.current_msgs()
    assert len(result) == 1

    assert result[0] == test_str
