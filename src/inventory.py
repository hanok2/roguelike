class Inventory(object):
    # Add a contains() method

    def __init__(self, owner, capacity):
        if capacity <= 0:
            raise ValueError('capacity needs to be a positive number!')

        self.owner = owner
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        if len(self.items) >= self.capacity:
            return False

        self.items.append(item)
        return True

    def rm_item(self, item):
        if item not in self.items:
            return False
        self.items.remove(item)
        return True
