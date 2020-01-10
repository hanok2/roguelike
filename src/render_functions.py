from enum import Enum, auto
import tcod
from . import config
from .states import States
from .menus import inv_menu, lvl_up_menu, char_scr


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

        # Initialize the consoles
        self.con = tcod.console.Console(width=config.scr_width, height=config.scr_height)
        self.panel = tcod.console.Console(width=config.scr_width, height=config.panel_height)
        self.msg_panel = tcod.console.Console(width=config.scr_width, height=config.msg_height)

    def render_all(self, dungeon, fov_map, fov_recompute, msg_log, mouse, state, turns):
        game_map = dungeon.current_map()

        # Draw all the tiles in the game map
        if fov_recompute:
            self.render_map_tiles(game_map, fov_map)

        # Draw all entities in the list
        sorted_entities = sorted(game_map.entities, key=lambda x: x.render_order.value)

        for entity in sorted_entities:
            self.draw_entity(entity, fov_map, game_map)

        # Display console
        self.con.blit(
            dest=self.root,
            dest_x=0,
            dest_y=config.msg_height,
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

            inv_menu(self, inv_title, dungeon.hero, 50)

        elif state == States.LEVEL_UP:
            lvl_up_menu(
                self,
                'Level up! Choose a stat to raise:',
                dungeon.hero,
                40,
            )

        elif state == States.SHOW_STATS:
            char_scr(self, dungeon.hero)

        self.panel.default_bg = tcod.black
        self.panel.clear()

        self.msg_panel.default_bg = tcod.black
        self.msg_panel.clear()

        self.render_status_bar(dungeon, fov_map, mouse, turns)
        self.render_console_messages(msg_log)


    def render_map_tiles(self, game_map, fov_map):
        # visible = fov_map.fov[:]

        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = fov_map.fov[y, x]

                wall = game_map.tiles[x][y].block_sight

                # Tiles within field-of-vision
                if visible:
                    if wall:
                        tcod.console_put_char_ex(
                            con=self.con,
                            x=x, y=y,
                            c='#',
                            fore=tcod.white,
                            back=tcod.black,
                        )
                    else:
                        tcod.console_put_char_ex(
                            con=self.con,
                            x=x, y=y,
                            c='.',
                            fore=tcod.white,
                            back=tcod.black
                        )

                    # It's visible therefore explored
                    game_map.tiles[x][y].explored = True

                # Tiles outside field-of-vision
                elif game_map.tiles[x][y].explored:
                    if wall:
                        tcod.console_put_char_ex(
                            con=self.con,
                            x=x, y=y,
                            c='#',
                            fore=tcod.white,
                            back=tcod.black,
                        )

                    else:
                        tcod.console_put_char_ex(
                            con=self.con,
                            x=x, y=y,
                            c='.',
                            fore=tcod.white,
                            back=tcod.black,
                        )

    def clear_all(self, entities):
        # Clear all entities on the console
        for entity in entities:
            self.clear_entity(entity)

    def clear_entity(self, entity):
        # Erase the character that represents this object
        tcod.console_put_char(
            con=self.con,
            x=entity.x, y=entity.y,
            c=' ',
            flag=tcod.BKGND_NONE
        )

    def draw_entity(self, entity, fov_map, game_map):
        # Draw an entity on the console
        entity_in_fov = fov_map.fov[entity.y, entity.x]
        stair_entity = ((entity.stair_down or entity.stair_up) and game_map.tiles[entity.x][entity.y].explored)

        if entity_in_fov or stair_entity:
            self.con.default_fg = entity.color

            tcod.console_put_char(
                con=self.con,
                x=entity.x, y=entity.y,
                c=entity.char,
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
        for y, msg in enumerate(msg_log.current_msgs()):
            self.msg_panel.default_fg = tcod.white
            self.msg_panel.print(x=msg_log.x, y=y, string=msg, alignment=tcod.LEFT)

        self.msg_panel.blit(
            dest=self.root,
            dest_x=0, dest_y=0,
            src_x=0, src_y=0,
            width=config.scr_width,
            height=config.msg_height,
        )

    def render_status_bar(self, dungeon, fov_map, mouse, turns):
        hero = dungeon.hero
        game_map = dungeon.current_map()

        # Display dungeon level
        self.panel.print(
            x=1, y=1,
            string='DungeonLvl: {}'.format(game_map.dungeon_lvl),
            alignment=tcod.LEFT,
        )

        # Display HP bar
        self.render_bar(
            1, 2,
            config.bar_width,
            'HP',
            hero.fighter.hp,
            hero.fighter.max_hp,
            tcod.light_red,
            tcod.darker_red
        )

        # todo: Display XP bar
        self.render_bar(
            1, 4,
            config.bar_width,
            'XP',
            hero.lvl.current_xp,
            hero.lvl.xp_to_next_lvl,
            tcod.light_blue,
            tcod.darker_blue
        )

        # todo: Display level
        self.panel.print(
            x=22, y=2,
            string='Lvl:{}'.format(hero.lvl.current_lvl),
        )

        # todo: Display power
        self.panel.print(
            x=29, y=2,
            string='Pow:{}'.format(hero.fighter.power),
        )

        # todo: Display defense
        self.panel.print(
            x=36, y=2,
            string='Def:{}'.format(hero.fighter.defense),
        )

        # todo: Display turns
        self.panel.print(
            x=55, y=2,
            string='Turn: {}'.format(turns),
        )

        # Display entity under mouse
        self.panel.print(
            x=1, y=0,
            string=get_names_under_mouse(mouse, game_map.entities, fov_map),
            alignment=tcod.LEFT,
        )

        self.panel.default_fg = tcod.light_gray

        self.panel.blit(
            dest=self.root,
            dest_x=0, dest_y=config.panel_y,
            src_x=0, src_y=0,
            width=config.scr_width,
            height=config.panel_height,
        )


def get_names_under_mouse(mouse, entities, fov_map):
    # note: Due to the message console - we have to offset the y.
    x, y = mouse.cx, mouse.cy - config.msg_height

    names = [e.name for e in entities if e.x == x and e.y == y and fov_map.fov[e.y, e.x]]
    names = ', '.join(names)
    return names.capitalize()
