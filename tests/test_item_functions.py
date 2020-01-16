import pytest
from pytest_mock import mocker
from ..src import components
from ..src import factory
from ..src import fov
from ..src import item_funcs
from ..src import maps
from ..src import player
from ..src import tile

@pytest.fixture
def hero():
    return player.get_hero()


@pytest.fixture
def open_map():
    # todo: When we revamp map - remove this fixture!!!!!!!!!!!!!!!!!!!!!!!!
    m = maps.Map(10, 10)
    m.tiles = [[tile.Tile(False) for y in range(10)] for x in range(10)]
    return m


@pytest.fixture
def test_map():
    # todo: When we revamp map - revise this fixture!!!!!!!!!!!!!!!!!!!!!!!!
    m = maps.Map(10, 10)
    # All open
    m.tiles = [[tile.Tile(False) for y in range(10)] for x in range(10)]
    orc_coordinates = [
        (1, 0), (3, 0), (5, 0),
        (2, 1),
        (1, 2), (2, 2), (3, 2),
        (2, 3), (3, 3),
        (9, 9)
    ]
    orcs = [factory.mk_entity('orc', x, y) for x, y in orc_coordinates]
    m.entities.extend(orcs)

    return m


""" Tests for heal() """

def test_heal__using_dict_for_kwargs(hero):
    # entity comes from args[0]
    kwargs = {'amt':40}
    assert item_funcs.heal(hero, **kwargs)  # Should return something


def test_heal__no_entity_raises_exception():
    # entity comes from args[0]
    with pytest.raises(IndexError):
        item_funcs.heal(amt=40)


def test_heal__no_amt_raises_exception(hero):
    with pytest.raises(KeyError):
        item_funcs.heal(hero)


def test_heal__at_max_hp__consumed_is_False(hero):
    assert hero.fighter.hp == hero.fighter.max_hp
    results = item_funcs.heal(hero, amt=40)
    assert results[0]['consumed'] is False


def test_heal__at_max_hp__cancel_inv_is_True(hero):
    assert hero.fighter.hp == hero.fighter.max_hp
    results = item_funcs.heal(hero, amt=40)
    assert results[0]['cancel_inv']


def test_heal__at_max_hp__msg(hero):
    assert hero.fighter.hp == hero.fighter.max_hp
    results = item_funcs.heal(hero, amt=40)
    assert results[0]['msg'] == 'You are already at full health'


def test_heal__below_max_hp__consumed_is_True(hero):
    hero.fighter.hp = 5
    results = item_funcs.heal(hero, amt=40)
    assert results[0]['consumed']


def test_heal__below_max_hp__msg(hero):
    hero.fighter.hp = 5
    results = item_funcs.heal(hero, amt=40)
    assert results[0]['msg'] == 'You drink the healing potion and start to feel better!'


""" Tests for cast_lightning() """


def test_cast_lightning__no_entity_raises_exception():
    kwargs = {'entities':[], 'fov_map':None, 'dmg':10, 'max_range':3}
    with pytest.raises(IndexError):
        item_funcs.cast_lightning(**kwargs)


def test_cast_lightning__no_entities_raises_exception():
    kwargs = {'fov_map':None, 'dmg':10, 'max_range':3}
    with pytest.raises(KeyError):
        item_funcs.cast_lightning(hero, **kwargs)


def test_cast_lightning__no_fov_map_raises_exception():
    kwargs = {'entities':[], 'dmg':10, 'max_range':3}
    with pytest.raises(KeyError):
        item_funcs.cast_lightning(hero, **kwargs)


def test_cast_lightning__no_dmg_raises_exception():
    kwargs = {'entities':[], 'fov_map':None, 'max_range':3}
    with pytest.raises(KeyError):
        item_funcs.cast_lightning(hero, **kwargs)


def test_cast_lightning__no_max_range_raises_exception():
    kwargs = {'entities':[], 'fov_map':None, 'dmg':10}
    with pytest.raises(KeyError):
        item_funcs.cast_lightning(hero, **kwargs)


    # Need empty map, hero, and entities that are in and out of FOV
    # kwargs = {'entities':[], 'fov_map':None, 'dmg':10, 'max_range':3}

    # if successful cast:

