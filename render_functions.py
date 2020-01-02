import tcod


def render_all(con, entities, screen_width, screen_height):
	# Draw all entities in the list
    for entity in entities:
        draw_entity(con, entity)

    tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)


def clear_all(con, entities):
    # Clear all entities on the console
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity):
    # Draw an entity on the console
    tcod.console_set_default_foreground(con, entity.color)
    tcod.console_put_char(con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)


def clear_entity(con, entity):
    # Erase the character that represents this object
    tcod.console_put_char(con, entity.x, entity.y, ' ', tcod.BKGND_NONE)
