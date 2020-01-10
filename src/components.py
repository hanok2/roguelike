from random import randint
from .equipment_slots import EquipmentSlots


class Fighter(object):
    def __init__(self, hp, defense, power, xp=0):
        if hp <= 0:
            raise ValueError('Fighter hp must be greater than 0!')
        elif defense < 0:
            raise ValueError('Fighter defense must be greater than or equal to 0!')
        elif power < 0:
            raise ValueError('Fighter power must be greater than or equal to 0!')
        elif xp < 0:
            raise ValueError('Fighter xp must be greater than or equal to 0!')

        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp

    @property
    def max_hp(self):
        if self.owner and self.owner.equipment:
            # Take into account what equipment is equipped
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0
        return self.base_max_hp + bonus

    @property
    def power(self):
        if self.owner and self.owner.equipment:
            # Take into account what equipment is equipped
            bonus = self.owner.equipment.power_bonus
        else:
            bonus = 0
        return self.base_power + bonus

    @property
    def defense(self):
        if self.owner and self.owner.equipment:
            # Take into account what equipment is equipped
            bonus = self.owner.equipment.defense_bonus
        else:
            bonus = 0
        return self.base_defense + bonus

    def take_dmg(self, amt):
        results = []
        self.hp -= amt

        if self.hp <= 0:
            results.append({
                'dead': self.owner,
                'xp': self.xp
            })

        return results

    def heal(self, amt):
        self.hp += amt

        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack(self, target):
        results = []

        dmg = self.power - target.fighter.defense

        if dmg > 0:
            msg = {'msg': '{} attacks {}!'.format(self.owner.name, target.name)}

            results.append(msg)
            results.extend(target.fighter.take_dmg(dmg))

        else:
            msg = {'msg': '{} attacks {}... But does no damage.'.format(self.owner.name, target.name), }
            results.append(msg)

        return results


class ApproachingBehavior(object):
    """AI for an entity/monster to approach the hero when within line of sight"""
    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        monster = self.owner

        if fov_map.fov[monster.y, monster.x]:
            if monster.distance_to(target) >= 2:
                # monster.move_towards(target.x, target.y, game_map, entities)
                monster.move_astar(target, entities, game_map)

            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)

        return results


class ConfusedBehavior(object):
    """AI for an entity/monster to move randomly for a set number of turns."""
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
                'msg': 'The {} is no longer confused!'.format(self.owner.name)
            })

        return results


class Item(object):
    def __init__(self, use_func=None, targeting=False, targeting_msg=None, **kwargs):
        self.use_func = use_func
        self.targeting = targeting
        self.targeting_msg = targeting_msg
        self.func_kwargs = kwargs


class Level(object):
    def __init__(self, current_lvl=1, current_xp=0, lvl_up_base=200, lvl_up_factor=150):
        # Note: Consider putting defaults in constants dict.
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
        self.current_xp += xp

        if self.current_xp > self.xp_to_next_lvl:
            # Maybe remove this line, seems like we are short-changing the player
            # self.current_xp -= self.xp_to_next_lvl

            # For now - reset the XP
            self.current_xp = 0
            self.current_lvl += 1

            return True
        else:
            return False


class Equippable(object):
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus


class Equipment(object):
    """Since we're using properties, these values can be accessed like a regular
        variable, which will come in handy soon enough. If the player has equipment
        in both the main hand and off hand that increases attack, for instance, then
        we'll get the bonus the same either way.
    """
    def __init__(self, main_hand=None, off_hand=None):
        self.main_hand = main_hand
        self.off_hand = off_hand

    @property
    def max_hp_bonus(self):
        bonus = 0
        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.max_hp_bonus
        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.max_hp_bonus
        return bonus

    @property
    def power_bonus(self):
        bonus = 0
        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.power_bonus
        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.power_bonus
        return bonus

    @property
    def defense_bonus(self):
        bonus = 0
        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.defense_bonus
        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.defense_bonus
        return bonus

    def toggle_equip(self, equippable_entity):
        """toggle_equip is what we'll call when we're either equipping or dequipping
            an item. If the item was not previously equipped, we equip it, removing
            any previously equipped item. If it's equipped already, we'll assume
            the player meant to remove it, and just dequip it.

            The two variables main_hand and off_hand will hold the entities that
            we're equipping. If they are set to None, then that means nothing is
            equipped to that slot.
        """

        results = []

        slot = equippable_entity.equippable.slot

        if slot == EquipmentSlots.MAIN_HAND:
            if self.main_hand == equippable_entity:
                self.main_hand = None
                results.append({'dequipped': equippable_entity})
            else:
                if self.main_hand:
                    results.append({'dequipped': self.main_hand})

                self.main_hand = equippable_entity
                results.append({'equipped': equippable_entity})

        elif slot == EquipmentSlots.OFF_HAND:
            if self.off_hand == equippable_entity:
                self.off_hand = None
                results.append({'dequipped': equippable_entity})
            else:
                if self.off_hand:
                    results.append({'dequipped': self.off_hand})

                self.off_hand = equippable_entity
                results.append({'equipped': equippable_entity})

        return results
