from random import randint
import tcod
from game_messages import Message


class Fighter(object):
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power

    def take_dmg(self, amt):
        results = []
        self.hp -= amt

        if self.hp <= 0:
            results.append({'dead': self.owner})

        return results

    def heal(self, amt):
        self.hp += amt

        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack(self, target):
        results = []

        dmg = self.power - target.fighter.defense

        if dmg > 0:
            msg = {'msg': Message('{} attacks {} for {} HP.'.format(
                self.owner.name, target.name, str(dmg)),
                                  tcod.white)}

            results.append(msg)
            results.extend(target.fighter.take_dmg(dmg))

        else:
            msg = {'msg': Message('{} attacks {} but does no damage.'.format(
                self.owner.name, target.name),
                                  tcod.white)}
            results.append(msg)

        return results


class BasicMonster(object):
    """AI for a BasicMonster"""
    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        monster = self.owner

        if tcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(target) >= 2:
                # monster.move_towards(target.x, target.y, game_map, entities)
                monster.move_astar(target, entities, game_map)

            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)

        return results


class ConfusedMonster(object):
    def __init__(self, prev_ai, num_turns=10):
        self.prev_ai = prev_ai
        self.num_turns = num_turns

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        if self.num_turns > 0:
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map, entities)

            self.num_turns -= 1

        else:
            # Spell has run out
            self.owner.ai = self.prev_ai
            results.append({
                'msg': Message('The {} is no longer confused!'.format(self.owner.name), tcod.red)
            })

        return results


class Item(object):
    def __init__(self, use_func=None, targeting=False, targeting_msg=None, **kwargs):
        self.use_func = use_func
        self.targeting = targeting
        self.targeting_msg = targeting_msg
        self.func_kwargs = kwargs
