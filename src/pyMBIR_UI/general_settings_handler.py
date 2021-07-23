import numpy as np

from . import ReconstructionAlgorithm


class GeneralSettingsHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def initialization_from_session(self):
        advanced_parameters_session = self.parent.session_dict.get('advanced parameters', None)

        if advanced_parameters_session is None:
            return

        diffuseness = advanced_parameters_session['diffuseness']
        smoothness = advanced_parameters_session['smoothness']
        sigma = advanced_parameters_session['sigma']
        reconstruction_algorithm = advanced_parameters_session['reconstruction algorithm']

        self.parent.ui.diffuseness_doubleSpinBox.setValue(diffuseness)
        self.parent.ui.smoothness_doubleSpinBox.setValue(smoothness)
        self.parent.ui.sigma_doubleSpinBox.setValue(sigma)
        self.set_reconstruction_algorithm_selected(reconstruction_algorithm)

    def sub_sampling_value_changed(self):
        factor = self.parent.ui.sub_sampling_spinBox.value()
        try:
            from_slice = np.int(str(self.parent.ui.crop_from_slice_label.text()))
            to_slice = np.int(str(self.parent.ui.crop_to_slice_label.text()))
            nbr_sampling = np.int(np.abs(to_slice - from_slice) / factor)
        except ValueError:
            nbr_sampling = "N/A"

        self.parent.ui.sub_sampling_label.setText(f"({nbr_sampling} projections will be reconstructed)")

    def get_reconstruction_algorithm_selected(self):
        if self.parent.ui.reconstruction_algorithm_pymbir_radioButton.isChecked():
            return ReconstructionAlgorithm.pymbir
        else:
            raise NotImplementedError(f"Reconstruction Algorithm not implemented yet!")

    def set_reconstruction_algorithm_selected(self, algorithm_selected=ReconstructionAlgorithm.pymbir):
        if algorithm_selected == ReconstructionAlgorithm.pymbir:
            self.parent.ui.reconstruction_algorithm_pymbir_radioButton.setChecked(True)
        else:
            raise NotImplementedError(f"Reconstruction Algorithm not implemented yet!")
