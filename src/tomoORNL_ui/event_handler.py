import logging
import numpy as np

from tomoORNL_ui import DataType
from tomoORNL_ui.gui_initialization import GuiInitialization


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
        self.parent.ui.output_horizontalSlider.blockSignals(True)
        full_reconstructed_array = self.parent.full_reconstructed_array

        nbr_arrays = len(full_reconstructed_array)
        if nbr_arrays == 1:
            self.parent.ui.output_horizontalSlider.setVisible(False)
            self.parent.ui.output_horizontalSlider.setValue(0)
            array_index_to_show = 0
        else:
            self.parent.ui.output_horizontalSlider.setVisible(True)
            self.parent.ui.output_horizontalSlider.setMaximum(nbr_arrays-1)
            if self.parent.ui.output_checkBox.isChecked():
                array_index_to_show = nbr_arrays - 1
                self.parent.ui.output_horizontalSlider.setValue(array_index_to_show)
            else:
                array_index_to_show = self.parent.ui.output_horizontalSlider.value()

        self.display_output_plot(array_index_to_show=array_index_to_show)
        self.parent.ui.output_horizontalSlider.blockSignals(False)

    def display_output_plot(self, array_index_to_show=0):
        self.parent.ui.output_slider_label.setText(f"{array_index_to_show}")
        full_reconstructed_array = self.parent.full_reconstructed_array
        data_to_display = np.transpose(full_reconstructed_array[array_index_to_show])

        _view = self.parent.ui.output_image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.parent.temporary_output_view_histogram is None:
            first_update = True

        _histo_widget = self.parent.ui.output_image_view.getHistogramWidget()
        self.parent.temporary_output_view_histogram = _histo_widget.getLevels()

        self.parent.ui.output_image_view.setImage(data_to_display)

        _view_box.setState(_state)

        if not first_update:
            histogram = self.parent.temporary_output_view_histogram
            _histo_widget.setLevels(histogram[0], histogram[1])

    def reset_output_plot(self):
        self.parent.ui.tabWidget.setTabEnabled(3, False)
        self.parent.ui.output_image_view.clear()
        self.parent.ui.output_horizontalSlider.setVisible(False)
        self.parent.ui.output_horizontalSlider.setMaximum(1)
        self.parent.full_reconstructed_array = None
