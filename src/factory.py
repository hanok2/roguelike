import tcod
from . import config
from . import item_funcs
from .config import RenderOrder, EquipmentSlots
from .components import Fighter, ApproachAI, Item, Equippable
from .entity import Entity
from .random_utils import rnd_choice_from_dict, from_dungeon_lvl


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


def rnd_monster(x, y):
    monster_choice = rnd_choice_from_dict(monster_chances)
    return mk_entity(monster_choice, x, y)


def rnd_item(x, y):
    item_choice = rnd_choice_from_dict(item_chances)
    return mk_entity(item_choice, x, y)


def mk_entity(entity_name, x, y):
    if x < 0 or y < 0:
        raise ValueError('x and y coordinates must be 0 or greater!')

    if entity_name == 'spider':
        spider = Entity(
            name='Spider',
            x=x,
            y=y,
            char='s',
            color=tcod.desaturated_green,
            blocks=True,
            render_order=RenderOrder.ACTOR,
        )
        spider.fighter = Fighter(owner=spider, hp=5, defense=0, power=2, xp=5)
        spider.ai = ApproachAI(spider)
        return spider

    elif entity_name == 'orc':
        orc = Entity(
            name='Orc',
            x=x,
            y=y,
            char='o',
            color=tcod.desaturated_green,
            blocks=True,
            render_order=RenderOrder.ACTOR,
        )
        orc.fighter = Fighter(owner=orc, hp=10, defense=1, power=3, xp=35)
        orc.ai = ApproachAI(orc)
        return orc

    elif entity_name == 'troll':
        troll = Entity(
            name='Troll',
            x=x,
            y=y,
            char='T',
            color=tcod.darker_green,
            blocks=True,
            render_order=RenderOrder.ACTOR,
        )
        troll.fighter = Fighter(owner=troll, hp=10, defense=2, power=4, xp=100)
        troll.ai = ApproachAI(troll)
        return troll

    if entity_name == 'healing_potion':
        item = Entity(
            name="Healing potion",
            x=x,
            y=y,
            blocks=False,
            char='!',
            color=tcod.violet,
            render_order=RenderOrder.ITEM,
        )
        item.item = Item(item, use_func=item_funcs.UseHeal(), amt=40)
        return item

    elif entity_name == 'sword':
        item = Entity(
            name='Sword',
            x=x,
            y=y,
            blocks=False,
            char='(',
            color=tcod.sky,
            render_order=RenderOrder.ITEM,
        )
        item.item = Item(owner=item)
        item.equippable = Equippable(owner=item, slot=EquipmentSlots.MAIN_HAND, power_bonus=3)
        return item

    elif entity_name == 'dagger':
        item = Entity(
            name='Dagger',
            x=0, y=0,
            blocks=False,
            char='(',
            color=tcod.sky,
            render_order=RenderOrder.ITEM,
        )
        item.item = Item(owner=item)
        item.equippable = Equippable(owner=item, slot=EquipmentSlots.MAIN_HAND, power_bonus=2)
        return item

    elif entity_name == 'shield':
        item = Entity(
            name='Shield',
            x=x, y=y,
            blocks=False,
            char='[',
            color=tcod.darker_orange,
            render_order=RenderOrder.ITEM,
        )
        item.item = Item(owner=item)
        item.equippable = Equippable(owner=item, slot=EquipmentSlots.OFF_HAND, defense_bonus=2)
        return item

    elif entity_name == 'ring of hp':
        item = Entity(
            name='Ring of HP',
            x=x, y=y,
            blocks=False,
            char='=',
            color=tcod.blue,
            render_order=RenderOrder.ITEM,
        )
        item.item = Item(owner=item)
        item.equippable = Equippable(owner=item, slot=EquipmentSlots.OFF_HAND, max_hp_bonus=50)
        return item

    elif entity_name == 'fireball_scroll':
        item = Entity(
            name="Fireball Scroll",
            x=x,
            y=y,
            blocks=False,
            char='?',
            color=tcod.yellow,
            render_order=RenderOrder.ITEM,
        )
        item.item = Item(
            owner=item,
            use_func=item_funcs.UseFireball(),
            targeting=True,
            targeting_msg='Left-click a target tile for the fireball, or right-click to cancel.',
            dmg=25,
            radius=3
        )
        return item

    elif entity_name == 'confusion_scroll':
        item = Entity(
            name="Confuse Scroll",
            x=x, y=y,
            blocks=False,
            char='?',
            color=tcod.yellow,
            render_order=RenderOrder.ITEM,
        )

        item.item = Item(
            owner=item,
            use_func=item_funcs.UseConfuse(),
            targeting=True,
            targeting_msg='Left-click an enemy to confuse it, or right-click to cancel.',
        )
        return item

    elif entity_name == 'lightning_scroll':
        # Scroll of lightning bolt
        item = Entity(
            name="Lightning Scroll",
            x=x, y=y,
            blocks=False,
            char='?',
            color=tcod.yellow,
            render_order=RenderOrder.ITEM,
        )

        item.item = Item(
            owner=item,
            use_func=item_funcs.UseLightning(),
            dmg=40,
            max_range=5
        )
        return item

    raise ValueError('Unknown entity selected: {}'.format(entity_name))
