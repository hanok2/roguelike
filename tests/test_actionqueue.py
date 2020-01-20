from ..src import actionqueue


""" Tests for ActionQueue """


def test_ActionQueue_init():
    q = actionqueue.ActionQueue()
    assert q.queue == []


def test_ActionQueue_len():
    q = actionqueue.ActionQueue()
    assert len(q) == 0
