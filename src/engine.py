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
            action = handle_main_menu(key_char)

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

        tcod.sys_wait_for_event(
            mask=tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE,
            k=key,
            m=mouse,
            flush=True
        )

        # Get keyboard/mouse input
        key_char = process_tcod_input(key)
        action = handle_keys(key_char, state)

        mouse_action = handle_mouse(mouse)

        move = action.get('move')
        wait = action.get('wait')
        pickup = action.get('pickup')
        show_inv = action.get('show_inv')
        drop_inv = action.get('drop_inv')
        inv_index = action.get('inv_index')
        stair_down = action.get('stair_down')
        stair_up = action.get('stair_up')
        lvl_up = action.get('lvl_up')
        show_char_scr = action.get('show_char_scr')
        gameexit = action.get('exit')
        full_scr = action.get('fullscreen')
        l_click = mouse_action.get('l_click')
        r_click = mouse_action.get('r_click')

        hero_turn_results = []

        if move and state == States.HERO_TURN:
            log.debug('Attempting move.')
            dx, dy = move
            dest_x = hero.x + dx
            dest_y = hero.y + dy

            if not stage.is_blocked(dest_x, dest_y):
                target = stage.get_blocker_at_loc(dest_x, dest_y)

                if target:
                    log.debug('Attacking.')
                    attack_results = hero.fighter.attack(target)
                    hero_turn_results.extend(attack_results)
                else:
                    log.debug('Moving.')
                    hero.move(dx, dy)

                    # Need to redraw FOV
                    fov_recompute = True

                # hero's turn is over
                state = States.WORLD_TURN

        elif wait:
            log.debug('Waiting.')
            # Skip the hero turn
            state = States.WORLD_TURN

        elif pickup and state == States.HERO_TURN:
            log.debug('Attempting pickup.')
            for entity in stage.entities:
                item_pos_at_our_pos = entity.x == hero.x and entity.y == hero.y

                if entity.has_comp('item') and item_pos_at_our_pos:
                    pickup_results = hero.inv.add_item(entity)
                    hero_turn_results.extend(pickup_results)

                    break
            else:
                msg_log.add('There is nothing here to pick up.')

        if show_inv:
            log.debug('Show inventory.')
            prev_state = state
            state = States.SHOW_INV

        if drop_inv:
            log.debug('Drop inventory.')
            prev_state == state
            state = States.DROP_INV

        # Item usage
        if inv_index is not None and prev_state != States.HERO_DEAD and inv_index < len(hero.inv.items):
            log.debug('Inventory menu.')
            item = hero.inv.items[inv_index]

            if state == States.SHOW_INV:
                hero_turn_results.extend(
                    hero.inv.use(
                        item, entities=stage.entities, fov_map=fov_map
                    )
                )

            elif state == States.DROP_INV:
                hero_turn_results.extend(hero.inv.drop(item))

        if stair_down and state == States.HERO_TURN:
            log.debug('Attempting stair down.')
            for entity in stage.entities:
                if entity.has_comp('stair_down'):
                    hero_at_stairs = entity.x == hero.x and entity.y == hero.y
                    if hero_at_stairs:
                        dungeon.mk_next_stage()

                        if dungeon.move_downstairs():
                            stage = dungeon.get_stage()
                            stage.populate()
                            msg_log.add('You carefully descend the stairs down.')

                            fov_map = initialize_fov(stage)
                            fov_recompute = True
                            render_eng.con.clear()
                            break
                        else:
                            raise ValueError("Something weird happened with going downstairs!")

            else:
                msg_log.add('There are no stairs here.')

        if stair_up and state == States.HERO_TURN:
            log.debug('Attempting stair up.')
            for entity in stage.entities:
                if entity.has_comp('stair_up'):
                    hero_at_stairs = entity.x == hero.x and entity.y == hero.y
                    if hero_at_stairs:

                        if dungeon.current_stage == 0:
                            msg_log.add('You go up the stairs and leave the dungeon forever...')
                            state = States.HERO_DEAD
                            # gameexit = True
                            break

                        elif dungeon.move_upstairs():
                            stage = dungeon.get_stage()
                            msg_log.add('You ascend the stairs up.')

                            fov_map = initialize_fov(stage)
                            fov_recompute = True
                            render_eng.con.clear()
                            break
                        else:
                            raise ValueError("Something weird happened with going upstairs!")

            else:
                msg_log.add('There are no stairs here.')

        if lvl_up:
            log.debug('Level up stat boost.')
            # todo: Move stat boosts to config
            if lvl_up == 'hp':
                hero.fighter.base_max_hp += 20
                hero.fighter.hp += 20
            elif lvl_up == 'str':
                hero.fighter.base_power += 1
            elif lvl_up == 'def':
                hero.fighter.base_defense += 1

            state = prev_state

        if show_char_scr:
            log.debug('Show character screen.')
            prev_state = state
            state = States.SHOW_STATS

        if state == States.TARGETING:
            log.debug('Targeting.')
            if l_click:
                target_x, target_y = l_click

                # note: Due to the message console - we have to offset the y.
                target_y -= config.msg_height

                item_use_results = hero.inv.use(
                    targeting_item,
                    entities=stage.entities,
                    fov_map=fov_map,
                    target_x=target_x,
                    target_y=target_y
                )
                hero_turn_results.extend(item_use_results)

            elif r_click:
                hero_turn_results.append({'cancel_target': True})

        if gameexit:
            log.debug('Attempting exit.')
            if state in (States.SHOW_INV, States.DROP_INV, States.SHOW_STATS):
                state = prev_state
            elif state == States.TARGETING:
                hero_turn_results.append({'cancel_target': True})
            else:
                save_game(config.savefile, dungeon, msg_log, state, turns)
                return True

        if full_scr:
            log.debug('Full screen.')
            # Toggle fullscreen on/off
            tcod.console_set_fullscreen(fullscreen=not tcod.console_is_fullscreen())

        # Process hero results
        for result in hero_turn_results:
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


def check_for_quit():
    # Check for quitting

    # AttributeError: module 'tcod' has no attribute 'event'
    for event in tcod.event.get():
        if event.type == "QUIT":
            raise SystemExit()
