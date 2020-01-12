import pytest
from ..src import item_functions
from ..src import player


@pytest.fixture
def hero():
    return player.get_hero()


def test_heal__using_dict_for_kwargs(hero):
    # entity comes from args[0]
    kwargs = {'amt':40}
    assert item_functions.heal(hero, **kwargs)  # Should return something


def test_heal__no_entity_raises_exception():
    # entity comes from args[0]
    with pytest.raises(IndexError):
        item_functions.heal(amt=40)


def test_heal__no_amt_raises_exception(hero):
    with pytest.raises(KeyError):
        item_functions.heal(hero)


def test_heal__at_max_hp__consumed_is_False(hero):
    assert hero.fighter.hp == hero.fighter.max_hp
    results = item_functions.heal(hero, amt=40)
    assert results[0]['consumed'] is False


def test_heal__at_max_hp__cancel_inv_is_True(hero):
    assert hero.fighter.hp == hero.fighter.max_hp
    results = item_functions.heal(hero, amt=40)
    assert results[0]['cancel_inv']


def test_heal__at_max_hp__msg(hero):
    assert hero.fighter.hp == hero.fighter.max_hp
    results = item_functions.heal(hero, amt=40)
    assert results[0]['msg'] == 'You are already at full health'


def test_heal__below_max_hp__consumed_is_True(hero):
    hero.fighter.hp = 5
    results = item_functions.heal(hero, amt=40)
    assert results[0]['consumed']


def test_heal__below_max_hp__msg(hero):
    hero.fighter.hp = 5
    results = item_functions.heal(hero, amt=40)
    assert results[0]['msg'] == 'You drink the healing potion and start to feel better!'


# def cast_lightning(*args, **kwargs):
    # entity comes from args[0]
    # kwargs: entities
    # kwargs: fov_map
    # kwargs: dmg
    # kwargs: max_range

    # if successful cast:
        # Results returns 'consumed': True,
        # Results returns 'target': target,
        # Results returns 'msg': 'A lighting bolt strikes the {} with a loud thunder! The damage is {}'.format(target.name, dmg)
        # (target.fighter.take_dmg(dmg)) is called

    # if not successful:
        # Results returns 'consumed': False,
        # Results returns 'target': None,
        # Results returns 'msg': 'No enemy is close enough to strike.'



# def cast_fireball(*args, **kwargs):
    # kwargs: entities
    # kwargs: fov_map
    # kwargs: dmg
    # kwargs: radius
    # kwargs: target_x
    # kwargs: target_y

    # if outside FOV:
        # 'consumed': False,
        # 'msg': 'You cannot target a tile outside your field of view.'

    # if successful:
        # 'consumed': True,
        # 'msg': 'The fireball explodes, burning everything within {} tiles!'.format(radius)

    # if successful and damages enemies:
            # results.append({'msg': 'The {} gets burned for {} hit points!'.format(entity.name, dmg) })
            # results.extend(entity.fighter.take_dmg(dmg))

    # Also check that hero gets damaged if too close



# def cast_confuse(*args, **kwargs):
    # kwargs: entities
    # kwargs: fov_map
    # kwargs: target_x
    # kwargs: target_y

    # if outside FOV:
        # 'consumed': False,
        # 'msg': 'You cannot target a tile outside your field of view.'

    # if successful:
        # enemy ai is replaced with ConfusedBehavior
        # 'consumed': True,
        # 'msg': 'The eyes of the {} look vacant, as he starts to stumble around!'.format(entity.name)

    # if unsuccess:
        # 'consumed': False,
        # 'msg': 'There is no targetable enemy at that location.'
