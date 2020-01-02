class Tile(object):
    """ A tile on a map."""
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked

        # By default, if a tile is blockd, it also blocks sight.
        if block_sight is None:
            block_sight = blocked

        self.block_sight = block_sight
