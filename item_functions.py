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
