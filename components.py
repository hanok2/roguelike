class Fighter(object):
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power


class BasicMonster(object):
    """AI for a BasicMonster"""
    def take_turn(self):
        print('The {} wonders when it will get to move.'.format(self.owner.name))
