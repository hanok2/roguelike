import tcod
from . import factory
from .entity import Entity
from .components import Fighter, Level, Equipment
from .config import RenderOrder
from .inventory import Inventory

HERO_HP = 100
HERO_DEF = 1
HERO_POW = 2
HERO_INV_CAPACITY = 26

def get_hero():
    fighter_comp = Fighter(
        hp=HERO_HP,
        defense=HERO_DEF,
        power=HERO_POW
    )
    inv_comp = Inventory(HERO_INV_CAPACITY)
    lvl_comp = Level()
    equipment_comp = Equipment()

    hero = Entity(
        x=0,
        y=0,
        char='@',
        color=tcod.white,
        name='Player',
        blocks=True,
        render_order=RenderOrder.ACTOR,
        fighter=fighter_comp,
        inv=inv_comp,
        lvl=lvl_comp,
        equipment=equipment_comp,
        human=True
    )

    dagger = factory.mk_entity('dagger', 0, 0)
    hero.inv.add_item(dagger)
    hero.equipment.toggle_equip(dagger)

    return hero
