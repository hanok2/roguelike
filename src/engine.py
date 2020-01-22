import tcod
from . import config
from . import game
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
                _game = game.Game()

                show_main_menu = False

            elif load_saved_game:
                log.debug('Load game selected.')
                try:
                    _game = load_game(config.savefile)

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

            play_game(_game, render_eng)
            show_main_menu = True


def play_game(g, render_eng):
    log.debug('Calling play_game...')
    # Deprecated since version 9.3: Use the tcod.event module to check for "QUIT" type events.
    # while not tcod.console_is_window_closed():

    log.debug('Entering game loop...')

    mouse = tcod.Mouse()

    actors = g.stage.entities
    actor_index = 0
    # Game loop
    while True:
        if g.redraw:
            # Reset the stage
            g.stage = g.dungeon.get_stage()

            g.fov_map = initialize_fov(g.stage)
            g.fov_recompute = True
            render_eng.con.clear()
            # libtcod.console_clear(con)
            g.redraw = False

        if g.fov_recompute:
            log.debug('fov_recompute...')
            recompute_fov(
                g.fov_map,
                g.hero.x,
                g.hero.y,
                config.fov_radius,
                config.fov_light_walls,
                config.fov_algorithm
            )

        # Render all entities
        render_eng.render_all(
            g.dungeon,
            g.fov_map,
            g.fov_recompute,
            g.msg_log,
            mouse,
            g.state,
            g.turns
        )

        g.fov_recompute = False       # Mandatory

        # Presents everything on screen
        tcod.console_flush()

        # Clear all entities
        render_eng.clear_all(g.stage.entities)

        # Check the action queue for any remaining actions - use them first
        if not g.action_queue.empty():
            action = g.action_queue.get()

        else:
            current_actor = g.stage.entities[actor_index].get_action(g)

            # todo: Fix this to be more consistent

            if current_actor.has_comp('human'):
                action = current_actor.get_action(g)
            elif current_actor.has_comp('ai'):
                action = current_actor.ai.get_action(g)

        if action:
            process_action(action, g.hero, g)

            # Print any messges
            # If failed - don't consume turn
            # If succeed - consume turn if required
            # If new state - change the state, and update the prev_state
            # If alternates actions - Add new Actions to the queue (in order)

        # Save and go to main menu
        if g.state == States.MAIN_MENU:
            g.redraw = True
            g.state = States.HERO_TURN
            save_game(config.savefile, g)
            return

        # if mouse_action?

        actor_index = (actor_index + 1) % len(g.stage.entities)


def process_action(action, entity, g):
    log.debug('process_action: {} - State: {}'.format(action, g.state))

    action_result = action.perform(
        state=g.state,
        prev_state=g.prev_state,
        dungeon=g.dungeon,
        stage=g.stage,
        fov_map=g.fov_map,
        entity=entity,
        targeting_item=g.targeting_item,
        game=g,
    )

    if action_result.success and action.consumes_turn:
        # Increment turn if necessary
        g.state = States.WORLD_TURN

    if action_result.new_state:
        g.prev_state = g.state
        g.state = action_result.new_state

    if action_result.msg:
        log.debug('msg: {}.'.format(action_result.msg))
        g.msg_log.add(action.result.msg)

    # alternate actions
    for a in action_result.alt:
        g.action_queue.put(a)


def check_for_quit():
    # AttributeError: module 'tcod' has no attribute 'event'
    for event in tcod.event.get():
        if event.type == "QUIT":
            raise SystemExit()
