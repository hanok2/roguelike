import tcod
from entity import Entity, get_blocking_entities_at_location
from render_functions import clear_all, render_all, RenderOrder
from game_map import GameMap
from fov import initialize_fov, recompute_fov
from game_states import GameStates
from components import Fighter
from inventory import Inventory
from input_handling import handle_keys
from death_functions import kill_monster, kill_player
from game_messages import Message, Messagelog


def main():
    img_file = 'images/arial10x10.png'
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 43
    room_max_size = 10
    room_min_size = 4
    max_rooms = 30
    max_monsters_per_room = 3
    max_items_per_room = 2
    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    msg_x = bar_width + 2
    msg_width = screen_width - bar_width - 2
    msg_height = panel_height - 1

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

    # Player components
    fighter_comp = Fighter(hp=30, defense=2, power=5)
    inv_comp = Inventory(26)

    # Create entities
    player = Entity(
        0, 0,
        '@',
        tcod.white,
        'Player',
        blocks=True,
        render_order=RenderOrder.ACTOR,
        fighter=fighter_comp,
        inv=inv_comp,
    )
    entities = [player]

    tcod.console_set_custom_font(img_file, tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

    # Creates the screen. (Boolean specifies full screen)
    tcod.console_init_root(screen_width, screen_height, 'libtcod tutorial revised', False)

    # Initialize the console
    con = tcod.console_new(screen_width, screen_height)

    # Initialize the panel
    panel = tcod.console_new(screen_width, panel_height)

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
        max_monsters_per_room,
        max_items_per_room
    )

    # Initialize fov
    fov_map = initialize_fov(game_map)

    msg_log = Messagelog(msg_x, msg_width, msg_height)

    key = tcod.Key()
    mouse = tcod.Mouse()

    game_state = GameStates.PLAYERS_TURN
    prev_game_state = game_state

    # Game loop
    while not tcod.console_is_window_closed():
        # Capture new user input
        # tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)


        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        # Render all entities
        render_all(
            con,
            panel,
            entities,
            player,
            game_map,
            fov_map,
            fov_recompute,
            msg_log,
            screen_width,
            screen_height,
            bar_width,
            panel_height,
            panel_y,
            mouse,
            colors,
            game_state
        )

        fov_recompute = False       # Mandatory

        # Presents everything on screen
        tcod.console_flush()

        # Clear all entities
        clear_all(con, entities)

        # Get keyboard input
        action = handle_keys(key, game_state)

        move = action.get('move')
        pickup = action.get('pickup')
        show_inv = action.get('inventory')
        drop_inv = action.get('drop_inv')
        inv_index = action.get('inv_index')
        gameexit = action.get('exit')
        fullscreen = action.get('fullscreen')

        player_turn_results = []

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            dest_x = player.x + dx
            dest_y = player.y + dy

            if not game_map.is_blocked(dest_x, dest_y):
                target = get_blocking_entities_at_location(entities, dest_x, dest_y)

                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)

                    # Need to redraw FOV
                    fov_recompute = True

                # Player's turn is over
                game_state = GameStates.ENEMY_TURN

        elif pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                item_pos_at_our_pos = entity.x == player.x and entity.y == player.y

                if entity.item and item_pos_at_our_pos:
                    pickup_results = player.inv.add_item(entity)
                    player_turn_results.extend(pickup_results)

                    break
            else:
                msg_log.add(Message('There is nothing here to pick up.', tcod.yellow))

        if show_inv:
            prev_game_state = game_state
            game_state = GameStates.INVENTORY

        if drop_inv:
            prev_game_state == game_state
            game_state = GameStates.DROP_INVENTORY

        if inv_index is not None and prev_game_state != GameStates.PLAYER_DEAD and inv_index < len(player.inv.items):
            item = player.inv.items[inv_index]

            # "using" the item
            # print(item)
            # player_turn_results.extend(player.inv.use(item))

            if game_state == GameStates.INVENTORY:
                player_turn_results.extend(player.inv.use(item))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inv.drop(item))



        if gameexit:
            if game_state in (GameStates.INVENTORY, GameStates.DROP_INVENTORY):
                game_state = prev_game_state
            else:
                return True

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        # Process player results
        for result in player_turn_results:
            msg = result.get('msg')
            dead_entity = result.get('dead')
            item_added = result.get('item_added')
            item_consumed = result.get('consumed')
            item_dropped = result.get('item_dropped')

            if msg:
                msg_log.add(msg)

            if dead_entity:
                if dead_entity == player:
                    msg, game_state = kill_player(dead_entity)
                else:
                    msg = kill_monster(dead_entity)

                msg_log.add(msg)

            if item_added:
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if item_dropped:
                entities.append(item_dropped)
                game_state = GameStates.ENEMY_TURN


        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:

                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for result in enemy_turn_results:
                        msg = result.get('msg')
                        dead_entity = result.get('dead')

                        if msg:
                            msg_log.add(msg)

                        if dead_entity:
                            if dead_entity == player:
                                msg, game_state = kill_player(dead_entity)
                            else:
                                msg = kill_monster(dead_entity)

                            msg_log.add(msg)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break

            else:
                game_state = GameStates.PLAYERS_TURN


if __name__ == "__main__":
    main()
