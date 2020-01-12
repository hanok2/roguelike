import pytest
from pytest_mock import mocker
from ..src import factory
from ..src import fov
from ..src import item_functions
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
        (2, 3),
        (9, 9)
    ]
    orcs = [factory.mk_entity('orc', x, y) for x, y in orc_coordinates]
    m.entities.extend(orcs)

    return m



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

def test_cast_lightning__no_entity_raises_exception():
    kwargs = {'entities':[], 'fov_map':None, 'dmg':10, 'max_range':3}
    with pytest.raises(IndexError):
        item_functions.cast_lightning(**kwargs)


def test_cast_lightning__no_entities_raises_exception():
    kwargs = {'fov_map':None, 'dmg':10, 'max_range':3}
    with pytest.raises(KeyError):
        item_functions.cast_lightning(hero, **kwargs)


def test_cast_lightning__no_fov_map_raises_exception():
    kwargs = {'entities':[], 'dmg':10, 'max_range':3}
    with pytest.raises(KeyError):
        item_functions.cast_lightning(hero, **kwargs)


def test_cast_lightning__no_dmg_raises_exception():
    kwargs = {'entities':[], 'fov_map':None, 'max_range':3}
    with pytest.raises(KeyError):
        item_functions.cast_lightning(hero, **kwargs)


def test_cast_lightning__no_max_range_raises_exception():
    kwargs = {'entities':[], 'fov_map':None, 'dmg':10}
    with pytest.raises(KeyError):
        item_functions.cast_lightning(hero, **kwargs)


    # Need empty map, hero, and entities that are in and out of FOV
    # kwargs = {'entities':[], 'fov_map':None, 'dmg':10, 'max_range':3}

    # if successful cast:

def test_cast_lightning__valid_target_returns_consumed_True(test_map, hero):
    test_map.entities.append(hero)
    fov_map = fov.initialize_fov(test_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=3)
    kwargs = {'entities':test_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_functions.cast_lightning(hero, **kwargs)
    assert results[0]['consumed']


def test_cast_lightning__valid_target_returns_entity(test_map, hero):
    test_map.entities.append(hero)
    fov_map = fov.initialize_fov(test_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=3)
    kwargs = {'entities':test_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_functions.cast_lightning(hero, **kwargs)
    assert results[0]['target'].x == 1
    assert results[0]['target'].y == 0


def test_cast_lightning__valid_target_returns_msg(test_map, hero):
    test_map.entities.append(hero)
    fov_map = fov.initialize_fov(test_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=3)
    kwargs = {'entities':test_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_functions.cast_lightning(hero, **kwargs)
    assert results[0]['msg'] == 'A lighting bolt strikes the Orc with a loud thunder! The damage is 10'


def test_cast_lightning__valid_target__take_dmg_called(mocker, test_map, hero):
    test_map.entities.append(hero)
    fov_map = fov.initialize_fov(test_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=3)
    kwargs = {'entities':test_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    # todo: Better way to do this...
    orc = test_map.entities[0]

    mocker.patch.object(orc.fighter, 'take_dmg')

    item_functions.cast_lightning(hero, **kwargs)

    orc.fighter.take_dmg.assert_called_once_with(10)


def test_cast_lightning__no_target_returns_consumed_False(open_map, hero):
    open_map.entities.append(hero)
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=3)
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_functions.cast_lightning(hero, **kwargs)
    assert results[0]['consumed'] is False


def test_cast_lightning__no_target_returns_target_None(open_map, hero):
    open_map.entities.append(hero)
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=3)
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_functions.cast_lightning(hero, **kwargs)
    assert results[0]['target'] is None


def test_cast_lightning__no_target_returns_msg(open_map, hero):
    open_map.entities.append(hero)
    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=3)
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_functions.cast_lightning(hero, **kwargs)
    assert results[0]['msg'] == 'No enemy is close enough to strike.'


def test_cast_lightning__out_of_range__consumed_False(open_map, hero):
    orc = factory.mk_entity('orc', 4, 4)
    open_map.entities.append(hero)
    open_map.entities.append(orc)

    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_functions.cast_lightning(hero, **kwargs)
    assert results[0]['consumed'] is False


def test_cast_lightning__out_of_range__target_None(open_map, hero):
    orc = factory.mk_entity('orc', 4, 4)
    open_map.entities.append(hero)
    open_map.entities.append(orc)

    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_functions.cast_lightning(hero, **kwargs)
    assert results[0]['target'] is None


def test_cast_lightning__out_of_range__returns_msg(open_map, hero):
    orc = factory.mk_entity('orc', 4, 4)
    open_map.entities.append(hero)
    open_map.entities.append(orc)

    fov_map = fov.initialize_fov(open_map)
    fov.recompute_fov(fov_map, x=0, y=0, radius=5)
    kwargs = {'entities':open_map.entities, 'fov_map':fov_map, 'dmg':10, 'max_range':3}

    results = item_functions.cast_lightning(hero, **kwargs)
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
