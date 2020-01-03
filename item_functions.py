import tcod
from game_messages import Message

def heal(*args, **kwargs):
    # Entity is first arg in args
    # 'amount' is required in kwargs

    entity = args[0]
    amt = kwargs.get('amt')
    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({
            'consumed': False,
            'msg': Message('You are already at full health', tcod.yellow)
        })
    else:
        entity.fighter.heal(amt)
        results.append({
            'consumed': True,
            'msg': Message('Your wounds start to feel better!', tcod.green)
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
            'msg': Message('A lighting bolt strikes the {} with a loud thunder! The damage is {}'.format(target.name, dmg))
        })
        results.extend(target.fighter.take_dmg(dmg))

    else:
        results.append({
            'consumed': False,
            'target': None,
            'msg': Message('No enemy is close enough to strike.', tcod.red)
        })

    return results
