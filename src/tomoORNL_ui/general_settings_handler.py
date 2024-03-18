from tomoORNL_ui import ReconstructionAlgorithm
from tomoORNL_ui import DataType


class GeneralSettingsHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def initialization_from_session(self):
        general_parameters_session = self.parent.session_dict.get('general parameters', None)

        if general_parameters_session is None:
            return

        diffuseness = general_parameters_session['diffuseness']
        smoothness = general_parameters_session['smoothness']
        sigma = general_parameters_session['sigma']
        reconstruction_algorithm = general_parameters_session['reconstruction algorithm']
        sub_sampling_factor = general_parameters_session['sub sampling factor']

        self.parent.ui.diffuseness_doubleSpinBox.setValue(diffuseness)
        self.parent.ui.smoothness_doubleSpinBox.setValue(smoothness)
        self.parent.ui.sigma_doubleSpinBox.setValue(sigma)
        self.set_reconstruction_algorithm_selected(reconstruction_algorithm)
        self.parent.ui.sub_sampling_spinBox.setValue(sub_sampling_factor)

    def sub_sampling_value_changed(self):
        factor = self.parent.ui.sub_sampling_spinBox.value()
        try:
            # from_slice = np.int(str(self.parent.ui.crop_from_slice_label.text()))
            # to_slice = np.int(str(self.parent.ui.crop_to_slice_label.text()))
            # nbr_sampling = np.int(np.abs(to_slice - from_slice) / factor)
            nbr_images = len(self.parent.input['list files'][DataType.projections])
            nbr_sampling = int(nbr_images / factor)
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
