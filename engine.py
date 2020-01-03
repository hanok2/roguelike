import tcod
from entity import get_blocking_entities_at_location
from render_functions import clear_all, render_all
from fov import initialize_fov, recompute_fov
from game_states import GameStates
from input_handling import handle_keys, handle_mouse
from death_functions import kill_monster, kill_player
from game_messages import Message
from initialize_new_game import CONSTANTS, GAME_DATA


def main():
    img_file = 'images/arial10x10.png'
    fov_recompute = True
    tcod.console_set_custom_font(img_file, tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

    # Creates the screen. (Boolean specifies full screen)
    tcod.console_init_root(
        CONSTANTS['screen_width'],
        CONSTANTS['screen_height'],
        'libtcod tutorial revised',
        False
    )

    # Initialize the console
    con = tcod.console_new(
        CONSTANTS['screen_width'],
        CONSTANTS['screen_height']
    )

    # Initialize the panel
    panel = tcod.console_new(
        CONSTANTS['screen_width'],
        CONSTANTS['panel_height']
    )
    # Initialize game data
    player = GAME_DATA['player']
    entities = GAME_DATA['entities']
    game_map = GAME_DATA['game_map']
    msg_log = GAME_DATA['msg_log']
    game_state = GAME_DATA['game_state']

    # Initialize fov
    fov_map = initialize_fov(game_map)
    key = tcod.Key()
    mouse = tcod.Mouse()

    prev_game_state = game_state

    # Keep track of any targeting items that were selected.
    targeting_item = None

    # Game loop
    while not tcod.console_is_window_closed():
        # Capture new user input
        # tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)


        if fov_recompute:
            recompute_fov(
                fov_map,
                player.x,
                player.y,
                CONSTANTS['fov_radius'],
                CONSTANTS['fov_light_walls'],
                CONSTANTS['fov_algorithm']
            )

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
            CONSTANTS['screen_width'],
            CONSTANTS['screen_height'],
            CONSTANTS['bar_width'],
            CONSTANTS['panel_height'],
            CONSTANTS['panel_y'],
            mouse,
            CONSTANTS['colors'],
            game_state
        )

        fov_recompute = False       # Mandatory

        # Presents everything on screen
        tcod.console_flush()

        # Clear all entities
        clear_all(con, entities)

        # Get keyboard/mouse input
        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        move = action.get('move')
        pickup = action.get('pickup')
        show_inv = action.get('inventory')
        drop_inv = action.get('drop_inv')
        inv_index = action.get('inv_index')
        gameexit = action.get('exit')
        fullscreen = action.get('fullscreen')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

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

        if inv_index is not None and prev_game_state != GameStates.PLAYER_DEAD and inv_index < len(GAME_DATA['player'].inv.items):
            item = player.inv.items[inv_index]

            # "using" the item
            # print(item)
            # player_turn_results.extend(player.inv.use(item))

            if game_state == GameStates.INVENTORY:
                # player_turn_results.extend(player.inv.use(item))
                player_turn_results.extend(
                    player.inv.use(
                        item, entities=entities, fov_map=fov_map
                    )
                )

            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inv.drop(item))

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inv.use(
                    targeting_item,
                    entities=entities,
                    fov_map=fov_map,
                    target_x=target_x,
                    target_y=target_y
                )
                player_turn_results.extend(item_use_results)

            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if gameexit:
            if game_state in (GameStates.INVENTORY, GameStates.DROP_INVENTORY):
                game_state = prev_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
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
            targeting = result.get('targeting')
            targeting_cancelled = result.get('targeting_cancelled')

            if msg:
                msg_log.add(msg)

            if targeting_cancelled:
                game_state = prev_game_state
                msg_log.add(Message('Targeting cancelled'))

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

            if targeting:
                # Set to PLAYERS_TURN so that if cancelled, we don't go back to inv.
                prev_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING
                targeting_item = targeting
                msg_log.add(targeting_item.item.targeting_msg)


            if item_dropped:
                entities.append(item_dropped)
                game_state = GameStates.ENEMY_TURN


        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:

                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(
                        player,
                        fov_map,
                        game_map,
                        entities
                    )

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
