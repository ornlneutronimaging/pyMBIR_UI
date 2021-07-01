import numpy as np

from pyMBIR_UI import DataType
from pyMBIR_UI.utilities.get import Get
from pyMBIR_UI import TiltAlgorithm
from pyMBIR_UI.tilt.direct_minimization import DirectMinimization
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
        self.set_algorithm(algorithm=session['algorithm selected'])

        self.file_index_changed()
        self.master_checkBox_clicked()

    def file_index_changed(self):
        file_index_selected = self.parent.ui.tilt_correction_file_index_horizontalSlider.value()
        o_loader = Loader(parent=self.parent)
        image = o_loader.retrieve_data(file_index=file_index_selected)
        transpose_image = np.transpose(image)
        self.parent.tilt_correction_image_view.setImage(transpose_image)

    def master_checkBox_clicked(self):
        master_value = self.parent.ui.tilt_correction_checkBox.isChecked()
        self.parent.ui.tilt_correction_frame.setEnabled(master_value)

    def correction_algorithm_changed(self):
        o_get = Get(parent=self.parent)
        algo_selected = o_get.tilt_algorithm_selected()
        tilt_value = np.NaN
        if algo_selected == TiltAlgorithm.direct_minimization:
            tilt_value = self.direct_minimization()
        elif algo_selected == TiltAlgorithm.phase_correlation:
            tilt_value = self.phase_correlation()
        elif algo_selected == TiltAlgorithm.use_center:
            tilt_value = self.use_center()
        self.parent.ui.tilt_correcton_value_label.setText(str(tilt_value))

    def direct_minimization(self):
        o_direct = DirectMinimization()
        tilt_value = o_direct.run()
        return tilt_value

    def phase_correlation(self):
        return np.NaN

    def use_center(self):
        return np.NaN

    def set_up_images_at_0_and_180_degrees(self):
        o_setup = Setup0180DegreeHandler(parent=self.parent)
        o_setup.show()

    def get_algorithm_selected(self):
        if self.parent.ui.tilt_correction_direct_minimization_radioButton.isChecked():
            return TiltAlgorithm.direct_minimization
        elif self.parent.ui.tilt_correction_phase_correlation_radioButton.isChecked():
            return TiltAlgorithm.phase_correlation
        elif self.parent.ui.tilt_correction_use_center_radioButton.isChecked():
            return TiltAlgorithm.use_center
        else:
            raise NotImplementedError("algorithm not implemented!")

    def set_algorithm(self, algorithm=TiltAlgorithm.direct_minimization):
        if algorithm == TiltAlgorithm.direct_minimization:
            self.parent.ui.tilt_correction_direct_minimization_radioButton.setChecked(True)
        elif algorithm == TiltAlgorithm.phase_correlation:
            self.parent.ui.tilt_correction_phase_correlation_radioButton.setChecked(True)
        elif algorithm == TiltAlgorithm.use_center:
            self.parent.ui.tilt_correction_use_center_radioButton.setChecked(True)
        else:
            raise NotImplementedError("Algorithm not implemened!")
