class ActionQueue(object):
    """ A FIFI queue. """
    def __init__(self):
        self.queue = []

    def __len__(self):
        return len(self.queue)
