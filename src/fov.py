import tcod


def initialize_fov(game_map):
    fov_map = tcod.map.Map(width=game_map.width, height=game_map.height)

    for y in range(game_map.height):
        for x in range(game_map.width):
            fov_map.transparent[y, x] = not game_map.tiles[x][y].block_sight
            fov_map.walkable[y, x] = not game_map.tiles[x][y].blocked

    return fov_map


def recompute_fov(fov_map, x, y, radius, light_walls=True, algorithm=0):

    fov_map.compute_fov(
        x=x,
        y=y,
        radius=radius,
        light_walls=light_walls,
        algorithm=algorithm
    )
