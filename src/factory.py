import tcod
from . import config
from .components import Fighter, ApproachingBehavior, Item, EquipmentSlots, Equippable
from .entity import Entity
from .item_functions import heal, cast_confuse, cast_lightning, cast_fireball
from .random_utils import rnd_choice_from_dict, from_dungeon_lvl
from .render_functions import RenderOrder

# Update to take the level
item_chances = {
    'healing_potion': 35,
    # 'lightning_scroll': from_dungeon_lvl([[25, 4]], dungeon_lvl),
    # 'fireball_scroll': from_dungeon_lvl([[25, 6]], dungeon_lvl),
    # 'confusion_scroll': from_dungeon_lvl([[10, 2]], dungeon_lvl),
    'lightning_scroll': 5,
    'fireball_scroll': 5,
    'confusion_scroll': 5,
    'sword': 5,
    'shield': 5,
    # 'sword': from_dungeon_lvl([[5, 4]], dungeon_lvl),
    # 'shield': from_dungeon_lvl([[15, 8]], dungeon_lvl),
}

# Update to take the level
monster_chances = {
    'spider': 80,
    'orc': 80,
    'troll': 40,
    # 'troll': from_dungeon_lvl(config.troll_chances, dungeon_lvl)
}


def get_random_monster(x, y):
    monster_choice = rnd_choice_from_dict(monster_chances)
    return mk_entity(monster_choice, x, y)


def get_random_item(x, y):
    item_choice = rnd_choice_from_dict(item_chances)
    return mk_entity(item_choice, x, y)


def mk_entity(entity_name, x, y):
    if x < 0 or y < 0:
        raise ValueError('x and y coordinates must be 0 or greater!')

    if entity_name == 'spider':
        return Entity(
            x, y,
            's',
            tcod.desaturated_green,
            'Spider',
            blocks=True,
            render_order=RenderOrder.ACTOR,
            fighter=Fighter(hp=5, defense=0, power=2, xp=5),
            ai=ApproachingBehavior()
        )
    elif entity_name == 'orc':
        return Entity(
            x, y,
            'o',
            tcod.desaturated_green,
            'Orc',
            blocks=True,
            render_order=RenderOrder.ACTOR,
            fighter=Fighter(hp=10, defense=1, power=3, xp=35),
            ai=ApproachingBehavior()
        )
    elif entity_name == 'troll':
        return Entity(
            x, y,
            'T',
            tcod.darker_green,
            'Troll',
            blocks=True,
            render_order=RenderOrder.ACTOR,
            fighter=Fighter(hp=10, defense=2, power=4, xp=100),
            ai=ApproachingBehavior()
        )


    if entity_name == 'healing_potion':
        return Entity(
            x, y,
            '!',
            tcod.violet,
            "Healing potion",
            render_order=RenderOrder.ITEM,
            item=Item(use_func=heal, amt=40),
        )

    elif entity_name == 'sword':
        return Entity(
            x, y,
            '(',
            tcod.sky,
            'Sword',
            equippable=Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
        )
    elif entity_name == 'shield':
        return Entity(
            x, y,
            '[',
            tcod.darker_orange,
            'Shield',
            equippable=Equippable(EquipmentSlots.OFF_HAND, defense_bonus=2)
        )

    elif entity_name == 'fireball_scroll':
        item_comp = Item(
            use_func=cast_fireball,
            targeting=True,
            targeting_msg='Left-click a target tile for the fireball, or right-click to cancel.',
            dmg=25,
            radius=3
        )

        return Entity(
            x, y,
            '?',
            tcod.yellow,
            "Fireball Scroll",
            render_order=RenderOrder.ITEM,
            item=item_comp,
        )

    elif entity_name == 'confusion_scroll':
        item_comp = Item(
            use_func=cast_confuse,
            targeting=True,
            targeting_msg='Left-click an enemy to confuse it, or right-click to cancel.',
        )

        return Entity(
            x, y,
            '?',
            tcod.yellow,
            "Confuse Scroll",
            render_order=RenderOrder.ITEM,
            item=item_comp,
        )

    elif entity_name == 'lightning_scroll':
        # Scroll of lightning bolt
        item_comp = Item(use_func=cast_lightning, dmg=40, max_range=5)
        return Entity(
            x, y,
            '?',
            tcod.yellow,
            "Lightning Scroll",
            render_order=RenderOrder.ITEM,
            item=item_comp,
        )

    raise ValueError('Unknown entity selected: {}'.format(entity_name))
