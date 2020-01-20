from ..src import actionqueue


""" Tests for ActionQueue """


def test_ActionQueue_init():
    q = actionqueue.ActionQueue()
    assert q.queue == []


def test_ActionQueue_len():
    q = actionqueue.ActionQueue()
    assert len(q) == 0


def test_ActionQueue_put():
    q = actionqueue.ActionQueue()
    q.put(1)
    q.put(2)
    assert q.queue == [1, 2]


def test_ActionQueue_get():
    q = actionqueue.ActionQueue()
    q.put(1)
    q.put(2)
    result = q.get()
    assert result == 1


def test_ActionQueue_empty__empty_returns_True():
    q = actionqueue.ActionQueue()
    assert q.empty()


def test_ActionQueue_empty__populated_returns_False():
    q = actionqueue.ActionQueue()
    q.put(1)
    assert not q.empty()


# def test_ActionQueue_get__empty_queue():
# def test_ActionQueue_iterator?():
# def test_ActionQueue_cannot_manipulate_the_queue():

