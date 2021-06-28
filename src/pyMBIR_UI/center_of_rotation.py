import numpy as np

from . import DataType


class CenterOfRotation:

    def __init__(self, parent=None):
        self.parent = parent

    def initialization(self):
        list_of_files = self.parent.input['list files'][DataType.projections]
        self.parent.ui.center_of_rotation_0_degrees_comboBox.addItems(list_of_files)
        self.parent.ui.center_of_rotation_180_degrees_comboBox.addItems(list_of_files)

        self.display_images()

    def master_checkbox_clicked(self):
        status = self.parent.ui.master_checkBox.isChecked()
        list_ui = [self.parent.ui.center_of_rotation_frame,
                   self.parent.ui.center_of_rotation_0_degree_label,
                   self.parent.ui.center_of_rotation_0_degrees_comboBox,
                   self.parent.ui.center_of_rotation_180_degree_label,
                   self.parent.ui.center_of_rotation_180_degrees_comboBox]
        for _ui in list_ui:
            _ui.setEnabled(status)

    def display_images(self):
        file_0_degree_index = self.parent.ui.center_of_rotation_0_degrees_comboBox.currentIndex()
        file_180_degrees_index = self.parent.ui.center_of_rotation_180_degrees_comboBox.currentIndex()

        image_0_degree = self.parent.input['data'][DataType.projections][file_0_degree_index]
        image_180_degree = self.parent.input['data'][DataType.projections][file_180_degrees_index]

        final_image = 0.5*image_0_degree + 0.5*image_180_degree
        transpose_image = np.transpose(final_image)
        self.parent.center_of_rotation_image_view.setImage(transpose_image)
