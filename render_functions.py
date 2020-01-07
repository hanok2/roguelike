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


class RenderEngine(object):
    def __init__(self):
        # Setup the font first
        tcod.console_set_custom_font(
            fontFile=config.tileset_file,
            flags=tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD
        )

        # Creates the screen.
        # Set up the primary display and return the root console.
        self.root = tcod.console_init_root(
            w=config.scr_width,
            h=config.scr_height,
            title=config.window_title,
            fullscreen=False
        )

        # Initialize the console
        self.con = tcod.console.Console(width=config.scr_width, height=config.scr_height)

        # Initialize the panel
        self.panel = tcod.console.Console(width=config.scr_width, height=config.panel_height)

    def render_all(self, entities, hero, game_map, fov_map, fov_recompute, msg_log, mouse, state):
        # Draw all the tiles in the game map
        if fov_recompute:
            self.render_map_tiles(game_map, fov_map)

        # Draw all entities in the list
        sorted_entities = sorted(entities, key=lambda x: x.render_order.value)

        for entity in sorted_entities:
            self.draw_entity(entity, fov_map, game_map)

        # Display console
        self.con.blit(
            dest=self.root,
            dest_x=0,
            dest_y=0,
            src_x=0, src_y=0,
            width=config.scr_width,
            height=config.scr_height,
        )

        # Display inventory menu if necessary
        if state in (States.SHOW_INV, States.DROP_INV):
            if state == States.SHOW_INV:
                inv_title = 'Press the key next to an item to use it, or ESC to cancel.\n'
            else:
                inv_title = 'Press the key next to an item to drop it, or ESC to cancel.\n'

            inv_menu(self, inv_title, hero, 50)

        elif state == States.LEVEL_UP:
            lvl_up_menu(
                self.root,
                self.con,
                'Level up! Choose a stat to raise:',
                hero,
                40,
            )

        elif state == States.SHOW_STATS:
            char_scr(self, hero)

        self.panel.default_bg = tcod.black

        self.panel.clear()
        self.render_console_messages(msg_log)
        self.render_status_bar(hero, entities, game_map, fov_map, mouse)


    def render_map_tiles(self, game_map, fov_map):
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
                            con=self.con,
                            x=x, y=y,
                            col=config.colors.get('light_wall'),
                            flag=tcod.BKGND_SET
                        )
                    else:
                        tcod.console_set_char_background(
                            con=self.con,
                            x=x, y=y,
                            col=config.colors.get('light_ground'),
                            flag=tcod.BKGND_SET
                        )

                    # It's visible therefore explored
                    game_map.tiles[x][y].explored = True

                elif game_map.tiles[x][y].explored:
                    if wall:
                        tcod.console_set_char_background(
                            con=self.con,
                            x=x, y=y,
                            col=config.colors.get('dark_wall'),
                            flag=tcod.BKGND_SET
                        )
                    else:
                        tcod.console_set_char_background(
                            con=self.con,
                            x=x, y=y,
                            col=config.colors.get('dark_ground'),
                            flag=tcod.BKGND_SET
                        )

    def clear_all(self, entities):
        # Clear all entities on the console
        for entity in entities:
            self.clear_entity(entity)

    def draw_entity(self, entity, fov_map, game_map):
        # Draw an entity on the console
        # todo: Break into nicer boolean later...

        # Deprecated since version 4.5: Use tcod.map.Map.fov to check this property.
        if tcod.map_is_in_fov(fov_map, entity.x, entity.y) or (entity.stairs and game_map.tiles[entity.x][entity.y].explored):
            self.con.default_fg = entity.color

            tcod.console_put_char(
                con=self.con,
                x=entity.x, y=entity.y,
                c=entity.char,
                flag=tcod.BKGND_NONE
            )

    def clear_entity(self, entity):
        # Erase the character that represents this object
        tcod.console_put_char(
            con=self.con,
            x=entity.x, y=entity.y,
            c=' ',
            flag=tcod.BKGND_NONE
        )

    def render_bar(self, x, y, total_width, name, value, maximum, bar_color, back_color):
        bar_width = int(float(value) / maximum * total_width)
        self.panel.default_bg = back_color

        self.panel.rect(
            x=x, y=y,
            width=total_width,
            height=1,
            clear=False,
            bg_blend=tcod.BKGND_SCREEN
        )

        self.panel.default_bg = bar_color

        if bar_width > 0:
            self.panel.rect(
                x=x, y=y,
                width=bar_width,
                height=1,
                clear=False,
                bg_blend=tcod.BKGND_SCREEN
            )

        self.panel.default_fg = tcod.white

        self.panel.print(
            x=int(x + total_width / 2), y=y,
            string='{}: {}/{}'.format(name, value, maximum),
            alignment=tcod.CENTER
        )

    def render_console_messages(self, msg_log):
        # Print the game messages, one line at a time
        y = 1
        for msg in msg_log.messages:
            self.panel.default_fg = tcod.white
            self.panel.print(x=msg_log.x, y=y, string=msg, alignment=tcod.LEFT)
            y += 1


    def render_status_bar(self, hero, entities, game_map, fov_map, mouse):
        self.render_bar(
            1, 1,
            config.bar_width,
            'HP',
            hero.fighter.hp,
            hero.fighter.max_hp,
            tcod.light_red,
            tcod.darker_red
        )

        # Display level
        self.panel.print(
            x=1, y=3,
            string='Dungeon level: {}'.format(game_map.dungeon_lvl),
            alignment=tcod.LEFT,
        )

        self.panel.default_fg = tcod.light_gray

        self.panel.print(
            x=1, y=0,
            string=get_names_under_mouse(mouse, entities, fov_map),
            alignment=tcod.LEFT,
        )

        self.panel.blit(
            dest=self.root,
            dest_x=0, dest_y=config.panel_y,
            src_x=0, src_y=0,
            width=config.scr_width,
            height=config.panel_height,
        )


def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)

    # Deprecated since version 4.5: Use tcod.map.Map.fov to check this property.
    names = [entity.name for entity in entities
             if entity.x == x and entity.y == y and
             tcod.map_is_in_fov(m=fov_map, x=entity.x, y=entity.y)]

    names = ', '.join(names)

    return names.capitalize()
