import os
from qtpy.QtWidgets import QMainWindow, QDialog

from . import load_ui
from pyMBIR_UI.session_handler import SessionHandler


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
            o_session = SessionHandler(parent=self.parent)
            o_session.save_from_ui()

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
        self.initialization()

    def initialization(self):
        session = self.parent.session_dict.get("advanced settings", None)
        if session is None:
            self.reset_button_clicked()
        else:
            wavelet_level = session["wavelet level"]
            max_number_of_iterations = session["max number of iterations"]
            number_of_cores = session["number of cores"]
            number_of_gpus = session["number of gpus"]
            stop_threshold = session["stop threshold"]
            det_x_y_linked = session["det_x, det_y"]["linked"]

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
        same_behavior_state = self.ui.det_x_y_radioButton.isChecked()
        same_behavior_widgets = [self.ui.det_x_y_label,
                                 self.ui.det_x_y_doubleSpinBox]
        not_same_behavior_widgets = [self.ui.det_x_label,
                                     self.ui.det_x_doubleSpinBox,
                                     self.ui.det_y_label,
                                     self.ui.det_y_doubleSpinBox,
                                     ]
        for _ui in same_behavior_widgets:
            _ui.setEnabled(same_behavior_state)
        for _ui in not_same_behavior_widgets:
            _ui.setEnabled(not same_behavior_state)

    def nbr_vox_clicked(self):
        same_behavior_state = self.ui.n_vox_x_y_radioButton.isChecked()
        same_behavior_widgets = [self.ui.n_vox_x_n_vox_y_label,
                                 self.ui.n_vox_x_n_vox_y_spinBox]
        not_same_behavior_widgets = [self.ui.n_vox_x_label,
                                     self.ui.n_vox_x_spinBox,
                                     self.ui.n_vox_y_label,
                                     self.ui.n_vox_y_spinBox,
                                     ]
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

        det_x_det_y_linked = config["det_x, det_y"]["linked"]
        self.ui.det_x_y_radioButton.setChecked(det_x_det_y_linked)
        det_x_det_y_value = config["det_x, det_y"]["value"]
        self.ui.det_x_y_doubleSpinBox.setValue(det_x_det_y_value)

        vox_xy_vox_z_linked = config["vox_xy, vox_z"]["linked"]
        self.ui.vox_xy_z_radioButton.setChecked(vox_xy_vox_z_linked)
        vox_xy_vox_z_value = config["vox_xy, vox_z"]["value"]
        self.ui.vox_xy_z_doubleSpinBox.setValue(vox_xy_vox_z_value)

        n_vox_x_n_vox_y_linked = config["n_vox_x, n_vox_y"]["linked"]
        self.ui.n_vox_x_y_radioButton.setChecked(n_vox_x_n_vox_y_linked)

        session_dict = self.parent.session_dict

        crop_width = session_dict['crop']['width']
        n_vox_x = crop_width / vox_xy_vox_z_value
        n_vox_y = n_vox_x
        self.ui.n_vox_x_spinBox.setValue(n_vox_x)
        self.ui.n_vox_y_spinBox.setValue(n_vox_y)
        self.ui.n_vox_x_n_vox_y_spinBox.setValue(n_vox_x)

        crop_height = session_dict['crop']['to slice - from slice']
        n_vox_z = (crop_height) / vox_xy_vox_z_value
        self.ui.n_vox_z_spinBox.setValue(n_vox_z)

        write_output_value = config["write output"]
        self.ui.write_output_checkBox.setChecked(write_output_value)

    def accept(self):
        self.save_widgets()
        self.close()

    def save_widgets(self):
        wavelet_level = self.ui.wavelet_level_slider.value()
        max_number_of_iterations = self.ui.max_nbr_iterations_spinBox.value()
        number_of_cores = self.ui.nbr_cores_slider.value()
        number_of_gpus = self.ui.nbr_gpu_slider.value()
        stop_threshold = self.ui.stop_threshold_lineEdit.text()
        det_x_y_linked = self.ui.det_x_y_radioButton.isChecked()
        if det_x_y_linked:
            value = self.ui.det_x_y_doubleSpinBox.value()
            det_x, det_y = value, value
        else:
            det_x = self.ui.det_x_doubleSpinBox.value()
            det_y = self.ui.det_y_doubleSpinBox.value()
        vox_xy_z_linked = self.ui.vox_xy_z_radioButton.isChecked()
        if vox_xy_z_linked:
            value = self.ui.vox_xy_z_doubleSpinBox.value()
            vox_xy, vox_z = value, value
        else:
            vox_xy = self.ui.vox_xy_doubleSpinBox.value()
            vox_z = self.ui.vox_z_doubleSpinBox.value()
        write_output_flag = self.ui.write_output_checkBox.isChecked()
        n_vox_x_y_linked = self.ui.n_vox_x_y_radioButton.isChecked()
        if n_vox_x_y_linked:
            value = self.ui.n_vox_x_n_vox_y_spinBox.value()
            n_vox_x, n_vox_y = value, value
        else:
            n_vox_x = self.ui.n_vox_x_spinBox.value()
            n_vox_y = self.ui.n_vox_y_spinBox.value()
        n_vox_z = self.ui.n_vox_z_spinBox.value()

        self.parent.session_dict["advanced settings"] = {"wavelet level": wavelet_level,
                                                         "max number of iterations": max_number_of_iterations,
                                                         "stop threshold": stop_threshold,
                                                         "number of cores": number_of_cores,
                                                         "number of gpus": number_of_gpus,
                                                         "det_x, det_y, det_z": {"linked": det_x_y_linked,
                                                                                 "det_x": det_x,
                                                                                 "det_y": det_y,
                                                                                },
                                                         "vox_xy, vox_z": {"linked": vox_xy_z_linked,
                                                                           "vox_xy": vox_xy,
                                                                           "vox_z": vox_z},
                                                         "n_vox_x, n_vox_y": {"linked" : n_vox_x_y_linked,
                                                                              "n_vox_x": n_vox_x,
                                                                              "n_vox_y": n_vox_y},
                                                         "n_vox_z": n_vox_z,
                                                         "write output": write_output_flag,
                                                         }
