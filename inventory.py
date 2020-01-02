import tcod
from game_messages import Message

class Inventory(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []


    def add_item(self, item):
        results = []

        if len(self.items) >= self.capacity:
            results.append({
                'item_added': None,
                'msg': Message('You cannot carry any more, your inventory is full.', tcod.yellow)
            })
        else:
            results.append({
                'item_added': item,
                'msg': Message('You pick up the {}!'.format(item.name), tcod.blue)
            })

            self.items.append(item)

        return results
