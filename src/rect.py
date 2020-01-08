MIN_WALL_LEN = 3

class Rect(object):
    """Creates a rectangle object.
        Note: Each rectangle has a wall perimeter that is 1 unit thick.

        x/y: Must be 0 or positive value (no negative space)
        w/h: Must be 3 or more to create empty space within the rectangle.
    """

    def __init__(self, x, y, w, h):
        if x < 0 or y < 0:
            raise ValueError('x and y must be positive values!')

        if w < MIN_WALL_LEN or h < MIN_WALL_LEN:
            raise ValueError('w and h must be a minimum of {}!'.format(MIN_WALL_LEN))

        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        # Return the coordinates of the the center of the Rect
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)

    def intersect(self, other):
        # Returns True if this rectangle intersects with another one.
        return (self.x1 <= other.x2 and
                self.x2 >= other.x1 and
                self.y1 <= other.y2 and
                self.y2 >= other.y1)

    # def get_rnd_area_loc(occupied)
    # def get_rnd_wall_loc()
