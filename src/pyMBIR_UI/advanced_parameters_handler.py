class AdvancedParametersHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def initialization_from_session(self):
        advanced_parameters_session = self.parent.session_dict.get('advanced parameters', None)

        if advanced_parameters_session is None:
            return

        diffuseness = advanced_parameters_session['diffuseness']
        smoothness = advanced_parameters_session['smoothness']
        sigma = advanced_parameters_session['sigma']

        self.parent.ui.diffuseness_doubleSpinBox.setValue(diffuseness)
        self.parent.ui.smoothness_doubleSpinBox.setValue(smoothness)
        self.parent.ui.sigma_doubleSpinBox.setValue(sigma)
        