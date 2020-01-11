class Tile(object):
    """ A tile on a map."""
    def __init__(self, blocked, block_sight=None):
        if not isinstance(blocked, bool):
            raise ValueError('blocked must be True or False!')

        self.blocked = blocked

        # By default, if a tile is blockd, it also blocks sight.
        if block_sight is None:
            block_sight = blocked

        self.block_sight = block_sight

        self.explored = False
