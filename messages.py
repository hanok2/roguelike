import tcod
import textwrap


class Msg(object):
    def __init__(self, text, color=tcod.white):
        self.text = text
        self.color = color


class MsgLog(object):
    def __init__(self, x, width, height):
        self.messages = []
        self.x = x
        self.width = width
        self.height = height

    def add(self, msg):
        # Split the message if necessary, among multiple lines.
        new_msg_lines = textwrap.wrap(msg.text, self.width)

        for line in new_msg_lines:
            # If the buffer is full, remove the first line to make room for the new one
            if len(self.messages) == self.height:
                del self.messages[0]

            # Add the new line as a Msg object, with the text and color
            self.messages.append(
                Msg(line, msg.color)
            )
