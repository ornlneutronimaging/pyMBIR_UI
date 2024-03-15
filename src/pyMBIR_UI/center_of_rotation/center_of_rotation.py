import numpy as np
from qtpy import QtGui, QtCore
from qtpy.QtWidgets import QApplication
import pyqtgraph as pg
from tomopy.recon import rotation
import logging

from pyMBIR_UI import DataType
from pyMBIR_UI.utilities.gui import Gui
from pyMBIR_UI.utilities.get import Get
from pyMBIR_UI.loader import Loader


class Algorithm:
    tomopy = 'tomopy'
    user = 'user defined'


class CenterOfRotation:

    def __init__(self, parent=None):
        self.parent = parent

    def initialize_from_session(self):
        session = self.parent.session_dict['center rotation']
        self.parent.ui.master_center_of_rotation_checkBox.setChecked(session['state'])
        self.parent.ui.center_of_rotation_0_degrees_comboBox.setCurrentIndex(session['image 0 file index'])
        self.parent.ui.center_of_rotation_180_degrees_comboBox.setCurrentIndex(session['image 180 file index'])
        self.set_algorithm(algorithm=session['algorithm selected'])
        self.parent.ui.center_of_rotation_user_defined_doubleSpinBox.setValue(session['user value'])
        self.display_images()
        self.calculate_center_of_rotation()
        self.display_center_of_rotation()
        self.update_widgets()
        self.master_checkbox_clicked()

    def initialization(self):
        list_of_files = self.parent.input['list files'][DataType.projections]

        o_gui = Gui(parent=self.parent)
        o_gui.block_signal_handler(block=True, ui=self.parent.ui.center_of_rotation_0_degrees_comboBox)
        o_gui.block_signal_handler(block=True, ui=self.parent.ui.center_of_rotation_180_degrees_comboBox)
        self.parent.ui.center_of_rotation_0_degrees_comboBox.clear()
        self.parent.ui.center_of_rotation_180_degrees_comboBox.clear()
        self.parent.ui.center_of_rotation_0_degrees_comboBox.addItems(list_of_files)
        self.parent.ui.center_of_rotation_180_degrees_comboBox.addItems(list_of_files)
        o_gui.block_signal_handler(block=False, ui=self.parent.ui.center_of_rotation_0_degrees_comboBox)
        o_gui.block_signal_handler(block=False, ui=self.parent.ui.center_of_rotation_180_degrees_comboBox)

        o_get = Get(parent=self.parent)
        index_of_180_degree_image = o_get.get_file_index_of_180_degree_image()
        self.parent.ui.center_of_rotation_180_degrees_comboBox.setCurrentIndex(index_of_180_degree_image)

        self.parent.ui.center_of_rotation_user_defined_doubleSpinBox.setMaximum(self.parent.crop_image_width)

        self.display_images()
        self.calculate_center_of_rotation()
        self.display_center_of_rotation()
        self.update_widgets()
        self.master_checkbox_clicked()

    def master_checkbox_clicked(self):
        status = self.parent.ui.master_center_of_rotation_checkBox.isChecked()
        list_ui = [self.parent.ui.center_of_rotation_frame,
                   self.parent.ui.center_of_rotation_0_degree_label,
                   self.parent.ui.center_of_rotation_0_degrees_comboBox,
                   self.parent.ui.center_of_rotation_180_degree_label,
                   self.parent.ui.center_of_rotation_180_degrees_comboBox]
        for _ui in list_ui:
            _ui.setEnabled(status)

        if status:
            logging.info("Center of rotation mode: ON")
            self.display_center_of_rotation()
        else:
            logging.info("Center of rotation mode: OFF")
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
        o_loader = Loader(parent=self.parent)
        image = o_loader.retrieve_data(file_index=index)
        return image

    def update_widgets(self):
        state_user_defined = self.parent.ui.user_defined_algorithm_radioButton.isChecked()
        self.parent.ui.center_of_rotation_user_defined_doubleSpinBox.setVisible(state_user_defined)
        self.parent.ui.center_of_rotation_calculated_label.setVisible(not state_user_defined)

    def calculate_center_of_rotation(self):

        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        QApplication.processEvents()

        if self.parent.ui.tomopy_algorithm_radioButton.isChecked():
            image_0_degree = self._get_image_from_angle(degree=0)
            image_180_degree = self._get_image_from_angle(degree=180)

            value = rotation.find_center_pc(image_0_degree,
                                            image_180_degree)
            self.parent.ui.center_of_rotation_calculated_label.setText(str(int(value)))

        QApplication.restoreOverrideCursor()
        QApplication.processEvents()

    def get_center_of_rotation(self):
        algorithm_selected = self.get_algorithm_selected()
        if algorithm_selected == Algorithm.tomopy:
            value = str(self.parent.ui.center_of_rotation_calculated_label.text())
            if value != "N/A":
                value = float(value)
            logging.info("Center of rotation calculated via tomopy (find_center_pc)")
        elif algorithm_selected == Algorithm.user:
            value = self.parent.ui.center_of_rotation_user_defined_doubleSpinBox.value()
            logging.info("Center of rotation defined by user")
        logging.info(f"-> value: {value}")
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

    def get_algorithm_selected(self):
        if self.parent.ui.tomopy_algorithm_radioButton.isChecked():
            return Algorithm.tomopy
        elif self.parent.ui.user_defined_algorithm_radioButton.isChecked():
            return Algorithm.user
        else:
            raise NotImplementedError("Algorithm not implemented yet!")

    def set_algorithm(self, algorithm=Algorithm.tomopy):
        if algorithm == Algorithm.tomopy:
            self.parent.ui.tomopy_algorithm_radioButton.setChecked(True)
        elif algorithm == Algorithm.user:
            self.parent.ui.user_defined_algorithm_radioButton.setChecked(True)
