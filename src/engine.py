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
            engine = Engine()
            engine.play_game(_game, render_eng)
            show_main_menu = True


class Engine(object):
    def __init__(self):
        # self.game = _game
        # self.render_eng = render_eng
        self.name = 'engine'

    def play_game(self, g, render_eng):
        log.debug('Calling play_game...')
        # Deprecated since version 9.3: Use the tcod.event module to check for "QUIT" type events.
        # while not tcod.console_is_window_closed():

        log.debug('Entering game loop...')

        key = tcod.Key()
        mouse = tcod.Mouse()

        current_actor, actor_index = self.get_next_actor(g.stage, len(g.stage.entities))

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

            # Only recompute the fov if its the Players turn.
            if g.fov_recompute and current_actor.has_comp('human'):
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
                g.state = States.ACTOR_TURN
                current_actor, actor_index = self.get_next_actor(g.stage, actor_index)

                # todo: Fix this to be more consistent

                if current_actor.has_comp('human'):
                    action = current_actor.get_action(g, key, mouse)

                elif current_actor.has_comp('ai'):
                    action = current_actor.ai.get_action(g)

            if action:
                self.process_action(
                    action=action,
                    entity=current_actor,
                    g=g
                )


            # Save and go to main menu
            if g.state == States.MAIN_MENU:
                g.redraw = True
                g.state = States.ACTOR_TURN
                save_game(config.savefile, g)
                return

            # if mouse_action?

    def get_next_actor(self, stage, actor_index):
        while True:
            actor_index = (actor_index + 1) % len(stage.entities)
            current_actor = stage.entities[actor_index]
            if current_actor.has_comp('ai') or current_actor.has_comp('human'):
                return current_actor, actor_index

    def process_action(self, action, entity, g):
        log.debug('process_action: %s - %s - %s', g.state, str(entity), action)

        action_results = action.perform(
            state=g.state,
            prev_state=g.prev_state,
            dungeon=g.dungeon,
            stage=g.stage,
            fov_map=g.fov_map,
            entity=entity,
            targeting_item=g.targeting_item,
            game=g,
        )
        if not isinstance(action_results, list):
            action_results = [action_results]

        # Use the first ActionResult to determine if we increment turn??


        # Process all the ActionResults
        for r in action_results:
            log.debug('ActionResult:')
            log.debug('\tSuccess: %s new_state: %s', r.success, r.new_state)
            log.debug('\tMsg: %s', r.msg)
            log.debug('\tAlt: %s', r.alt)

            # Increment turn if necessary
            if r.success and action.consumes_turn:
                g.state = States.TURN_CONSUMED
                g.turns += 1

            if r.new_state:
                g.prev_state = g.state
                g.state = r.new_state

            if r.msg:
                g.msg_log.add(r.msg)

            # alternate actions
            if r.alt:
                g.action_queue.put(r.alt)


def check_for_quit():
    # AttributeError: module 'tcod' has no attribute 'event'
    for event in tcod.event.get():
        if event.type == "QUIT":
            raise SystemExit()
