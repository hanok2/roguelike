from enum import Enum

class States(Enum):
    # Note: In Python 3.6+, we can use "auto" feature to auto-increment
    HERO_TURN = 1
    WORLD_TURN = 2
    HERO_DEAD = 3
    SHOW_INV = 4
    DROP_INV = 5
    TARGETING = 6
    LEVEL_UP = 7
    SHOW_STATS = 8
