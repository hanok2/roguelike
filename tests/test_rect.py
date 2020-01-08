""" Tests for rect.py """

import pytest
from ..src import rect

def test_Rect_init():
    r = rect.Rect(0, 0, 3, 3)
    assert r


def test_Rect_init_x2():
    r = rect.Rect(0, 0, 5, 10)
    x2 = 5
    assert r.x2 == x2


def test_Rect_init_y2():
    r = rect.Rect(0, 0, 5, 10)
    y2 = 10
    assert r.y2 == y2


def test_Rect_init_negative_x_raises_ValueError():
    with pytest.raises(ValueError):
        rect.Rect(-2, 2, 2, 2)


def test_Rect_init_negative_y_raises_ValueError():
    with pytest.raises(ValueError):
        rect.Rect(2, -2, 2, 2)


def test_Rect_init_low_w_raises_ValueError():
    with pytest.raises(ValueError):
        rect.Rect(2, 2, 2, 3)


def test_Rect_init_low_h_raises_ValueError():
    with pytest.raises(ValueError):
        rect.Rect(2, 2, 3, 2)


def test_Rect_center():
    r = rect.Rect(0, 0, 3, 3)
    center = (1, 1)
    assert r.center() == center


def test_Rect_intersect_no_intersect_returns_False():
    r1 = rect.Rect(0, 0, 3, 3)
    r2 = rect.Rect(10, 10, 3, 3)
    assert r1.intersect(r2) is False
    assert r2.intersect(r1) is False


def test_Rect_intersect_both_rects_intersect_returns_True():
    r1 = rect.Rect(0, 0, 3, 3)
    r2 = rect.Rect(1, 1, 3, 3)
    assert r1.intersect(r2)
    assert r2.intersect(r1)


def test_Rect_within__valid_returns_True():
    r1 = rect.Rect(0, 0, 3, 3)
    x, y = 0, 0
    assert r1.within(x, y)


def test_Rect_within__invalid_returns_False():
    r1 = rect.Rect(0, 0, 3, 3)
    x, y = 3, 3
    assert r1.within(x, y) is False
