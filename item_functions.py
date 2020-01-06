import tcod
from messages import Msg
from components import ConfusedBehavior


def heal(*args, **kwargs):
    # Entity is first arg in args
    # 'amt' is required in kwargs

    entity = args[0]
    amt = kwargs.get('amt')
    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({
            'consumed': False,
            'msg': Msg('You are already at full health', tcod.yellow)
        })
    else:
        entity.fighter.heal(amt)
        results.append({
            'consumed': True,
            'msg': Msg('Your wounds start to feel better!', tcod.green)
        })

    return results

def cast_lightning(*args, **kwargs):
    caster = args[0]  # First arg is entity
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    dmg = kwargs.get('dmg')
    max_range = kwargs.get('max_range')

    results = []

    target = None
    closest_distance = max_range + 1

    for entity in entities:
        if entity.fighter and entity != caster and tcod.map_is_in_fov(fov_map, entity.x, entity.y):
            distance = caster.distance_to(entity)

            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append({
            'consumed': True,
            'target': target,
            'msg': Msg('A lighting bolt strikes the {} with a loud thunder! The damage is {}'.format(target.name, dmg))
        })
        results.extend(target.fighter.take_dmg(dmg))

    else:
        results.append({
            'consumed': False,
            'target': None,
            'msg': Msg('No enemy is close enough to strike.', tcod.red)
        })

    return results


def cast_fireball(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    dmg = kwargs.get('dmg')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not tcod.map_is_in_fov(fov_map,target_x, target_y):
        results.append({
            'consumed': False,
            'msg': Msg('You cannot target a tile outside your field of view.', tcod.yellow)
        })
        return results

    results.append({
        'consumed': True,
        'msg': Msg('The fireball explodes, burning everything within {} tiles!'.format(radius), tcod.orange)
    })

    for entity in entities:
        if entity.distance(target_x, target_y) <= radius and entity.fighter:
            results.append({
                'msg': Msg('The {} gets burned for {} hit points!'.format(entity.name, dmg), tcod.orange)
            })
            results.extend(entity.fighter.take_dmg(dmg))

    return results


def cast_confuse(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not tcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({
            'consumed': False,
            'msg': Msg('You cannot target a tile outside your field of view.', tcod.yellow)
        })
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            confused_ai = ConfusedBehavior(prev_ai=entity.ai, num_turns=10)

            confused_ai.owner = entity
            entity.ai = confused_ai

            results.append({
                'consumed': True,
                'msg': Msg('The eyes of the {} look vacant, as he starts to stumble around!'.format(entity.name), tcod.light_green)
            })
            break
    else:
        results.append({
            'consumed': False,
            'msg': Msg('There is no targetable enemy at that location.', tcod.yellow)
        })

    return results
