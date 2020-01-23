from abc import ABC, abstractmethod
from .components import ConfusedBehavior
from . import actions
from . import stages


class Use(ABC):
    # def __init__(self):
        # super().__init__()

    @abstractmethod
    def use(self, *args, **kwargs):
        pass


# Is *args really necessary for these?
# If the entity is expected in args[0] is there a better way?
#   can we pass the entity in kwargs instead?


class UseHeal(Use):
    def use(self, *args, **kwargs):
        # Entity is first arg in args
        # 'amt' is required in kwargs

        entity = args[0]
        amt = kwargs['amt']

        if entity.fighter.hp == entity.fighter.max_hp:
            return actions.ActionResult(
                success=False,
                msg='You are already at full health',
                # 'consumed': False,
            )

        # entity.fighter.heal(amt)

        return actions.ActionResult(
            success=True,
            msg='You drink the healing potion and start to feel better!',
            alt=actions.HealAction(entity, amt)
            # 'consumed': True,
        )



class UseLightning(Use):
    def use(self, *args, **kwargs):
        caster = args[0]  # First arg is entity
        entities = kwargs['entities']
        fov_map = kwargs['fov_map']
        dmg = kwargs['dmg']
        max_range = kwargs['max_range']

        target = None
        closest_distance = max_range + 1

        # Export to map? Instead of importing entities/fov_map, just import game_map
        for entity in entities:

            # todo: Break into better boolean
            if entity.has_comp('fighter') and entity != caster and fov_map.fov[entity.y, entity.x]:

                # distance = caster.distance_to(entity)
                distance = stages.Stage.distance_between_entities(caster, entity)

                if distance < closest_distance:
                    target = entity
                    closest_distance = distance

        if target:
            return actions.ActionResult(
                success=True,
                msg='A lighting bolt strikes the {} with a loud thunder! The damage is {}'.format(target.name, dmg),
                alt=actions.TakeDmgAction(
                    attacker=caster,
                    defender=target,
                    dmg=dmg),
                # 'consumed': True,
            )

        return actions.ActionResult(
            success=False,
            msg='No enemy is close enough to strike.',
            # 'consumed': False,
        )



class UseFireball(Use):
    def use(self, *args, **kwargs):
        caster = args[0]  # First arg is entity
        entities = kwargs['entities']
        fov_map = kwargs['fov_map']
        dmg = kwargs['dmg']
        radius = kwargs['radius']
        target_x = kwargs['target_x']
        target_y = kwargs['target_y']

        if not fov_map.fov[target_y, target_x]:
            return [actions.ActionResult(
                success=False,
                msg='You cannot target a tile outside your field of view.'
            )]

        action_results = []

        action_results.append(actions.ActionResult(
            success=True,
            msg='The fireball explodes, burning everything within {} tiles!'.format(radius),
            # 'consumed': True,
        ))

        for entity in entities:
            dist_to_entity = stages.Stage.distance(entity.x, entity.y, target_x, target_y)

            if dist_to_entity <= radius and entity.has_comp('fighter'):
                action_results.append(actions.ActionResult(
                    alt=actions.TakeDmgAction(caster, entity, dmg),
                    msg='The {} gets burned for {} hit points!'.format(entity.name, dmg)
                ))

        return action_results


class UseConfuse(Use):
    def use(self, *args, **kwargs):
        # todo: Add ability to target player - right now cannot because player
        # doesn't have ai.

        entities = kwargs['entities']
        fov_map = kwargs['fov_map']
        target_x = kwargs['target_x']
        target_y = kwargs['target_y']

        if not fov_map.fov[target_y, target_x]:
            return actions.ActionResult(
                success=False,
                msg='You cannot target a tile outside your field of view.',
                # 'consumed': False,
            )

        for entity in entities:
            matches_coordinates = entity.x == target_x and entity.y == target_y

            if matches_coordinates and entity.has_comp('ai'):
                confused_ai = ConfusedBehavior(owner=entity, prev_ai=entity.ai, num_turns=10)
                entity.ai = confused_ai

                return actions.ActionResult(
                    success=True,
                    msg='The eyes of the {} look vacant, as he starts to stumble around!'.format(entity.name)
                    # 'consumed': True,
                )

        return actions.ActionResult(
            success=False,
            msg='There is no targetable enemy at that location.'
            # 'consumed': False,
        )
