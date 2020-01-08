from enum import Enum, auto

class States(Enum):
    # Note: In Python 3.6+, we can use "auto" feature to auto-increment
    HERO_TURN = auto()
    WORLD_TURN = auto()
    HERO_DEAD = auto()
    SHOW_INV = auto()
    DROP_INV = auto()
    TARGETING = auto()
    LEVEL_UP = auto()
    SHOW_STATS = auto()
