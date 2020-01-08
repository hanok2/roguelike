import tcod
import config
import game_init
import render_functions
from data_loaders import load_game, save_game
from death_functions import kill_monster, kill_hero
from entity import get_blockers_at_loc
from fov import initialize_fov, recompute_fov
from states import States
from input_handling import handle_keys, handle_mouse, handle_main_menu
from menus import main_menu, msg_box


def main():
    render_eng = render_functions.RenderEngine()

    # Initialize game data
    # hero = None
    # entities = []
    dungeon = None
    # current_map = None
    msg_log = None
    state = None
    turns = 0

    show_main_menu = True
    show_load_err_msg = False

    main_menu_bg_img = tcod.image_load(filename=config.menu_img)

    key = tcod.Key()
    mouse = tcod.Mouse()

    while True:

        # Deprecated since version 9.3: Use the tcod.event.get function to check for events.
        tcod.sys_check_for_event(
            mask=tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE,
            k=key,
            m=mouse
        )

        if show_main_menu:
            main_menu(render_eng, main_menu_bg_img)

            if show_load_err_msg:
                msg_box(render_eng, 'No save game to load', 50)

            # Update the display to represent the root consoles current state.
            tcod.console_flush()

            action = handle_main_menu(key)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')
            options = action.get('options')

            if show_load_err_msg and (new_game or load_saved_game or exit_game):
                show_load_err_msg = False
            elif new_game:
                dungeon, msg_log, state, turns = game_init.get_game_data()
                state = States.HERO_TURN
                show_main_menu = False

            elif load_saved_game:
                try:
                    dungeon, msg_log, state, turns = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_err_msg = True

            elif options:
                # todo: Fill out options menu
                print('Options selected - STUB!')

            elif exit_game:
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
    hero = dungeon.hero
    current_map = dungeon.current_map()

    fov_recompute = True

    # Initialize fov
    fov_map = initialize_fov(current_map)

    key = tcod.Key()
    mouse = tcod.Mouse()

    prev_state = state

    # Keep track of any targeting items that were selected.
    targeting_item = None

    # Game loop

    # Deprecated since version 9.3: Use the tcod.event module to check for "QUIT" type events.
    # while not tcod.console_is_window_closed():

    while True:
        # Capture new user input
        # Deprecated since version 9.3: Use the tcod.event.get function to check for events.
        tcod.sys_check_for_event(
            mask=tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE,
            k=key,
            m=mouse
        )

        if fov_recompute:
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
        render_eng.clear_all(current_map.entities)

        # Get keyboard/mouse input
        action = handle_keys(key, state)
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
            dx, dy = move
            dest_x = hero.x + dx
            dest_y = hero.y + dy

            if not current_map.is_blocked(dest_x, dest_y):
                target = get_blockers_at_loc(current_map.entities, dest_x, dest_y)

                if target:
                    attack_results = hero.fighter.attack(target)
                    hero_turn_results.extend(attack_results)
                else:
                    hero.move(dx, dy)

                    # Need to redraw FOV
                    fov_recompute = True

                # hero's turn is over
                state = States.WORLD_TURN

        elif wait:
            # Skip the hero turn
            state = States.WORLD_TURN

        elif pickup and state == States.HERO_TURN:
            for entity in current_map.entities:
                item_pos_at_our_pos = entity.x == hero.x and entity.y == hero.y

                if entity.item and item_pos_at_our_pos:
                    pickup_results = hero.inv.add_item(entity)
                    hero_turn_results.extend(pickup_results)

                    break
            else:
                msg_log.add('There is nothing here to pick up.')

        if show_inv:
            prev_state = state
            state = States.SHOW_INV

        if drop_inv:
            prev_state == state
            state = States.DROP_INV

        # Item usage
        if inv_index is not None and prev_state != States.HERO_DEAD and inv_index < len(hero.inv.items):
            item = hero.inv.items[inv_index]

            if state == States.SHOW_INV:
                # hero_turn_results.extend(hero.inv.use(item))
                hero_turn_results.extend(
                    hero.inv.use(
                        item, entities=current_map.entities, fov_map=fov_map
                    )
                )

            elif state == States.DROP_INV:
                hero_turn_results.extend(hero.inv.drop(item))

        if stair_down and state == States.HERO_TURN:
            for entity in current_map.entities:
                hero_at_stairs = entity.x == hero.x and entity.y == hero.y
                if entity.stair_down and hero_at_stairs:
                    dungeon.generate_next_level()
                    if dungeon.move_downstairs():
                        current_map = dungeon.current_map()
                        current_map.populate()
                        # hero = dungeon.hero

                        fov_map = initialize_fov(current_map)
                        fov_recompute = True
                        render_eng.con.clear()
                        break
                    else:
                        raise ValueError("Something weird happened with going downstairs!")

            else:
                msg_log.add('There are no stairs here.')

        if stair_up and state == States.HERO_TURN:
            for entity in current_map.entities:
                hero_at_stairs = entity.x == hero.x and entity.y == hero.y

                if entity.stair_up and hero_at_stairs:

                    if dungeon.current_lvl == 0:
                        msg_log.add('You go up the stairs and leave the dungeon forever...')
                        state = States.HERO_DEAD
                        gameexit = True

                    elif dungeon.move_upstairs():
                        current_map = dungeon.current_map()

                        fov_map = initialize_fov(current_map)
                        fov_recompute = True
                        render_eng.con.clear()
                        break
                    else:
                        raise ValueError("Something weird happened with going upstairs!")

            else:
                msg_log.add('There are no stairs here.')

        if lvl_up:
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
            prev_state = state
            state = States.SHOW_STATS

        if state == States.TARGETING:
            if l_click:
                target_x, target_y = l_click

                item_use_results = hero.inv.use(
                    targeting_item,
                    entities=current_map.entities,
                    fov_map=fov_map,
                    target_x=target_x,
                    target_y=target_y
                )
                hero_turn_results.extend(item_use_results)

            elif r_click:
                hero_turn_results.append({'cancel_target': True})

        if gameexit:
            if state in (States.SHOW_INV, States.DROP_INV, States.SHOW_STATS):
                state = prev_state
            elif state == States.TARGETING:
                hero_turn_results.append({'cancel_target': True})
            else:
                save_game(dungeon, msg_log, state, turns)
                return True

        if full_scr:
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
            xp = result.get('xp')

            if msg:
                msg_log.add(msg)

            if cancel_target:
                state = prev_state
                msg_log.add('Targeting cancelled.')

            if xp:
                leveled_up = hero.lvl.add_xp(xp)

                if leveled_up:
                    msg_log.add('Your battle skills grow stronger! You reached level {}!'.format(hero.lvl.current_lvl))
                    prev_state = state
                    state = States.LEVEL_UP

            if dead_entity:
                if dead_entity == hero:
                    msg, state = kill_hero(dead_entity)
                else:
                    msg = kill_monster(dead_entity)

                msg_log.add(msg)

            if item_added:
                current_map.entities.remove(item_added)
                state = States.WORLD_TURN

            if item_consumed:
                state = States.WORLD_TURN

            if targeting:
                # Set to HERO_TURN so that if cancelled, we don't go back to inv.
                prev_state = States.HERO_TURN
                state = States.TARGETING
                targeting_item = targeting
                msg_log.add(targeting_item.item.targeting_msg)

            if item_dropped:
                current_map.entities.append(item_dropped)
                state = States.WORLD_TURN

            if equip:
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
            # Increment turn counter
            # This *may* go elsewhere, but we'll try it here first.
            turns += 1

            for entity in current_map.entities:

                if entity.ai:
                    turn_results = entity.ai.take_turn(
                        hero,
                        fov_map,
                        current_map,
                        current_map.entities
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


if __name__ == "__main__":
    main()
