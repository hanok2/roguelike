import tcod
import config
from entity import Entity
from components import Fighter, Level, Equipment, Equippable
from equipment_slots import EquipmentSlots
from maps import Map
from inventory import Inventory
from messages import MsgLog
from render_functions import RenderOrder
from states import States


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

    entities = [hero]

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

    # Initialize the game map
    game_map = Map(
        config.map_width,
        config.map_height
    )

    game_map.make_map(hero, entities)

    msg_log = MsgLog(
        x=1,
        width=config.scr_width,
        height=config.msg_height
    )

    state = States.HERO_TURN
    turn = 0

    return hero, entities, game_map, msg_log, state, turn
