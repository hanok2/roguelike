from .components import ConfusedBehavior

# Is *args really necessary for these?
# If the entity is expected in args[0] is there a better way?
#   can we pass the entity in kwargs instead?


def heal(*args, **kwargs):
    # Entity is first arg in args
    # 'amt' is required in kwargs

    entity = args[0]
    amt = kwargs.get('amt')
    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({
            'consumed': False,
            'cancel_inv': True,
            'msg': 'You are already at full health'
        })
    else:
        entity.fighter.heal(amt)
        results.append({
            'consumed': True,
            'msg': 'You drink the healing potion and start to feel better!'
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

    # Export to map? Instead of importing entities/fov_map, just import game_map
    for entity in entities:
        if entity.fighter and entity != caster and fov_map.fov[entity.y, entity.x]:
            distance = caster.distance_to(entity)

            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append({
            'consumed': True,
            'target': target,
            'msg': 'A lighting bolt strikes the {} with a loud thunder! The damage is {}'.format(target.name, dmg)
        })
        results.extend(target.fighter.take_dmg(dmg))

    else:
        results.append({
            'consumed': False,
            'target': None,
            'msg': 'No enemy is close enough to strike.'
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

    if not fov_map.fov[target_y, target_x]:
        results.append({
            'consumed': False,
            'msg': 'You cannot target a tile outside your field of view.'
        })
        return results

    results.append({
        'consumed': True,
        'msg': 'The fireball explodes, burning everything within {} tiles!'.format(radius)
    })

    for entity in entities:
        if entity.distance(target_x, target_y) <= radius and entity.fighter:
            results.append({'msg': 'The {} gets burned for {} hit points!'.format(entity.name, dmg)})
            results.extend(entity.fighter.take_dmg(dmg))

    return results


def cast_confuse(*args, **kwargs):
    # Convert to [] notation
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not fov_map.fov[target_y, target_x]:
        results.append({
            'consumed': False,
            'msg': 'You cannot target a tile outside your field of view.'
        })
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            confused_ai = ConfusedBehavior(prev_ai=entity.ai, num_turns=10)

            confused_ai.owner = entity
            entity.ai = confused_ai

            results.append({
                'consumed': True,
                'msg': 'The eyes of the {} look vacant, as he starts to stumble around!'.format(entity.name)
            })
            break
    else:
        results.append({
            'consumed': False,
            'msg': 'There is no targetable enemy at that location.'
        })

    return results
