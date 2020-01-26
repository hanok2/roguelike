class Tile(object):
    """ A tile on a map."""
    def __init__(self, blocks, block_sight=None):
        if not isinstance(blocks, bool):
            raise ValueError('blocks must be True or False!')

        self.blocks = blocks

        # By default, if a tile is blockd, it also blocks sight.
        if block_sight is None:
            block_sight = blocks

        self.block_sight = block_sight

        self.explored = False
