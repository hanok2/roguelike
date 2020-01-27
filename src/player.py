import tcod
from . import components
from . import factory
from . import entity
from . import input_handling
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
    hero.equipment.equip(dagger)

    return hero


class Player(entity.Entity):
    def __init__(self, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            char='@',
            color=tcod.white,
            name='Player',
            human=True,
            equipment=Equipment(),
            lvl=Level(),
            render_order=RenderOrder.ACTOR,
            blocks=True,
            energymeter=components.EnergyMeter(threshold=100)
        )
        self.fighter = Fighter(self, HERO_HP, HERO_DEF, HERO_POW)
        self.inv = Inventory(owner=self, capacity=HERO_INV_CAPACITY)


    def get_action(self, g, key, mouse):
        # Capture new user input
        # Deprecated since version 9.3: Use the tcod.event.get function to check for events.
        # tcod.sys_check_for_event(
            # mask=tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE,
            # k=key,
            # m=mouse
        # )

        # Flush False - returns 2 key events
        # tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('h'))
        # tcod.Key(pressed=True, vk=tcod.KEY_TEXT, text='h')

        # Flush True: returns just this
        # tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('h'))


        # Nothing is waiting in the action queue - collect more actions
        tcod.sys_wait_for_event(
            mask=tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE,
            k=key,
            m=mouse,
            flush=True
        )

        # Get keyboard/mouse input
        key_char = input_handling.process_tcod_input(key)

        action = input_handling.handle_keys(g.state, key_char)
        mouse_action = input_handling.handle_mouse(g.state, mouse)

        if mouse_action:
            # Mouse action will take priority over keys (for now)
            # log.debug('mouse_action: {}'.format(mouse_action))

            action = mouse_action

        return action
