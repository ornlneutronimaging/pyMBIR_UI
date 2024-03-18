import numpy as np
import pyqtgraph as pg
from qtpy import QtGui

from pyMBIR_UI import DataType
from pyMBIR_UI.utilities.get import Get
from pyMBIR_UI.tilt.direct_minimization import DirectMinimization
from pyMBIR_UI.tilt.phase_correlation import PhaseCorrelation
from pyMBIR_UI.tilt.use_center import UseCenter
from pyMBIR_UI.tilt.setup_0_180_degree_handler import Setup0180DegreeHandler
from pyMBIR_UI.loader import Loader
from pyMBIR_UI import TiltAlgorithm


class TiltHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def initialize_tilt_correction(self):
        list_image = self.parent.input['data'][DataType.projections]
        if list_image is None:
            return

        # file index
        first_image = list_image[0]
        nbr_files = len(self.parent.input['list files'][DataType.projections])
        self.parent.ui.tilt_correction_file_index_horizontalSlider.setMaximum(nbr_files-1)
        image_height, image_width = np.shape(first_image)
        self.parent.tilt_correction_image_height = image_height
        self.parent.tilt_correction_image_width = image_width

        # initialize 0 and 180 degrees images
        tilt_correction_index_dict = self.parent.tilt_correction_index_dict
        if tilt_correction_index_dict['180_degree'] == -1:
            o_get = Get(parent=self.parent)
            index_of_180_degree_image = o_get.get_file_index_of_180_degree_image()
            self.parent.tilt_correction_index_dict['180_degree'] = index_of_180_degree_image
            self.parent.tilt_correction_index_dict['0_degree'] = 0

    def initialize_tilt_from_session(self):
        session = self.parent.session_dict['tilt']
        self.parent.ui.tilt_correction_checkBox.setChecked(session['state'])
        self.parent.ui.tilt_correction_file_index_horizontalSlider.setValue(session['file index'])
        self.parent.tilt_correction_index_dict['180_degree'] = session['image 180 file index']
        self.parent.tilt_correction_index_dict['0_degree'] = session['image 0 file index']
        if TiltAlgorithm.user_defined:
            self.parent.tilt_user_defined_doubleSpinBox.setValue(session[TiltAlgorithm.user_defined])
        self.set_algorithm(algorithm=session['algorithm selected'])

        tilt_calculation = {TiltAlgorithm.phase_correlation: session[TiltAlgorithm.phase_correlation],
                            TiltAlgorithm.direct_minimization: session[TiltAlgorithm.direct_minimization],
                            TiltAlgorithm.use_center: session[TiltAlgorithm.use_center],
                            TiltAlgorithm.user_defined: session[TiltAlgorithm.user_defined]}
        self.parent.tilt_calculation = tilt_calculation
        self.correction_algorithm_changed()
        self.parent.ui.tilt_refresh_calculation_pushButton.setEnabled(False)

        self.file_index_changed()
        self.master_checkBox_clicked()

    def file_index_changed(self):
        file_index_selected = self.parent.ui.tilt_correction_file_index_horizontalSlider.value()
        o_loader = Loader(parent=self.parent)
        image = o_loader.retrieve_data(file_index=file_index_selected)
        transpose_image = np.transpose(image)
        self.parent.tilt_correction_image_view.setImage(transpose_image)

        if not (self.parent.tilt_grid_item is None):
            self.parent.tilt_correction_image_view.removeItem(self.parent.tilt_grid_item)
            self.parent.tilt_grid_item = None

        # show tilt calculated
        tilt_value = self.parent.ui.tilt_correcton_value_label.text()
        tilt_value_float = float(tilt_value)
        if np.isfinite(tilt_value_float):

            _pen = QtGui.QPen()
            _pen.setColor(QtGui.QColor(0, 255, 255))
            _pen.setWidth(5)

            self.parent.tilt_grid_item = pg.InfiniteLine([self.parent.tilt_correction_item_x_position,
                                                          self.parent.tilt_correction_item_x_position],
                                                         angle=90-tilt_value_float,
                                                         movable=True,
                                                         pen=_pen)
            self.parent.tilt_correction_image_view.addItem(self.parent.tilt_grid_item)
            self.parent.tilt_grid_item.sigPositionChanged.connect(self.parent.tilt_item_moved_by_user)

    def tilt_item_moved_by_user(self):
        item = self.parent.tilt_grid_item
        value = item.value()
        if type(value) is float:
            self.parent.tilt_correction_item_x_position = value
        else:
            self.parent.tilt_correction_item_x_position = value[0]

    def master_checkBox_clicked(self):
        master_value = self.parent.ui.tilt_correction_checkBox.isChecked()
        self.parent.ui.tilt_correction_frame.setEnabled(master_value)
        if not master_value:
            if not (self.parent.tilt_grid_item is None):
                self.parent.tilt_correction_image_view.removeItem(self.parent.tilt_grid_item)
                self.parent.tilt_grid_item = None
        else:
            self.file_index_changed()

    def correction_algorithm_changed(self):
        o_get = Get(parent=self.parent)
        algo_selected = o_get.tilt_algorithm_selected()
        if algo_selected == TiltAlgorithm.user_defined:
            tilt_value = self.parent.ui.tilt_user_defined_doubleSpinBox.value()
            self.parent.tilt_calculation[algo_selected] = tilt_value
        tilt_value = self.parent.tilt_calculation[algo_selected]
        if tilt_value is None:
            self.parent.ui.tilt_correcton_value_label.setText("NaN")
        else:
            self.parent.ui.tilt_correcton_value_label.setText("{:.2f}".format(tilt_value))
        self.parent.ui.tilt_refresh_calculation_pushButton.setEnabled(True)

        if algo_selected == TiltAlgorithm.user_defined:
            self.parent.ui.tilt_user_defined_doubleSpinBox.setEnabled(True)
        else:
            self.parent.ui.tilt_user_defined_doubleSpinBox.setEnabled(False)
        self.file_index_changed()

    def refresh_calculation(self):
        o_get = Get(parent=self.parent)
        algo_selected = o_get.tilt_algorithm_selected()
        tilt_value = np.NaN
        if algo_selected == TiltAlgorithm.direct_minimization:
            tilt_value = self.direct_minimization()
        elif algo_selected == TiltAlgorithm.phase_correlation:
            tilt_value = self.phase_correlation()
        elif algo_selected == TiltAlgorithm.use_center:
            tilt_value = self.use_center()
        elif algo_selected == TiltAlgorithm.user_defined:
            tilt_value = self.ui.tilt_user_defined_doubleSpinBox.value()
        self.parent.tilt_calculation[algo_selected] = tilt_value
        self.correction_algorithm_changed()
        self.parent.ui.tilt_refresh_calculation_pushButton.setEnabled(False)

    def direct_minimization(self):
        o_direct = DirectMinimization(parent=self.parent)
        tilt_value = o_direct.compute()
        return tilt_value

    def phase_correlation(self):
        o_phase = PhaseCorrelation(parent=self.parent)
        tilt_value = o_phase.compute()
        return tilt_value

    def use_center(self):
        o_center = UseCenter(parent=self.parent)
        tilt_value = o_center.compute(sigma=15, maxshift=200)
        return tilt_value

    def set_up_images_at_0_and_180_degrees(self):
        o_setup = Setup0180DegreeHandler(parent=self.parent)
        o_setup.show()

    def get_algorithm_selected(self):
        o_get = Get(parent=self.parent)
        algo_selected = o_get.tilt_algorithm_selected()
        return algo_selected

    def get_tilt_value_to_use_in_reconstruction(self):
        algo_selected = self.get_algorithm_selected()
        return self.parent.tilt_calculation[algo_selected]

    def set_algorithm(self, algorithm=TiltAlgorithm.direct_minimization):
        state_of_user_defined_checkbox = False
        if algorithm == TiltAlgorithm.direct_minimization:
            self.parent.ui.tilt_correction_direct_minimization_radioButton.setChecked(True)
        elif algorithm == TiltAlgorithm.phase_correlation:
            self.parent.ui.tilt_correction_phase_correlation_radioButton.setChecked(True)
        elif algorithm == TiltAlgorithm.use_center:
            self.parent.ui.tilt_correction_use_center_radioButton.setChecked(True)
        elif algorithm == TiltAlgorithm.user_defined:
            self.parent.ui.tilt_user_defined_radioButton.setChecked(True)
            state_of_user_defined_checkbox = True
        else:
            raise NotImplementedError("Algorithm not implemented!")
        self.parent.ui.tilt_user_defined_doubleSpinBox.setEnabled(state_of_user_defined_checkbox)
