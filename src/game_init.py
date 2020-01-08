import tcod
from src import config
from src import maps
from src.entity import Entity
from src.components import Fighter, Level, Equipment, Equippable
from src.equipment_slots import EquipmentSlots
from src.inventory import Inventory
from src.messages import MsgLog
from src.render_functions import RenderOrder
from src.states import States


def get_game_data():
    # Player components
    fighter_comp = Fighter(hp=100, defense=1, power=2)
    inv_comp = Inventory(26)
    lvl_comp = Level()
    equipment_comp = Equipment()

    # Create entities
    hero = Entity(
        0, 0,
        '@',
        tcod.white,
        'Player',
        blocks=True,
        render_order=RenderOrder.ACTOR,
        fighter=fighter_comp,
        inv=inv_comp,
        lvl=lvl_comp,
        equipment=equipment_comp,
    )

    equippable_comp = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
    dagger = Entity(
        0, 0,
        '(',
        tcod.sky,
        'Dagger',
        equippable=equippable_comp
    )
    hero.inv.add_item(dagger)
    hero.equipment.toggle_equip(dagger)

    # Initialize the Dungeon
    dungeon = maps.Dungeon(hero)

    msg_log = MsgLog(
        x=1,
        width=config.scr_width,
        height=config.msg_height
    )

    state = States.HERO_TURN
    turn = 0

    return dungeon, msg_log, state, turn