import tcod


def initialize_fov(game_map):
    # Deprecated since version 4.5: Use the tcod.map module for working with
    # field-of-view, or tcod.path for working with path-finding.
    # fov_map = tcod.map_new(w=game_map.width, h=game_map.height)

    fov_map = tcod.map.Map(
        width=game_map.width,
        height=game_map.height
    )

    for y in range(game_map.height):
        for x in range(game_map.width):

            # Note: This function is slow
            # Deprecated since version 4.5: Use tcod.map.Map.transparent and tcod.map.Map.walkable arrays to set these properties.
            # parameters: m, x, y, isTrans, isWalk
            # tcod.map_set_properties( m=fov_map, x=x, y=y, isTrans=not game_map.tiles[x][y].block_sight, isWalk=not game_map.tiles[x][y].blocked)

            fov_map.transparent[y, x] = not game_map.tiles[x][y].block_sight
            fov_map.walkable[y, x] = not game_map.tiles[x][y].blocked

    return fov_map


def recompute_fov(fov_map, x, y, radius, light_walls=True, algorithm=0):
    # Deprecated since version 4.5: Use tcod.map.Map.compute_fov instead.

    # tcod.map_compute_fov( m=fov_map, x=x, y=y, radius=radius, light_walls=light_walls, algo=algorithm)

    # fov_map.compute_fov(
        # x=x,
        # y=y,
        # radius=radius,
        # light_walls=light_walls,
        # algorithm=algorithm
    # )

    fov_map.compute_fov(x=x, y=y)
