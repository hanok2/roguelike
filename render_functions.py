from enum import Enum, auto
import tcod
import config
from states import States
from menus import inv_menu, lvl_up_menu, char_scr


class RenderOrder(Enum):
    STAIRS = auto()
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()


def render_all(root, con, panel, entities, hero, game_map, fov_map, fov_recompute, msg_log, mouse, state):
    # Draw all the tiles in the game map

    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                # Deprecated since version 4.5: Use tcod.map.Map.fov to check this property.
                # This function is slow
                visible = tcod.map_is_in_fov(m=fov_map, x=x, y=y)

                # visible = fov_map.fov

                wall = game_map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        tcod.console_set_char_background(
                            con=con,
                            x=x, y=y,
                            col=config.colors.get('light_wall'),
                            flag=tcod.BKGND_SET
                        )
                    else:
                        tcod.console_set_char_background(
                            con=con,
                            x=x, y=y,
                            col=config.colors.get('light_ground'),
                            flag=tcod.BKGND_SET
                        )

                    # It's visible therefore explored
                    game_map.tiles[x][y].explored = True

                elif game_map.tiles[x][y].explored:
                    if wall:
                        tcod.console_set_char_background(
                            con=con,
                            x=x, y=y,
                            col=config.colors.get('dark_wall'),
                            flag=tcod.BKGND_SET
                        )
                    else:
                        tcod.console_set_char_background(
                            con=con,
                            x=x, y=y,
                            col=config.colors.get('dark_ground'),
                            flag=tcod.BKGND_SET
                        )

	# Draw all entities in the list
    sorted_entities = sorted(entities, key=lambda x: x.render_order.value)

    for entity in sorted_entities:
        draw_entity(con, entity, fov_map, game_map)

    # Display console
    con.blit(
        dest=root,
        dest_x=0,
        dest_y=0,
        src_x=0, src_y=0,
        width=config.scr_width,
        height=config.scr_height,
    )

    if state in (States.SHOW_INV, States.DROP_INV):
        if state == States.SHOW_INV:
            inv_title = 'Press the key next to an item to use it, or ESC to cancel.\n'
        else:
            inv_title = 'Press the key next to an item to drop it, or ESC to cancel.\n'

        inv_menu(
            root,
            con,
            inv_title,
            hero,
            50,
            config.scr_width,
            config.scr_height
        )

    elif state == States.LEVEL_UP:
        lvl_up_menu(
            root,
            con,
            'Level up! Choose a stat to raise:',
            hero,
            40,
            config.scr_width,
            config.scr_height
        )

    elif state == States.SHOW_STATS:
        char_scr(root, hero, 30, 10, config.scr_width, config.scr_height)

    panel.default_bg = tcod.black

    panel.clear()

    # Print the game messages, one line at a time
    y = 1
    for msg in msg_log.messages:
        panel.default_fg = tcod.white

        panel.print(x=msg_log.x, y=y, string=msg, alignment=tcod.LEFT)
        y += 1

    render_bar(
        panel,
        1, 1,
        config.bar_width,
        'HP',
        hero.fighter.hp,
        hero.fighter.max_hp,
        tcod.light_red,
        tcod.darker_red
    )

    # Display level
    panel.print(
        x=1, y=3,
        string='Dungeon level: {}'.format(game_map.dungeon_lvl),
        alignment=tcod.LEFT,
    )

    panel.default_fg = tcod.light_gray

    panel.print(
        x=1, y=0,
        string=get_names_under_mouse(mouse, entities, fov_map),
        alignment=tcod.LEFT,

    )

    panel.blit(
        dest=root,
        dest_x=0, dest_y=config.panel_y,
        src_x=0, src_y=0,
        width=config.scr_width,
        height=config.panel_height,
    )


def clear_all(con, entities):
    # Clear all entities on the console
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity, fov_map, game_map):
    # Draw an entity on the console
    # todo: Break into nicer boolean later...

    # Deprecated since version 4.5: Use tcod.map.Map.fov to check this property.
    if tcod.map_is_in_fov(fov_map, entity.x, entity.y) or (entity.stairs and game_map.tiles[entity.x][entity.y].explored):
        con.default_fg = entity.color

        tcod.console_put_char(
            con=con,
            x=entity.x, y=entity.y,
            c=entity.char,
            flag=tcod.BKGND_NONE
        )


def clear_entity(con, entity):
    # Erase the character that represents this object
    tcod.console_put_char(
        con=con,
        x=entity.x, y=entity.y,
        c=' ',
        flag=tcod.BKGND_NONE
    )

def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)
    panel.default_bg = back_color

    panel.rect(
        x=x, y=y,
        width=total_width,
        height=1,
        clear=False,
        bg_blend=tcod.BKGND_SCREEN
    )

    panel.default_bg = bar_color

    if bar_width > 0:
        panel.rect(
            x=x, y=y,
            width=bar_width,
            height=1,
            clear=False,
            bg_blend=tcod.BKGND_SCREEN
        )

    panel.default_fg = tcod.white

    panel.print(
        x=int(x + total_width / 2), y=y,
        string='{}: {}/{}'.format(name, value, maximum),
        alignment=tcod.CENTER
    )

def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)

    # Deprecated since version 4.5: Use tcod.map.Map.fov to check this property.
    names = [entity.name for entity in entities
             if entity.x == x and entity.y == y and
             tcod.map_is_in_fov(m=fov_map, x=entity.x, y=entity.y)]

    names = ', '.join(names)

    return names.capitalize()
