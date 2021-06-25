import numpy as np

from . import DataType


class TiltHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def initialize_tilt_correction(self):
        list_image = self.parent.input['data'][DataType.projections]
        if list_image is None:
            return

        self.file_index_changed()

    def file_index_changed(self):
        file_index_selected = self.parent.ui.tilt_correctoni_file_index_horizontalSlider.value()
        list_image = self.parent.input['data'][DataType.projections]
        image = list_image[file_index_selected]
        transpose_image = np.transpose(image)
        self.parent.tilt_correction_image_view.setImage(transpose_image)

    def master_checkBox_clicked(self):
        master_value = self.parent.ui.tilt_correction_checkBox.isChecked()
        self.parent.ui.tilt_correction_frame.setEnabled(master_value)
