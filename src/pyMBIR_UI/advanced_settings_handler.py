import os
from qtpy.QtWidgets import QMainWindow, QDialog

from . import load_ui


class AdvancedSettingsPasswordHandler(QMainWindow):

    def __init__(self, parent=None):
        self.parent = parent
        super(QMainWindow, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'password.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.ui.wrong_password_label.setVisible(False)

    def password_changing(self, text):
        self.ui.wrong_password_label.setVisible(False)

    def validate_password(self):
        password = self.ui.password_input.text()
        if password == self.parent.config["advanced_settings_password"]:
            o_advanced = AdvancedSettingsHandler(parent=self.parent)
            o_advanced.show()
            self.close()
        else:
            self.ui.password_input.setText("")
            self.ui.wrong_password_label.setVisible(True)

    def ok_clicked(self):
        self.validate_password()

    def cancel_clicked(self):
        self.close()


class AdvancedSettingsHandler(QDialog):

    def __init__(self, parent=None):
        self.parent = parent
        super(QDialog, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'advanced_settings.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)

    def vox_clicked(self):
        same_behavior_state = self.ui.vox_xy_z_radioButton.isChecked()
        same_behavior_widgets = [self.ui.vox_xy_z_label,
                                 self.ui.vox_xy_z_doubleSpinBox]
        not_same_behavior_widgets = [self.ui.vox_xy_label,
                                     self.ui.vox_xy_doubleSpinBox,
                                     self.ui.vox_z_label,
                                     self.ui.vox_z_doubleSpinBox]
        for _ui in same_behavior_widgets:
            _ui.setEnabled(same_behavior_state)
        for _ui in not_same_behavior_widgets:
            _ui.setEnabled(not same_behavior_state)

    def det_clicked(self):
        same_behavior_state = self.ui.det_x_y_z_radioButton.isChecked()
        same_behavior_widgets = [self.ui.det_x_y_z_label,
                                 self.ui.det_x_y_z_doubleSpinBox]
        not_same_behavior_widgets = [self.ui.det_x_label,
                                     self.ui.det_x_doubleSpinBox,
                                     self.ui.det_y_label,
                                     self.ui.det_y_doubleSpinBox,
                                     self.ui.det_z_label,
                                     self.ui.det_z_doubleSpinBox]
        for _ui in same_behavior_widgets:
            _ui.setEnabled(same_behavior_state)
        for _ui in not_same_behavior_widgets:
            _ui.setEnabled(not same_behavior_state)

    def reset_button_clicked(self):
        config = self.parent.config["default widgets values"]

        wavelet_level = config["wavelet level"]
        self.ui.wavelet_level_slider.setValue(wavelet_level)

        max_number_of_iterations = config["max number of iterations"]
        self.ui.max_nbr_iterations_spinBox.setValue(max_number_of_iterations)

        stop_threshold = str(config["stop threshold"])
        self.ui.stop_threshold_lineEdit.setText(stop_threshold)

        det_x_det_y_det_z_linked = config["det_x, det_y, det_z"]["linked"]
        self.ui.det_x_y_z_radioButton.setChecked(det_x_det_y_det_z_linked)
        det_x_det_y_det_z_value = config["det_x, det_y, det_z"]["value"]
        self.ui.det_x_y_z_doubleSpinBox.setValue(det_x_det_y_det_z_value)

        vox_xy_vox_z_linked = config["vox_xy, vox_z"]["linked"]
        self.ui.vox_xy_z_radioButton.setChecked(vox_xy_vox_z_linked)
        vox_xy_vox_z_value = config["vox_xy, vox_z"]["value"]
        self.ui.vox_xy_z_doubleSpinBox.setValue(vox_xy_vox_z_value)

        write_output_value = config["write output"]
        self.ui.write_output_checkBox.setChecked(write_output_value)
