class ActionQueue(object):
    """ A FIFI queue. """
    # todo: Protect queue
    # todo: Implement put
    # todo: Implement get

    def __init__(self):
        self.queue = []

    def __len__(self):
        return len(self.queue)

    def put(self, item):
        self.queue.append(item)

    def get(self):
        item = self.queue.pop(0)
        return item

    def empty(self):
        return len(self.queue) == 0
