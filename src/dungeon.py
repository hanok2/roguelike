from . import config
from . import stages


class Dungeon(object):
    def __init__(self, hero):
        self.hero = hero
        self.stages = []

        # Note: Can we fix this with a property? To match up with Stages?
        self.current_stage = 0

        # Generate the first level on initialization
        self.mk_next_stage()

        hero_start_x, hero_start_y = self.stages[0].rooms[0].center()
        self.move_hero(0, hero_start_x, hero_start_y)

        self.get_stage().populate()

    # def current_lvl(self):
        # Find the hero and return the level the hero is on.

    def get_stage(self):
        # todo: Returns the specified stage, otherwise returns the stage the
        # hero is currently on
        return self.stages[self.current_stage]

    def mk_next_stage(self):
        # Generate next dungeon level
        level_depth = len(self.stages) + 1
        new_stage = stages.Stage(config.stage_width, config.stage_height, level_depth)
        new_stage.mk_stage()
        self.stages.append(new_stage)

    def hero_at_stairs(self, stair_char):
        for e in self.get_stage().entities:
            if stair_char == '>' and e.has_comp('stair_down'):
                return e.x == self.hero.x and e.y == self.hero.y
            if stair_char == '<' and e.has_comp('stair_up'):
                return e.x == self.hero.x and e.y == self.hero.y
        return False

    def move_downstairs(self):
        """ Removes the hero from the current level and places them at the
            up-stair at the next level.
            First checks if the hero is at a down-stair. If they are, proceeds
            moving the hero and returns True, otherwise returns False.
        """
        down_stair = self.get_stage().find_stair('>')

        if self.hero.x == down_stair.x and self.hero.y == down_stair.y:
            next_lvl = self.current_stage + 1
            hero_start_x, hero_start_y = self.stages[next_lvl].rooms[0].center()
            return self.move_hero(next_lvl, hero_start_x, hero_start_y)

        return False

    def move_upstairs(self):
        """ Removes the hero from the current level and places them at the
            down-stair at the previous level.
            First checks if the hero is at an up-stair. If they are, proceeds
            moving the hero and returns True, otherwise returns False.
        """
        up_stair = self.get_stage().find_stair('<')

        if self.hero.x == up_stair.x and self.hero.y == up_stair.y:
            next_lvl = self.current_stage - 1
            hero_start_x, hero_start_y = self.stages[next_lvl].rooms[-1].center()
            return self.move_hero(next_lvl, hero_start_x, hero_start_y)

        return False

    def move_hero(self, dest_stage_index, dest_x, dest_y):
        """Moves the hero from the current to the destination level at the
            specified x and y coordinates.
            If the destination is a wall or unoccupied, we won't be able to move
            the hero and will return False.
            If the move succeeds, returns True.

            For future: Might be good to track the Hero's current level.
        """
        # Check the destination:
        # Does the destination level exist??

        # Is it a wall?
        src_stage = self.stages[dest_stage_index]
        if src_stage.tiles[dest_x][dest_y].blocked:
            return False

        # Is there a blocking monster there?
        blockers = [e for e in src_stage.entities if e.blocks]
        for e in blockers:
            if e.x == dest_x and e.y == dest_y:
                return False

        # Search for the hero(If not found - that is ok.)
        # If found, keep current location

        # Remove the hero
        src_stage.rm_hero()

        # Place the hero at the destination
        self.stages[dest_stage_index].entities.append(self.hero)

        # Update hero x/y
        self.hero.x, self.hero.y = dest_x, dest_y

        # Update current_lvl
        self.current_stage = dest_stage_index

        return True
