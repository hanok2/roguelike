import textwrap


class MsgLog(object):
    def __init__(self, x, width, height):
        if height < 1:
            raise ValueError('MsgLog height must be at least 1!')

        self.messages = []
        self.x = x
        self.width = width
        self.height = height

    def add(self, msg):
        # Split the message if necessary, among multiple lines.
        new_msg_lines = textwrap.wrap(msg, self.width)

        for line in new_msg_lines:
            self.messages.append(line)

    def current_msgs(self):
        """Returns the most recent (and relevant) messages. The quantity depends
            on the height attribute.
        """
        return self.messages[-self.height:]
