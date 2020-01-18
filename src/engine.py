import tcod
from . import config
from . import game_init
from . import logger
from . import render_functions
from .config import States
from .data_loaders import load_game, save_game
from .death_functions import kill_monster, kill_hero
from .fov import initialize_fov, recompute_fov
from .input_handling import handle_keys, handle_mouse, handle_main_menu, process_tcod_input

log = logger.setup_logger()


def main():
    log.debug('Started new game.')

    render_eng = render_functions.RenderEngine()

    # Initialize game data
    dungeon = None
    msg_log = None
    state = None
    turns = 0

    show_main_menu = True
    show_load_err_msg = False

    main_menu_bg_img = tcod.image_load(filename=config.menu_img)

    key = tcod.Key()
    mouse = tcod.Mouse()

    while True:
        # todo: This runs all the time! Make it wait...

        # Deprecated since version 9.3: Use the tcod.event.get function to check for events.
        tcod.sys_check_for_event(
            mask=tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE,
            k=key,
            m=mouse
        )

        # When I can re-arrange input after rendering - re-enable this...
        # tcod.sys_wait_for_event(
            # mask=tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE,
            # k=key,
            # m=mouse,
            # flush=True
        # )

        if show_main_menu:
            render_eng.render_main_menu(main_menu_bg_img)

            if show_load_err_msg:
                render_eng.render_msg_box(render_eng, 'No save game to load', 50)

            # Update the display to represent the root consoles current state.
            tcod.console_flush()

            key_char = process_tcod_input(key)
            action = handle_main_menu(state=None, key=key_char)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')
            options = action.get('options')

            if show_load_err_msg and (new_game or load_saved_game or exit_game):
                show_load_err_msg = False
            elif new_game:
                log.debug('New game selected.')
                dungeon, msg_log, state, turns = game_init.get_game_data()
                state = States.HERO_TURN
                show_main_menu = False

            elif load_saved_game:
                log.debug('Load game selected.')
                try:
                    dungeon, msg_log, state, turns = load_game(config.savefile)
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_err_msg = True

            elif options:
                # todo: Fill out options menu
                log.debug('Options selected - STUB!')

            elif exit_game:
                log.debug('Exit selected')
                break
        else:
            # Reset a console to its default colors and the space character.

            render_eng.con.clear()

            play_game(
                dungeon,
                msg_log,
                state,
                turns,
                render_eng
            )
            show_main_menu = True

        # check_for_quit()


def play_game(dungeon, msg_log, state, turns, render_eng):
    log.debug('Calling play_game...')
    hero = dungeon.hero
    stage = dungeon.get_stage()

    fov_recompute = True

    # Initialize fov
    fov_map = initialize_fov(stage)

    key = tcod.Key()
    mouse = tcod.Mouse()

    prev_state = state

    # Keep track of any targeting items that were selected.
    targeting_item = None

    # Keep track of any alternate Actions
    next_action = None

    # Game loop

    # Deprecated since version 9.3: Use the tcod.event module to check for "QUIT" type events.
    # while not tcod.console_is_window_closed():

    log.debug('Entering game loop...')
    while True:
        if fov_recompute:
            log.debug('fov_recompute...')
            recompute_fov(
                fov_map,
                hero.x,
                hero.y,
                config.fov_radius,
                config.fov_light_walls,
                config.fov_algorithm
            )

        # Render all entities
        render_eng.render_all(
            dungeon,
            fov_map,
            fov_recompute,
            msg_log,
            mouse,
            state,
            turns
        )

        fov_recompute = False       # Mandatory

        # Presents everything on screen
        tcod.console_flush()

        # Clear all entities
        render_eng.clear_all(stage.entities)

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

        if next_action:
            action = next_action
            next_action = None

        else:
            tcod.sys_wait_for_event(
                mask=tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE,
                k=key,
                m=mouse,
                flush=True
            )

            # Get keyboard/mouse input
            key_char = process_tcod_input(key)

            action = handle_keys(state, key_char)
            mouse_action = handle_mouse(mouse)

        if action:
            next_action, state, prev_state, dungeon, stage, fov_map, hero, targeting_item, msg_log = process_action(action, state, prev_state, dungeon, stage, fov_map, hero, targeting_item, msg_log)

        # if mouse_action?

        if state == States.WORLD_TURN:
            log.debug('Turn: {}'.format(turns))
            # Increment turn counter
            # This *may* go elsewhere, but we'll try it here first.
            turns += 1

            for entity in stage.entities:

                if entity.has_comp('ai'):
                    turn_results = entity.ai.take_turn(
                        hero,
                        fov_map,
                        stage,
                    )

                    for result in turn_results:
                        msg = result.get('msg')
                        dead_entity = result.get('dead')

                        if msg:
                            msg_log.add(msg)

                        if dead_entity:
                            if dead_entity == hero:
                                msg, state = kill_hero(dead_entity)
                            else:
                                msg = kill_monster(dead_entity)

                            msg_log.add(msg)

                            if state == States.HERO_DEAD:
                                break

                    if state == States.HERO_DEAD:
                        break

            else:
                state = States.HERO_TURN

        # check_for_quit()


