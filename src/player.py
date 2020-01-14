import tcod
from . import factory
from . import entity
from .components import Fighter, Level, Equipment
from .config import RenderOrder
from .inventory import Inventory

HERO_HP = 100
HERO_DEF = 1
HERO_POW = 2
HERO_INV_CAPACITY = 26

def get_hero():
    hero = Player()

    dagger = factory.mk_entity('dagger', 0, 0)
    hero.inv.add_item(dagger)
    hero.equipment.toggle_equip(dagger)

    return hero


class Player(entity.Entity):
    def __init__(self):
        super().__init__(
            x=0,
            y=0,
            char='@',
            color=tcod.white,
            name='Player',
            human=True,
            equipment=Equipment(),
            lvl=Level(),
            inv=Inventory(HERO_INV_CAPACITY),
            render_order=RenderOrder.ACTOR,
            blocks=True,
        )
        self.fighter = Fighter(self, HERO_HP, HERO_DEF, HERO_POW)
