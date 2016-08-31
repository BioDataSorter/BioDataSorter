"""For adding info on hover of a tkinter widget. Adapted from
https://jakirkpatrick.wordpress.com/2012/02/01/making-a-hovering-box-in-tkinter/"""

from tkinter import *
import re


class HoverText(Tk):
    """
    Usage: Bind methods to target widget with any other commands.

    hover_instance = HoverText(parent, "Hi\nThese are some facts\nPython is awesome!")
    target_widget.bind('<Enter>', lambda e: (hover_instance.enter(e),
                                             do_something_else(hover_instance)))  # <= multiple commands
    target_widget.bind('<Leave>', hover_instance.leave)
    parent.bind('<Motion>', hover_instance.motion)
    """

    def __init__(self, parent, text="", width=100):
        Tk.__init__(self)
        self.overrideredirect(True)
        self.parent = parent
        if not isinstance(text, str):
            raise TypeError('Trying to initialize a Hover Menu with a non string type: ' + text.__class__.__name__)

        text_lines = re.split('\n', text)
        self.width = max([len(text_line) for text_line in text_lines]) * 7
        self.labels = []
        for t in text_lines:
            self.labels.append(Label(self, text=t))
        for i, label in enumerate(self.labels):
            label.grid(row=i)

        self.withdraw()
        self._displayed = False

    def enter(self, _):
        self._displayed = True
        self.deiconify()
        self.motion(_)

    def leave(self, event):
        # extra check in case mouse moves over top frame instead of hovering over word cloud
        if self._displayed and (event.x > 390 or event.y > 203 or event.x < 3 or event.y < 3):
            self._displayed = False
            self.withdraw()

    def motion(self, _):
        x = self.winfo_pointerx()  # absolute positioning instead of compared to widget
        y = self.winfo_pointery()  # b/c geometry uses absolute positioning
        self.geometry("%dx%d+%d+%d" % (self.width, len(self.labels)*22, x+2, y+2))


class HoverFrame(HoverText):
    def __init__(self, frame):
        HoverText.__init__(self)