def test_cast_lightning__valid_target_returns_consumed_True(test_map, hero):
    test_map.entities.append(hero)
    fov_map = fov.initialize_fov(test_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=3)
    kwargs = {'entities':test_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_funcs.cast_lightning(hero, **kwargs)
    assert results[0]['consumed']


def test_cast_lightning__valid_target_returns_entity(test_map, hero):
    test_map.entities.append(hero)
    fov_map = fov.initialize_fov(test_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=3)
    kwargs = {'entities':test_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_funcs.cast_lightning(hero, **kwargs)
    assert results[0]['target'].x == 1
    assert results[0]['target'].y == 0


def test_cast_lightning__valid_target_returns_msg(test_map, hero):
    test_map.entities.append(hero)
    fov_map = fov.initialize_fov(test_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=3)
    kwargs = {'entities':test_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_funcs.cast_lightning(hero, **kwargs)
    assert results[0]['msg'] == 'A lighting bolt strikes the Orc with a loud thunder! The damage is 10'


def test_cast_lightning__valid_target__take_dmg_called(mocker, test_map, hero):
    test_map.entities.append(hero)
    fov_map = fov.initialize_fov(test_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=3)
    kwargs = {'entities':test_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    # todo: Better way to do this...
    orc = test_map.entities[0]

    mocker.patch.object(orc.fighter, 'take_dmg')

    item_funcs.cast_lightning(hero, **kwargs)

    orc.fighter.take_dmg.assert_called_once_with(10)


def test_cast_lightning__no_target_returns_consumed_False(open_map, hero):
    open_map.entities.append(hero)
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=3)
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_funcs.cast_lightning(hero, **kwargs)
    assert results[0]['consumed'] is False


def test_cast_lightning__no_target_returns_target_None(open_map, hero):
    open_map.entities.append(hero)
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=3)
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_funcs.cast_lightning(hero, **kwargs)
    assert results[0]['target'] is None


def test_cast_lightning__no_target_returns_msg(open_map, hero):
    open_map.entities.append(hero)
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=3)
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_funcs.cast_lightning(hero, **kwargs)
    assert results[0]['msg'] == 'No enemy is close enough to strike.'


def test_cast_lightning__out_of_range__consumed_False(open_map, hero):
    orc = factory.mk_entity('orc', 4, 4)
    open_map.entities.append(hero)
    open_map.entities.append(orc)

    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_funcs.cast_lightning(hero, **kwargs)
    assert results[0]['consumed'] is False


def test_cast_lightning__out_of_range__target_None(open_map, hero):
    orc = factory.mk_entity('orc', 4, 4)
    open_map.entities.append(hero)
    open_map.entities.append(orc)

    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_funcs.cast_lightning(hero, **kwargs)
    assert results[0]['target'] is None


def test_cast_lightning__out_of_range__returns_msg(open_map, hero):
    orc = factory.mk_entity('orc', 4, 4)
    open_map.entities.append(hero)
    open_map.entities.append(orc)

    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_funcs.cast_lightning(hero, **kwargs)
    assert results[0]['msg'] == 'No enemy is close enough to strike.'


@pytest.mark.skip(reason='need Boulder entity to block FOV')
def test_cast_lightning__out_of_fov__consumed_False(open_map, hero):
    pass


@pytest.mark.skip(reason='need Boulder entity to block FOV')
def test_cast_lightning__out_of_fov__target_None(open_map, hero):
    pass


@pytest.mark.skip(reason='need Boulder entity to block FOV')
def test_cast_lightning__out_of_fov__returns_msg(open_map, hero):
    pass


""" Tests for cast_fireball() """


def test_cast_fireball__no_entities_raises_exception():
    kwargs = {'fov_map':None, 'dmg':10, 'radius':3, 'target_x': 0, 'target_y': 0}
    with pytest.raises(KeyError):
        item_funcs.cast_fireball(**kwargs)


def test_cast_fireball__no_fov_map_raises_exception():
    kwargs = {'entities':[], 'dmg':10, 'radius':3, 'target_x': 0, 'target_y': 0}
    with pytest.raises(KeyError):
        item_funcs.cast_fireball(**kwargs)


def test_cast_fireball__no_dmg_raises_exception():
    kwargs = {'entities':[], 'fov_map':None, 'radius':3, 'target_x': 0, 'target_y': 0}
    with pytest.raises(KeyError):
        item_funcs.cast_fireball(**kwargs)


def test_cast_fireball__no_radius_raises_exception():
    kwargs = {'entities':[], 'fov_map':None, 'dmg':10, 'target_x': 0, 'target_y': 0}
    with pytest.raises(KeyError):
        item_funcs.cast_fireball(**kwargs)


def test_cast_fireball__no_target_x_raises_exception():
    kwargs = {'entities':[], 'fov_map':None, 'dmg':10, 'radius':3, 'target_y': 0}
    with pytest.raises(KeyError):
        item_funcs.cast_fireball(**kwargs)


def test_cast_fireball__no_target_y_raises_exception():
    kwargs = {'entities':[], 'fov_map':None, 'dmg':10, 'radius':3, 'target_x': 0}
    with pytest.raises(KeyError):
        item_funcs.cast_fireball(**kwargs)


def test_cast_fireball__outside_fov__consumed_False(open_map, hero):
    orc = factory.mk_entity('orc', 9, 9)
    open_map.entities.extend([hero, orc])

    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':25, 'radius':3, 'target_x': orc.x, 'target_y': orc.y}

    results = item_funcs.cast_fireball(hero, **kwargs)
    assert results[0]['consumed'] is False


def test_cast_fireball__outside_fov__msg(open_map, hero):
    orc = factory.mk_entity('orc', 9, 9)
    open_map.entities.extend([hero, orc])

    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':25, 'radius':3, 'target_x': orc.x, 'target_y': orc.y}

    results = item_funcs.cast_fireball(hero, **kwargs)
    assert results[0]['msg'] == 'You cannot target a tile outside your field of view.'


def test_cast_fireball__in_fov__consumed_True(open_map, hero):
    open_map.entities.append(hero)
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)

    radius = 3
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':25, 'radius': radius, 'target_x': 5, 'target_y': 0}

    results = item_funcs.cast_fireball(hero, **kwargs)
    assert results[0]['consumed']


