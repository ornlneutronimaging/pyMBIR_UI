import logging

from . import DataType
from .gui_initialization import GuiInitialization


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def full_reset_clicked(self):
        self.parent.input = {'list files'     : {DataType.projections: None,
                                                 DataType.ob         : None,
                                                 DataType.df         : None,
                                                 },
                             'full list files': {DataType.projections: None,
                                                 DataType.ob         : None,
                                                 DataType.df         : None,
                                                 },
                             'data'           : {DataType.projections: None,
                                                 DataType.ob         : None,
                                                 DataType.df         : None},
                             }

        o_init = GuiInitialization(parent=self.parent)
        o_init.full_reset()

        logging.info("Full reset of application!")
