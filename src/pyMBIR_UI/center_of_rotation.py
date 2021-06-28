import numpy as np
from qtpy import QtGui
import pyqtgraph as pg
from tomopy.recon import rotation

from . import DataType
from .utilities.gui import Gui


class CenterOfRotation:

    def __init__(self, parent=None):
        self.parent = parent

    def initialization(self):
        list_of_files = self.parent.input['list files'][DataType.projections]

        o_gui = Gui(parent=self.parent)
        o_gui.block_signal_handler(block=True, ui=self.parent.ui.center_of_rotation_0_degrees_comboBox)
        o_gui.block_signal_handler(block=True, ui=self.parent.ui.center_of_rotation_180_degrees_comboBox)
        self.parent.ui.center_of_rotation_0_degrees_comboBox.addItems(list_of_files)
        self.parent.ui.center_of_rotation_180_degrees_comboBox.addItems(list_of_files)
        o_gui.block_signal_handler(block=False, ui=self.parent.ui.center_of_rotation_0_degrees_comboBox)
        o_gui.block_signal_handler(block=False, ui=self.parent.ui.center_of_rotation_180_degrees_comboBox)

        self.parent.ui.center_of_rotation_user_defined_spinBox.setMaximum(self.parent.crop_image_width)

        self.display_images()
        self.calculate_center_of_rotation()
        self.display_center_of_rotation()

    def master_checkbox_clicked(self):
        status = self.parent.ui.master_checkBox.isChecked()
        list_ui = [self.parent.ui.center_of_rotation_frame,
                   self.parent.ui.center_of_rotation_0_degree_label,
                   self.parent.ui.center_of_rotation_0_degrees_comboBox,
                   self.parent.ui.center_of_rotation_180_degree_label,
                   self.parent.ui.center_of_rotation_180_degrees_comboBox]
        for _ui in list_ui:
            _ui.setEnabled(status)

        if status:
            self.display_center_of_rotation()
        else:
            if self.parent.center_of_rotation_item:
                self.parent.ui.center_of_rotation_image_view.removeItem(self.parent.center_of_rotation_item)

    def display_images(self):
        image_0_degree = self._get_image_from_angle(degree=0)
        image_180_degree = self._get_image_from_angle(degree=180)

        final_image = 0.5*image_0_degree + 0.5*image_180_degree
        transpose_image = np.transpose(final_image)
        self.parent.center_of_rotation_image_view.setImage(transpose_image)

    def _get_image_from_angle(self, degree=0):
        if degree == 0:
            index = self.parent.ui.center_of_rotation_0_degrees_comboBox.currentIndex()
        elif degree == 180:
            index = self.parent.ui.center_of_rotation_180_degrees_comboBox.currentIndex()
        return self.parent.input['data'][DataType.projections][index]

    def update_widgets(self):
        state_user_defined = self.parent.ui.user_defined_algorithm_radioButton.isChecked()
        self.parent.ui.center_of_rotation_user_defined_spinBox.setVisible(state_user_defined)
        self.parent.ui.center_of_rotation_calculated_label.setVisible(not state_user_defined)

    def calculate_center_of_rotation(self):
        if self.parent.ui.tomopy_algorithm_radioButton.isChecked():
            image_0_degree = self._get_image_from_angle(degree=0)
            image_180_degree = self._get_image_from_angle(degree=180)

            value = rotation.find_center_pc(image_0_degree,
                                            image_180_degree)
            self.parent.ui.center_of_rotation_calculated_label.setText(str(np.int(value)))

    def get_center_of_rotation(self):
        if self.parent.ui.tomopy_algorithm_radioButton.isChecked():
            value = np.int(str(self.parent.ui.center_of_rotation_calculated_label.text()))
        elif self.parent.ui.user_defined_algorithm_radioButton.isChecked():
            value = self.parent.ui.center_of_rotation_user_defined_spinBox.value()
        else:
            raise ValueError("not supported yet!")
        return value

    def display_center_of_rotation(self):
        if self.parent.center_of_rotation_item:
            self.parent.ui.center_of_rotation_image_view.removeItem(self.parent.center_of_rotation_item)

        _pen = QtGui.QPen()
        _pen.setColor(QtGui.QColor(255, 0, 0))
        _pen.setWidth(10)

        center_of_rotation_value = self.get_center_of_rotation()
        self.parent.center_of_rotation_item = pg.InfiniteLine(center_of_rotation_value,
                                                              pen=_pen,
                                                              angle=90,
                                                              movable=False)
        self.parent.ui.center_of_rotation_image_view.addItem(self.parent.center_of_rotation_item)