def test_cast_fireball__in_fov__msg(open_map, hero):
    open_map.entities.append(hero)
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)

    radius = 3
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':25, 'radius': radius, 'target_x': 5, 'target_y': 0}

    results = item_funcs.cast_fireball(hero, **kwargs)
    assert results[0]['msg'] == 'The fireball explodes, burning everything within {} tiles!'.format(radius)


def test_cast_fireball__close_to_hero__msg(open_map, hero):
    open_map.entities.append(hero)
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)

    radius = 3
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':25, 'radius': radius, 'target_x': 1, 'target_y': 0}

    results = item_funcs.cast_fireball(hero, **kwargs)
    assert results[0]['msg'] == 'The fireball explodes, burning everything within {} tiles!'.format(radius)
    assert results[1]['msg'] == 'The Player gets burned for 25 hit points!'


def test_cast_fireball__close_to_hero__take_dmg_called(mocker, open_map, hero):
    open_map.entities.append(hero)
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)

    radius = 3
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':25, 'radius': radius, 'target_x': 1, 'target_y': 0}

    mocker.patch.object(hero.fighter, 'take_dmg')

    item_funcs.cast_fireball(hero, **kwargs)
    hero.fighter.take_dmg.assert_called_once_with(25)


def test_cast_fireball__orc_mob__hits_5_orcs(test_map, hero):
    test_map.entities.append(hero)
    fov_map = fov.initialize_fov(test_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=3)

    orc_xp = test_map.entities[0].fighter.xp
    radius = 1
    kwargs = {'entities':test_map.entities, 'fov_map':fov_map, 'dmg':25, 'radius': radius, 'target_x': 2, 'target_y': 2}

    results = item_funcs.cast_fireball(hero, **kwargs)
    assert len(results) == 11

    assert results[0]['msg'] == 'The fireball explodes, burning everything within {} tiles!'.format(radius)
    assert results[0]['consumed']
    assert results[1]['msg'] == 'The Orc gets burned for 25 hit points!'
    assert results[2]['dead']
    assert results[2]['xp'] == orc_xp
    assert results[3]['msg'] == 'The Orc gets burned for 25 hit points!'
    assert results[4]['dead']
    assert results[4]['xp'] == orc_xp
    assert results[5]['msg'] == 'The Orc gets burned for 25 hit points!'
    assert results[6]['dead']
    assert results[6]['xp'] == orc_xp
    assert results[7]['msg'] == 'The Orc gets burned for 25 hit points!'
    assert results[8]['dead']
    assert results[8]['xp'] == orc_xp
    assert results[9]['msg'] == 'The Orc gets burned for 25 hit points!'
    assert results[10]['dead']
    assert results[10]['xp'] == orc_xp


