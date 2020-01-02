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


class Item(object):
    def __init__(self):
        pass
