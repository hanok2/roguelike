import tcod
from .components import Item, EquipmentSlots, Equippable
from .entity import Entity
from .item_functions import heal, cast_confuse, cast_lightning, cast_fireball
from .random_utils import rnd_choice_from_dict, from_dungeon_lvl
from .render_functions import RenderOrder


def item_chances(dungeon_lvl):
    return {
        'healing_potion': 35,
        # 'lightning_scroll': from_dungeon_lvl([[25, 4]], dungeon_lvl),
        # 'fireball_scroll': from_dungeon_lvl([[25, 6]], dungeon_lvl),
        # 'confusion_scroll': from_dungeon_lvl([[10, 2]], dungeon_lvl),
        'lightning_scroll': 35,
        'fireball_scroll': 35,
        'confusion_scroll': 35,
        'sword': 35,
        'shield': 35,
        # 'sword': from_dungeon_lvl([[5, 4]], dungeon_lvl),
        # 'shield': from_dungeon_lvl([[15, 8]], dungeon_lvl),
    }


def get_rnd_item(x, y, item_chances):
    item_choice = rnd_choice_from_dict(item_chances)

    if item_choice == 'healing_potion':
        item_comp = Item(use_func=heal, amt=40)
        item = Entity(
            x, y,
            '!',
            tcod.violet,
            "Healing potion",
            render_order=RenderOrder.ITEM,
            item=item_comp,
        )

    elif item_choice == 'sword':
        equippable_comp = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
        item = Entity(
            x, y,
            '(',
            tcod.sky,
            'Sword',
            equippable=equippable_comp
        )
    elif item_choice == 'shield':
        equippable_comp = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=2)
        item = Entity(
            x, y,
            '[',
            tcod.darker_orange,
            'Shield',
            equippable=equippable_comp
        )

    elif item_choice == 'fireball_scroll':
        item_comp = Item(
            use_func=cast_fireball,
            targeting=True,
            targeting_msg='Left-click a target tile for the fireball, or right-click to cancel.',
            dmg=25,
            radius=3
        )

        item = Entity(
            x, y,
            '?',
            tcod.yellow,
            "Fireball Scroll",
            render_order=RenderOrder.ITEM,
            item=item_comp,
        )

    elif item_choice == 'confusion_scroll':
        item_comp = Item(
            use_func=cast_confuse,
            targeting=True,
            targeting_msg='Left-click an enemy to confuse it, or right-click to cancel.',
        )

        item = Entity(
            x, y,
            '?',
            tcod.yellow,
            "Confuse Scroll",
            render_order=RenderOrder.ITEM,
            item=item_comp,
        )

    elif item_choice == 'lightning_scroll':
        # Scroll of lightning bolt
        item_comp = Item(use_func=cast_lightning, dmg=40, max_range=5)
        item = Entity(
            x, y,
            '?',
            tcod.yellow,
            "Lightning Scroll",
            render_order=RenderOrder.ITEM,
            item=item_comp,
        )

    return item