def process_action(action, state, prev_state, dungeon, stage, fov_map, hero, targeting_item, msg_log):
    next_action = None
    hero_turn_results = []

    # Perform action
    action.perform(
        state=state,
        prev_state=prev_state,
        dungeon=dungeon,
        stage=stage,
        fov_map=fov_map,
        hero=hero,     # todo: consolidate to entity
        entity=hero,
        targeting_item=targeting_item,
    )

    hero_turn_results = action.results

    # Increment turn if necessary
    if action.consumes_turn:
        state = States.WORLD_TURN

    # Process hero results
    for result in hero_turn_results:
        alternate = result.get('alternate')

        attack = result.get('attack')
        new_state = result.get('state')
        fov_recompute = result.get('fov_recompute')
        msg = result.get('msg')
        dead_entity = result.get('dead')
        item_added = result.get('item_added')
        item_consumed = result.get('consumed')
        item_dropped = result.get('item_dropped')
        equip = result.get('equip')
        targeting = result.get('targeting')
        cancel_target = result.get('cancel_target')
        cancel_inv = result.get('cancel_inv')

        xp = result.get('xp')

        if new_state:
            state = new_state

        if alternate:
            next_action = alternate

        if fov_recompute:
            fov_recompute = True

        if msg:
            log.debug('msg: {}.'.format(msg))
            msg_log.add(msg)

        if cancel_target:
            log.debug('Targeting cancelled.')
            state = prev_state
            msg_log.add('Targeting cancelled.')

        if cancel_inv:
            log.debug('Inventory menu cancelled')
            state = prev_state

        if xp:
            log.debug('Adding xp.')
            leveled_up = hero.lvl.add_xp(xp)

            if leveled_up:
                log.debug('Hero level up.')
                msg_log.add('Your battle skills grow stronger! You reached level {}!'.format(hero.lvl.current_lvl))
                prev_state = state
                state = States.LEVEL_UP

        if dead_entity:
            log.debug('Dead entity.')
            if dead_entity == hero:
                msg, state = kill_hero(dead_entity)
            else:
                msg = kill_monster(dead_entity)

            msg_log.add(msg)

        if item_added:
            log.debug('Item added.')
            stage.entities.remove(item_added)
            state = States.WORLD_TURN

        if item_consumed:
            log.debug('Item consumed.')
            state = States.WORLD_TURN

        if targeting:
            log.debug('Targeting.')
            # Set to HERO_TURN so that if cancelled, we don't go back to inv.
            prev_state = States.HERO_TURN
            state = States.TARGETING
            targeting_item = targeting
            msg_log.add(targeting_item.item.targeting_msg)

        if item_dropped:
            log.debug('Item dropped.')
            stage.entities.append(item_dropped)
            state = States.WORLD_TURN

        if equip:
            log.debug('Equip.')
            equip_results = hero.equipment.toggle_equip(equip)

            for equip_result in equip_results:
                equipped = equip_result.get('equipped')
                dequipped = equip_result.get('dequipped')

                if equipped:
                    msg_log.add('You equipped the {}'.format(equipped.name))

                if dequipped:
                    msg_log.add('You dequipped the {}'.format(dequipped.name))

            state = States.WORLD_TURN


        return next_action, state, prev_state, dungeon, stage, fov_map, hero, targeting_item, msg_log


def check_for_quit():
    # Check for quitting

    # AttributeError: module 'tcod' has no attribute 'event'
    for event in tcod.event.get():
        if event.type == "QUIT":
            raise SystemExit()
