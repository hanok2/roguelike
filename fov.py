import tcod

def initialize_fov(game_map):
    fov_map = tcod.map_new(game_map.width, game_map.height)

    for y in range(game_map.height):
        for x in range(game_map.width):
            # Note: This function is slow
            # Deprecated since version 4.5: Use tcod.map.Map.transparent and tcod.map.Map.walkable arrays to set these properties.
            # parameters: m, x, y, isTrans, isWalk
            tcod.map_set_properties(
                fov_map,
                x,
                y,
                not game_map.tiles[x][y].block_sight,
                not game_map.tiles[x][y].blocked
            )

    return fov_map

def recompute_fov(fov_map, x, y, radius, light_walls=True, algorithm=0):
    tcod.map_compute_fov(fov_map, x, y, radius, light_walls, algorithm)
