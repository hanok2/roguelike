import tcod
from .config import RenderOrder
from . import entity

# Component
class Stairs(object):
    def __init__(self, floor):
        self.floor = floor


class StairUp(entity.Entity):
    def __init__(self, x, y, floor):
        super().__init__(
            x=x,
            y=y,
            blocks=False,
            char='<',
            color=tcod.white,
            name='Stairs Up',
            render_order=RenderOrder.STAIRS
        )

        self.stair_up = Stairs(floor)


class StairDown(entity.Entity):
    def __init__(self, x, y, floor):
        super().__init__(
            x=x,
            y=y,
            blocks=False,
            char='>',
            color=tcod.white,
            name='Stairs Down',
            render_order=RenderOrder.STAIRS
        )

        self.stair_down = Stairs(floor)
