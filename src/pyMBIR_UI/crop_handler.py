import numpy as np

from . import DataType


class CropHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def initialize_crop(self):
        list_image = self.parent.input['data'][DataType.projections]
        if list_image is None:
            return

        first_image = list_image[0]
        transpose_image = np.transpose(first_image)
        self.parent.crop_image_view.setImage(transpose_image)

        # file index
        nbr_files = len(self.parent.input['list files'][DataType.projections])
        self.parent.ui.crop_file_index_horizontalSlider.setMaximum(nbr_files-1)
        image_height, image_width = np.shape(first_image)

        # width
        self.parent.ui.crop_width_horizontalSlider.setMaximum(image_width)
        self.parent.ui.crop_width_horizontalSlider.setValue(image_width)
        self.parent.ui.crop_width_label.setText(str(image_width))
        self.parent.ui.crop_width_horizontalSlider.setMinimum(20)

    def master_checkbox_clicked(self):
        self.parent.ui.crop_frame.setEnabled(self.parent.ui.cropping_checkBox.isChecked())
