from ..src import stairs


def test_Stairs_init():
    s = stairs.Stairs(floor=0)
    assert s.floor == 0
