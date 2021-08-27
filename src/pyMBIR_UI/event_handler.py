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

    def update_output_plot(self):

        full_reconstructed_array = self.parent.full_reconstructed_array

        nbr_arrays = len(full_reconstructed_array)
        if nbr_arrays == 1:
            self.parent.ui.output_horizontalSlider.setVisible(False)
            self.parent.ui.output_horizontalSlider.setValue(0)
            self.parent.ui.output_checkBox.setVisible(False)
            array_index_to_show = 0
        else:
            self.parent.ui.output_horizontalSlider.setVisible(True)
            self.parent.ui.output_horizontalSlider.setMaximum(nbr_arrays)
            if self.parent.ui.output_checkBox.isChecked():
                array_index_to_show = nbr_arrays - 1
            else:
                array_index_to_show = self.parent.ui.output_horizontalSlider.value()

        data_to_display = np.transpose(full_reconstructed_array[array_index_to_show])
        self.parent.ui.output_image_view.setImage(data_to_display)
