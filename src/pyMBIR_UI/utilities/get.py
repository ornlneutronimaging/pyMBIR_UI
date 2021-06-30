from os.path import expanduser
import os

from .. import TiltAlgorithm


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def get_log_file_name(self):
        log_file_name = self.parent.config['log_file_name']
        full_log_file_name = Get.get_full_home_file_name(log_file_name)
        return full_log_file_name

    def get_main_tab_selected(self):
        current_tab = self.parent.ui.top_tabWidget.currentIndex()
        return current_tab

    def algorithm_selected(self):
        index_selected = self.parent.ui.pre_processing_fitting_procedure_comboBox.currentIndex()
        return self.parent.ui.pre_processing_fitting_procedure_comboBox.itemData(index_selected)

    def get_automatic_config_file_name(self):
        config_file_name = self.parent.config['session_file_name']
        full_config_file_name = Get.get_full_home_file_name(config_file_name)
        return full_config_file_name

    def tilt_algorithm_selected(self):
        if self.parent.ui.tilt_correction_direct_minimization_radioButton.isChecked():
            return TiltAlgorithm.direct_minimization
        elif self.parent.ui.tilt_correction_phase_correlation_radioButton.isChecked():
            return TiltAlgorithm.phase_correlation
        elif self.parent.ui.tilt_correction_use_center_radioButton.isChecked():
            return TiltAlgorithm.use_center
        else:
            NotImplementedError("Tilt algorithm not implemented!")

    @staticmethod
    def get_full_home_file_name(base_file_name):
        home_folder = expanduser("~")
        full_log_file_name = os.path.join(home_folder, base_file_name)
        return full_log_file_name
