import tcod
from . import config
from .config import States
from . import menus


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
        stage = dungeon.get_stage()

        # Draw all the tiles in the stage
        if fov_recompute:
            self.render_tiles(stage, fov_map)

        # Draw all entities in the list
        sorted_entities = sorted(stage.entities, key=lambda x: x.render_order.value)

        for entity in sorted_entities:
            self.draw_entity(entity, fov_map, stage)

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
            header, options = menus.inv_options(dungeon.hero, state)
            self.render_menu(header, options, width=50)

        elif state == States.LEVEL_UP:
            # Render the level-up menu
            header, options = menus.lvl_up_options()
            self.render_menu(header, options, width=40)

        elif state == States.SHOW_STATS:
            self.render_char_scr(dungeon.hero)

        self.panel.default_bg = tcod.black
        self.panel.clear()

        self.msg_panel.default_bg = tcod.black
        self.msg_panel.clear()

        self.render_status_bar(dungeon, fov_map, mouse, turns)
        self.render_console_messages(msg_log)

    def render_tiles(self, stage, fov_map):
        # visible = fov_map.fov[:]

        for y in range(stage.height):
            for x in range(stage.width):
                visible = fov_map.fov[y, x]

                wall = stage.tiles[x][y].block_sight

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
                    stage.tiles[x][y].explored = True

                # Tiles outside field-of-vision
                elif stage.tiles[x][y].explored:
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

    def draw_entity(self, entity, fov_map, stage):
        # Draw an entity on the console
        entity_in_fov = fov_map.fov[entity.y, entity.x]

        # todo: Break into nicer booleans
        stair_entity = ((entity.has_comp('stair_down') or entity.has_comp('stair_up')) and stage.tiles[entity.x][entity.y].explored)

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
        stage = dungeon.get_stage()

        # Display dungeon level
        self.panel.print(
            x=1, y=1,
            string='DungeonLvl: {}'.format(stage.dungeon_lvl),
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

        # Display XP bar
        self.render_bar(
            1, 4,
            config.bar_width,
            'XP',
            hero.lvl.current_xp,
            hero.lvl.xp_to_next_lvl,
            tcod.light_blue,
            tcod.darker_blue
        )

        # Display level
        self.panel.print(
            x=22, y=2,
            string='Lvl:{}'.format(hero.lvl.current_lvl),
        )

        # Display power
        self.panel.print(x=29, y=2, string='Pow:{}'.format(hero.fighter.power))

        # Display defense
        self.panel.print(x=36, y=2, string='Def:{}'.format(hero.fighter.defense))

        # todo: Display turns
        self.panel.print(x=55, y=2, string='Turn: {}'.format(turns))

        # Display entity under mouse
        self.panel.print(
            x=1, y=0,
            string=get_names_under_mouse(mouse, stage.entities, fov_map),
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

    def render_menu(self, header, options, width):
        """ Display a menu of options. Each option has a letter to the left side."""
        if len(options) > config.MAX_MENU_ITEMS:
            raise ValueError('Cannot have a menu with more than 26 options.')

        # Calculate total height for the header (after auto-wrap) and one line per option
        header_height = tcod.console_get_height_rect(
            con=self.con,
            x=0, y=0,
            w=width,
            h=config.scr_height,
            fmt=header
        )

        height = len(options) + header_height

        # Create an off-screen console that represents the menu's window
        window = tcod.console.Console(width=width, height=height)

        window.default_fg = tcod.white
        window.default_bg = tcod.black

        # Print a string constrained to a rectangle with blend and alignment.
        window.print(
            x=0, y=0,
            string=header,
            alignment=tcod.LEFT
        )

        # Print all the options
        y = header_height

        for k, v in options.items():
            text = '({}) {}'.format(k, v)

            window.print(
                x=0, y=y,
                string=text,
                alignment=tcod.LEFT
            )
            y += 1

        x = int(config.scr_width / 2 - width / 2)
        y = 5

        # Blit the contents of "window" to the root console
        window.blit(
            dest=self.root,
            dest_x=x, dest_y=y,
            src_x=0, src_y=0,
            width=width,
            height=height,
        )

    def render_main_menu(self, menu_img):
        """ Displays the main menu for the game."""

        tcod.image_blit_2x(image=menu_img, console=self.root, dx=0, dy=0)

        self.root.default_fg=tcod.light_yellow

        # Display game title
        title_x = int(config.scr_width / 2)
        title_y = 3

        self.root.print(x=title_x, y=title_y, string=config.game_title, alignment=tcod.CENTER)

        # Display author
        author_x = int(config.scr_width / 2)
        author_y = int(config.scr_height - 2)

        self.root.print(x=author_x, y=author_y, string='By {}'.format(config.author), alignment=tcod.CENTER)

        # Display main menu options
        options = menus.main_menu_options()
        self.render_menu('', options, 24)

    def render_msg_box(self, header, width):
        self.render_menu(header, {}, width)

    def render_char_scr(self, hero):
        """ Displays a windows showing the hero's current stats and experience."""
        window = tcod.console.Console(
            width=config.char_scr_width,
            height=config.char_scr_height
        )

        window.default_fg = tcod.white
        info = menus.hero_info(hero)

        for i, row in enumerate(info):
            window.print_box(
                x=0, y=i+1,
                width=config.char_scr_width,
                height=config.char_scr_height,
                string=row,
                bg=tcod.black,
                alignment=tcod.LEFT,
            )

        x = config.scr_width // 2 - config.char_scr_width // 2
        y = 5

        window.blit(
            dest=self.root,
            dest_x=x, dest_y=y,
            src_x=0, src_y=0,
            width=config.char_scr_width,
            height=config.char_scr_height,
        )


def get_names_under_mouse(mouse, entities, fov_map):
    # note: Due to the message console - we have to offset the y.
    x, y = mouse.cx, mouse.cy - config.msg_height

    names = [e.name for e in entities if e.x == x and e.y == y and fov_map.fov[e.y, e.x]]
    names = ', '.join(names)
    return names.capitalize()