""" Tests for cast_confuse() """


def test_cast_confuse__no_entities_raises_exception():
    kwargs = {'fov_map':None, 'target_x':0, 'target_y':0}
    with pytest.raises(KeyError):
        item_funcs.cast_confuse(**kwargs)


def test_cast_confuse__no_fov_map_raises_exception():
    kwargs = {'entities':[], 'target_x':0, 'target_y':0}
    with pytest.raises(KeyError):
        item_funcs.cast_confuse(**kwargs)


def test_cast_confuse__no_target_x_raises_exception():
    kwargs = {'entities':[], 'fov_map':None, 'target_y':0}
    with pytest.raises(KeyError):
        item_funcs.cast_confuse(**kwargs)


def test_cast_confuse__no_target_y_raises_exception():
    kwargs = {'entities':[], 'fov_map':None, 'target_x':0}
    with pytest.raises(KeyError):
        item_funcs.cast_confuse(**kwargs)


def test_cast_confuse__outside_fov__consumed_False(open_map, hero):
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)

    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'target_x':9, 'target_y':9}
    results = item_funcs.cast_confuse(hero, **kwargs)
    assert results[0]['consumed'] is False


def test_cast_confuse__outside_fov__msg(open_map, hero):
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)

    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'target_x':9, 'target_y':9}
    results = item_funcs.cast_confuse(hero, **kwargs)
    assert results[0]['msg'] == 'You cannot target a tile outside your field of view.'


def test_cast_confuse__in_fov_but_not_entity__consumed_False(open_map, hero):
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)

    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'target_x':1, 'target_y':1}
    results = item_funcs.cast_confuse(hero, **kwargs)
    assert results[0]['consumed'] is False


def test_cast_confuse__in_fov_but_not_entity__msg(open_map, hero):
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)

    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'target_x':1, 'target_y':1}
    results = item_funcs.cast_confuse(hero, **kwargs)
    assert results[0]['msg'] == 'There is no targetable enemy at that location.'


# if successful:
    # enemy ai is replaced with ConfusedBehavior
    # 'consumed': True,
    # 'msg': 'The eyes of the {} look vacant, as he starts to stumble around!'.format(entity.name)


def test_cast_confuse__success__replaced_ai(open_map, hero):
    orc = factory.mk_entity('orc', 1, 1)
    open_map.entities.extend([hero, orc])
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)

    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'target_x':1, 'target_y':1}
    item_funcs.cast_confuse(hero, **kwargs)

    assert isinstance(orc.ai, components.ConfusedBehavior)


def test_cast_confuse__success__consumed_True(open_map, hero):
    orc = factory.mk_entity('orc', 1, 1)
    open_map.entities.extend([hero, orc])
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)

    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'target_x':1, 'target_y':1}
    results = item_funcs.cast_confuse(hero, **kwargs)

    assert results[0]['consumed']


def test_cast_confuse__success__msg(open_map, hero):
    orc = factory.mk_entity('orc', 1, 1)
    open_map.entities.extend([hero, orc])
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)

    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'target_x':1, 'target_y':1}
    results = item_funcs.cast_confuse(hero, **kwargs)

    assert results[0]['msg'] == 'The eyes of the Orc look vacant, as he starts to stumble around!'


def test_cast_confuse__on_hero__not_successful(open_map, hero):
    open_map.entities.append(hero)
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)

    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'target_x':0, 'target_y':0}
    results = item_funcs.cast_confuse(hero, **kwargs)

    assert results[0]['consumed'] is False
    assert results[0]['msg'] == 'There is no targetable enemy at that location.'
