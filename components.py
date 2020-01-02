import tcod

class Fighter(object):
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power

    def take_dmg(self, amt):
        self.hp -= amt

    def attack(self, target):
        dmg = self.power - target.fighter.defense

        if dmg > 0:
            target.fighter.take_dmg(dmg)
            print('{} attacks {} for {} HP.'.format(
                self.owner.name,
                target.name,
                str(dmg))
                 )
        else:
            print('{} attacks {} but does no damage.'.format(
                self.owner.name,
                target.name,
            ))


class BasicMonster(object):
    """AI for a BasicMonster"""
    def take_turn(self, target, fov_map, game_map, entities):
        monster = self.owner

        if tcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(target) >= 2:
                # monster.move_towards(target.x, target.y, game_map, entities)
                monster.move_astar(target, entities, game_map)

            elif target.fighter.hp > 0:
                # print('The {} insults you!'.format(monster.name))
                monster.fighter.attack(target)
