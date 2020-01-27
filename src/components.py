from random import randint
from . import actions
from . import config
from .config import Slots


class Fighter(object):
    def __init__(self, owner, hp, defense, power, xp=0):
        if hp <= 0:
            raise ValueError('Fighter hp must be greater than 0!')
        elif defense < 0:
            raise ValueError('Fighter defense must be greater than or equal to 0!')
        elif power < 0:
            raise ValueError('Fighter power must be greater than or equal to 0!')
        elif xp < 0:
            raise ValueError('Fighter xp must be greater than or equal to 0!')

        self.owner = owner
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp

    @property
    def max_hp(self):
        if self.owner.has_comp('equipment'):
            # Take into account what equipment is equipped
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0
        return self.base_max_hp + bonus

    @property
    def power(self):
        if self.owner.has_comp('equipment'):
            # Take into account what equipment is equipped
            bonus = self.owner.equipment.power_bonus
        else:
            bonus = 0
        return self.base_power + bonus

    @property
    def defense(self):
        if self.owner.has_comp('equipment'):
            # Take into account what equipment is equipped
            bonus = self.owner.equipment.defense_bonus
        else:
            bonus = 0
        return self.base_defense + bonus


class ApproachAI(object):
    """AI for an entity/monster to approach the hero when within line of sight"""
    def __init__(self, owner):
        self.owner = owner

    def get_action(self, g):
        if g.fov_map.fov[self.owner.y, self.owner.x]:

            # if stages.Stage.distance_between_entities(self.owner, g.hero) >= 2:

            if self.owner.distance_to(g.hero) >= 2:
                return actions.MoveAStarAction(g.stage, self.owner, g.hero)

                # self.owner.move_astar(g.hero, g.stage)

            elif g.hero.fighter.hp > 0:
                # attack_results = self.owner.fighter.attack(target)
                # attack_results = self.owner.fighter.attack(g.hero)

                return actions.AttackAction(attacker=self.owner, defender=g.hero)


                # results.extend(attack_results)

        return actions.WaitAction()



class ConfusedBehavior(object):
    """AI for an entity/monster to move randomly for a set number of turns."""
    def __init__(self, owner, prev_ai, num_turns=10):
        if num_turns < 0:
            raise ValueError('num_turns needs to be 0 or greater!')

        self.owner = owner
        self.prev_ai = prev_ai
        self.num_turns = num_turns

    def take_turn(self, target, fov_map, game_map):
        results = []

        if self.num_turns > 0:
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map)

            self.num_turns -= 1

        else:
            # Spell has run out
            self.owner.ai = self.prev_ai
            results.append({
                'msg': 'The {} is no longer confused!'.format(self.owner.name)
            })

        return results


class Item(object):
    def __init__(self, owner, use_func=None, targeting=False, targeting_msg=None, **kwargs):
        self.owner = owner
        self.use_func = use_func
        self.targeting = targeting
        self.targeting_msg = targeting_msg
        self.func_kwargs = kwargs


class Level(object):
    def __init__(self,
                 current_lvl=config.default_lvl,
                 current_xp=config.starting_xp,
                 lvl_up_base=config.lvl_up_base,
                 lvl_up_factor=config.lvl_up_factor):

        self.current_lvl = current_lvl
        self.current_xp = current_xp
        self.lvl_up_base = lvl_up_base
        self.lvl_up_factor = lvl_up_factor

    @property
    def xp_to_next_lvl(self):
        # Read-only variable that we can easily access inside the class and on
        # the objects we create.
        return self.lvl_up_base + self.current_lvl * self.lvl_up_factor

    def add_xp(self, xp):
        if xp < 0:
            raise ValueError('xp must be greater than or equal to 0!')

        self.current_xp += xp

        if self.current_xp > self.xp_to_next_lvl:
            self.current_xp -= self.xp_to_next_lvl
            self.current_lvl += 1
            return True

        return False


class Equippable(object):
    def __init__(self, owner, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        if not slot:
            raise ValueError('slot must not be None!')
        elif power_bonus < 0 or defense_bonus < 0 or max_hp_bonus < 0:
            raise ValueError('bonus must not be less than 0!')

        self.owner = owner
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus

        # If the entity does not have an Item component, then we  add one. This
        # is because every piece of equipment is also an item by definition,
        # because it gets added to the inventory, picked up, and dropped.
        # if not owner.item:
            # item = Item(owner)
            # owner.item = item


class Equipment(object):
    """Since we're using properties, these values can be accessed like a regular
        variable, which will come in handy soon enough. If the player has equipment
        in both the main hand and off hand that increases attack, for instance, then
        we'll get the bonus the same either way.
    """
    def __init__(self):
        self.slots = {slot: None for slot in config.Slots}

    @property
    def max_hp_bonus(self):
        bonus = 0
        for item in self.slots.values():
            if item and item.equippable:
                bonus += item.equippable.max_hp_bonus
        return bonus

    @property
    def power_bonus(self):
        bonus = 0
        for item in self.slots.values():
            if item and item.equippable:
                bonus += item.equippable.power_bonus
        return bonus

    @property
    def defense_bonus(self):
        bonus = 0
        for item in self.slots.values():
            if item and item.equippable:
                bonus += item.equippable.defense_bonus
        return bonus

    def is_equipped(self, equippable):
        for item in self.slots.values():
            if item == equippable:
                return True

        return False

    def equip(self, equippable):
        slot = equippable.equippable.slot
        if slot in self.slots:
            self.slots[slot] = equippable
            return True

        return False

    def unequip(self, equippable):
        if not self.is_equipped(equippable):
            return False

        slot = equippable.equippable.slot

        if slot in self.slots:
            self.slots[slot] = None
            return True

        return False


class EnergyMeter(object):
    def __init__(self, threshold):
        self.threshold = threshold
        self.energy = 0

    def add_energy(self, amt):
        self.energy += amt

    def burn_turn(self):
        if self.energy >= self.threshold:
            self.energy -= self.threshold
            return True
        return False
