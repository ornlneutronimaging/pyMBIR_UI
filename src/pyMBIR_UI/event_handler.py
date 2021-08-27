import logging
import numpy as np

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

    def update_output_plot(self, data):
        self.parent.ui.tabWidget.setTabEnabled(3, True)
        self.parent.ui.tabWidget.setCurrentIndex(3)

        data_to_display = np.transpose(data)
        self.parent.ui.output_image_view.setImage(data_to_display)
