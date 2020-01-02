import tcod
from entity import Entity, get_blocking_entities_at_location
from render_functions import clear_all, render_all
from game_map import GameMap
from fov import initialize_fov, recompute_fov
from game_states import GameStates
from components import Fighter
from input_handling import handle_keys


def main():
    img_file = 'images/arial10x10.png'
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45
    room_max_size = 10
    room_min_size = 4
    max_rooms = 30
    max_monsters_per_room = 3

    fov_algorithm = 0               # 0 is default alg tcod uses
    fov_light_walls = True          # Light up walls we see
    fov_radius = 10                 # How far can we see?
    fov_recompute = True

    colors = {
        'dark_wall': tcod.Color(0, 0, 100),
        'dark_ground': tcod.Color(50, 50, 150),
        'light_wall': tcod.Color(130, 110, 50),
        'light_ground': tcod.Color(200, 180, 50)
    }

    # Create entities
    fighter_comp = Fighter(hp=30, defense=2, power=5)
    player = Entity(0, 0, '@', tcod.white, 'Player', blocks=True, fighter=fighter_comp)
    entities = [player]

    tcod.console_set_custom_font(img_file, tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

    # Creates the screen. (Boolean specifies full screen)
    tcod.console_init_root(screen_width, screen_height, 'libtcod tutorial revised', False)

    # Initialize the console
    con = tcod.console_new(screen_width, screen_height)

    # Initialize the game map
    game_map = GameMap(map_width, map_height)
    game_map.make_map(
        max_rooms,
        room_min_size,
        room_max_size,
        map_width,
        map_height,
        player,
        entities,
        max_monsters_per_room
    )

    # Initialize fov
    fov_map = initialize_fov(game_map)

    key = tcod.Key()
    mouse = tcod.Mouse()

    game_state = GameStates.PLAYERS_TURN

    # Game loop
    while not tcod.console_is_window_closed():
        # Capture new user input
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        # Render all entities
        render_all(con, entities, game_map, fov_map, fov_recompute, screen_width, screen_height, colors)

        fov_recompute = False       # Mandatory

        # Presents everything on screen
        tcod.console_flush()

        # Clear all entities
        clear_all(con, entities)

        # Get keyboard input
        action = handle_keys(key)

        move = action.get('move')
        gameexit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            dest_x = player.x + dx
            dest_y = player.y + dy

            if not game_map.is_blocked(dest_x, dest_y):
                target = get_blocking_entities_at_location(entities, dest_x, dest_y)

                if target:
                    # print('You kick the {} in the shins, much to its annoyance!'.format(target.name))
                    player.fighter.attack(target)
                else:

                    player.move(dx, dy)

                    # Need to redraw FOV
                    fov_recompute = True

                # Player's turn is over
                game_state = GameStates.ENEMY_TURN

        if gameexit:
            return True

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:

                if entity.ai:
                    entity.ai.take_turn(player, fov_map, game_map, entities)

            game_state = GameStates.PLAYERS_TURN


if __name__ == "__main__":
    main()
