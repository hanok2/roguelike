import pytest
from . import random_utils

CHOICE_DICT = {'a': 1, 'b': 2, 'c': 3}


def test_rnd_choice_index_make_sure_result_is_in_bounds():
    chances = CHOICE_DICT.values()
    result = random_utils.rnd_choice_index(chances)
    assert result >= 0 and result < len(CHOICE_DICT)


def test_rnd_choice_index_empty_list_raises_ValueError():
    chances = []
    with pytest.raises(ValueError):
        random_utils.rnd_choice_index(chances)


def test_rnd_choice_from_dict():
    result = random_utils.rnd_choice_from_dict(CHOICE_DICT)
    assert result in CHOICE_DICT.keys()


# Table for testing from_dungeon_lvl
TABLE1 = [
    # [value, level]
    [2, 1],
    [3, 4],
    [5, 6]
]

def test_from_dungeon_lvl_negative_level_raises_Exception():
    with pytest.raises(ValueError):
        random_utils.from_dungeon_lvl(table=TABLE1, dungeon_lvl=-1)

def test_from_dungeon_lvl_valid_level():
    result = random_utils.from_dungeon_lvl(table=TABLE1, dungeon_lvl=1)
    assert result == 2


def test_from_dungeon_lvl_level_is_less_than_listed_returns0():
    result = random_utils.from_dungeon_lvl(table=TABLE1, dungeon_lvl=0)
    assert result == 0


def test_from_dungeon_lvl_level_is_more_than_listed_returns_higher_lvl_val():
    result = random_utils.from_dungeon_lvl(table=TABLE1, dungeon_lvl=7)
    assert result == 5
