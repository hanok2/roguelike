import tcod
from . import config
from . import game
from . import logger
from . import render_functions
from .config import States
from .data_loaders import load_game, save_game
from .fov import initialize_fov, recompute_fov
from .input_handling import handle_main_menu, process_tcod_input

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
                render_eng.render_msg_box('No save game to load', 50)

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
                _game = load_game(config.savefile)

                if _game:
                    show_main_menu = False
                else:
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
            engine = Engine(_game, render_eng)
            engine.play_game()
            show_main_menu = True


class Engine(object):
    def __init__(self, _game, render_eng):
        self.g = _game
        self.render_eng = render_eng
        self.key = tcod.Key()
        self.mouse = tcod.Mouse()


    def play_game(self):
        log.debug('Calling play_game...')

        # Deprecated since version 9.3: Use the tcod.event module to check for "QUIT" type events.
        # while not tcod.console_is_window_closed():

        # self.update_rendering()

        log.debug('Entering game loop...')
        # Game loop

        # Change to while not dead or main menu?
        while True:
            # Player goes first
            self.player_turn()

            # Save and go to main menu
            if self.g.state == States.MAIN_MENU:
                log.info('trying to enter the MAIN_MENU')

                # self.g.state = States.ACTOR_TURN  # Maybe previous state instead?
                self.g.state = self.g.prev_state
                self.g.redraw = True
                self.g.fov_recompute = True
                save_game(config.savefile, self.g)
                return

            # All other entities on the stage get a turn
            # if not self.g.state == States.HERO_DEAD:
            self.world_turn()

            self.g.fov_recompute = True

    def get_actors(self):
        return [e for e in self.g.stage.entities if e.has_comp('ai')]

    def player_turn(self):
        self.g.state = States.ACTOR_TURN
        log.info('Turn: %s: Player', self.g.turns)
        self.g.hero.energymeter.add_energy(config.energy_per_turn)


        while self.g.hero.energymeter.burn_turn():
            while not self.g.state in (States.TURN_CONSUMED, States.MAIN_MENU):
                self.update_rendering()
                action = self.g.hero.get_action(self.g, self.key, self.mouse)

                self.g.action_queue.put(action)
                self.resolve_actions(self.g.hero)

            if self.g.state == States.MAIN_MENU:
                break

            self.g.turns += 1


    def world_turn(self):
        self.g.state = States.ACTOR_TURN

        for actor in self.get_actors():
            actor.energymeter.add_energy(config.energy_per_turn)

            while actor.energymeter.burn_turn():

                print('Turn: {} Actor: {}'.format(self.g.turns, actor.name))

                action = actor.ai.get_action(self.g)
                self.g.action_queue.put(action)
                self.resolve_actions(actor)

    def resolve_actions(self, actor):
        print('Resolving actions')

        # Check the action queue for any remaining actions - use them first
        while not self.g.action_queue.empty():
            action = self.g.action_queue.get()
            print('\t{}'.format(action))

            self.process_action(action=action, entity=actor)


    def process_action(self, action, entity):
        log.debug('process_action: %s - %s - %s', self.g.state, str(entity), action)

        action_results = action.perform(
            state=self.g.state,
            prev_state=self.g.prev_state,
            dungeon=self.g.dungeon,
            stage=self.g.stage,
            fov_map=self.g.fov_map,
            entity=entity,
            targeting_item=self.g.targeting_item,
            game=self.g,
        )
        if not isinstance(action_results, list):
            action_results = [action_results]

        # Process all the ActionResults
        for r in action_results:
            log.debug('ActionResult:')
            log.debug('\tSuccess: %s new_state: %s', r.success, r.new_state)
            log.debug('\tMsg: %s', r.msg)
            log.debug('\tAlt: %s', r.alt)

            # Increment turn if necessary
            if r.success and action.consumes_turn:
                self.g.state = States.TURN_CONSUMED

            if r.new_state:
                self.g.prev_state = self.g.state
                self.g.state = r.new_state

                log.info('%s -> %s', self.g.prev_state, self.g.state)

                if self.g.state == States.HERO_DEAD:
                    break

            if r.msg:
                self.g.msg_log.add(r.msg)

            # alternate actions
            if r.alt:
                self.g.action_queue.put(r.alt)


    def update_rendering(self):
        log.info('update_rendering:')

        if self.g.redraw:
            log.info('redraw:')
            # Reset the stage
            stage = self.g.dungeon.get_stage()

            self.g.fov_map = initialize_fov(stage)
            self.g.fov_recompute = True
            self.render_eng.con.clear()
            # libtcod.console_clear(con)

            self.g.redraw = False

        # Only recompute the fov if its the Players turn.
        if self.g.fov_recompute:
            log.info('fov_recompute:')
            recompute_fov(
                self.g.fov_map,
                self.g.hero.x,
                self.g.hero.y,
                config.fov_radius,
                config.fov_light_walls,
                config.fov_algorithm
            )

        # Render all entities
        self.render_eng.render_all(self.g, self.mouse)

        self.g.fov_recompute = False       # Mandatory

        # Presents everything on screen
        tcod.console_flush()

        # Clear all entities
        self.render_eng.clear_all(self.g.stage.entities)
