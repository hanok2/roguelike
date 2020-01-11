from ..src import item_functions
from .test_death_functions import orc

# todo: Revise with monster generator

def test_heal(*args, **kwargs):

    # amt keyword is required
    # entity comes from args[0]

    # if hp is already at max:
        # Results return 'consumed': False,
        # Results return 'cancel_inv': True,
        # Results return 'msg': 'You are already at full health'

    # if consumed:
        # entity.fighter.heal is called
        # Results returns:'consumed': True,
        # Results returns:'msg': 'You drink the healing potion and start to feel better!'



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
