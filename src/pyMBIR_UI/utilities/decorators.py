import functools
from .gui import Gui
import logging


def check_ui(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):

        logging.debug(f"calling {func.__name__}")
        self = args[0]

        if len(args) > 1:
            retval = func(self, args[1:], **kwargs)
        else:
            retval = func(self, **kwargs)

        o_gui = Gui(parent=self)
        o_gui.check_ui()

        return retval

    return wrap
