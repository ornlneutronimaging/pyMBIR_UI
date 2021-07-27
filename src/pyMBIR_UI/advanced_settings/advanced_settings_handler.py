import os
from qtpy.QtWidgets import QMainWindow, QDialog

from pyMBIR_UI import load_ui
from pyMBIR_UI.session_handler import SessionHandler
from pyMBIR_UI.utilities.get import Get


class AdvancedSettingsPasswordHandler(QMainWindow):

    def __init__(self, parent=None):
        self.parent = parent
        super(QMainWindow, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('../ui',
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
    local_session_dict = {}

    def __init__(self, parent=None):
        self.parent = parent
        super(QDialog, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('../ui',
                                                 'advanced_settings.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.initialization()

    def initialization(self):
        session = self.parent.session_dict.get("advanced settings", None)

        nbr_cpu = Get.get_number_of_cpu()
        self.ui.nbr_cores_slider.setMaximum(nbr_cpu)
        self.ui.nbr_cores_label.setText(str(nbr_cpu))

        # nbr gpu
        nbr_gpu = Get.get_number_of_gpu()
        if nbr_gpu == 0:
            widget_state = False
        else:
            widget_state = True
        self.ui.number_of_gpu_first_label.setEnabled(widget_state)
        self.ui.nbr_gpu_slider.setEnabled(widget_state)
        self.ui.nbr_gpu_label.setEnabled(widget_state)
        self.ui.nbr_gpu_label.setText(str(nbr_gpu))

        if session is None:
            self.reset_button_clicked()
        else:
            self.local_session_dict = {"wavelet_level"           : session["wavelet level"],
                                       "max_number_of_iterations": session["max number of iterations"],
                                       "number_of_cores"         : session["number of cores"],
                                       "number_of_gpus"          : session["number of gpus"],
                                       "stop_threshold"          : session["stop threshold"],
                                       "median_filter_size"      : session.get("median filter size",
                                                                               self.parent.config["default widgets values"]['median filter size']),
                                       "det_x_y_linked"          : session["det_x, det_y"]["linked"],
                                       "det_x_y_value"           : session["det_x, det_y"]["det_x_y"],
                                       "det_x_value"             : session["det_x, det_y"]["det_x"],
                                       "det_y_value"             : session["det_x, det_y"]["det_y"],
                                       "vox_xy_z_linked"         : session["vox_xy, vox_z"]["linked"],
                                       "vox_xy_z_value"          : session["vox_xy, vox_z"]["vox_xy_z"],
                                       "vox_xy_value"            : session["vox_xy, vox_z"]["vox_xy"],
                                       "vox_z_value"             : session["vox_xy, vox_z"]["vox_z"],
                                       "n_vox_x_y_linked"        : session["n_vox_x, n_vox_y"]["linked"],
                                       "n_vox_x_y_value"         : session["n_vox_x, n_vox_y"]["n_vox_x_y"],
                                       "n_vox_x_value"           : session["n_vox_x, n_vox_y"]["n_vox_x"],
                                       "n_vox_y_value"           : session["n_vox_x, n_vox_y"]["n_vox_y"],
                                       "n_vox_z_value"           : session["n_vox_z"],
                                       "write_output_flag"       : session["write output"],
                                       }
            self.update_widgets()

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

    def wavelet_level_changed(self, value):
        self.ui.wavelet_level_label.setText(str(value))

    def wavelet_level_clicked(self):
        value = self.ui.wavelet_level_slider.value()
        self.wavelet_level_changed(value)

    def number_of_cores_changed(self, value):
        self.ui.nbr_cores_label.setText(str(value))

    def number_of_cores_clicked(self):
        value = self.ui.nbr_cores_slider.value()
        self.number_of_cores_changed(value)

    def number_of_gpus_changed(self, value):
        self.ui.nbr_gpu_label.setText(str(value))

    def number_of_gpus_clicked(self):
        value = self.ui.nbr_gpu_slider.value()
        self.number_of_gpus_changed(value)

    def update_widgets(self):
        local_session_dict = self.local_session_dict
        wavelet_level = local_session_dict["wavelet_level"]
        self.ui.wavelet_level_slider.setValue(wavelet_level)
        self.ui.wavelet_level_label.setText(str(wavelet_level))
        max_number_of_iterations = local_session_dict["max_number_of_iterations"]
        self.ui.max_nbr_iterations_spinBox.setValue(max_number_of_iterations)
        stop_threshold = local_session_dict["stop_threshold"]
        self.ui.stop_threshold_lineEdit.setText(stop_threshold)
        median_filter_size = local_session_dict["median_filter_size"]
        self.ui.median_filter_spinBox.setValue(median_filter_size)

        det_x_det_y_linked = local_session_dict["det_x_y_linked"]
        self.ui.det_x_y_radioButton.setChecked(det_x_det_y_linked)
        det_x_y_value = local_session_dict["det_x_y_value"]
        self.ui.det_x_y_doubleSpinBox.setValue(det_x_y_value)
        det_x_value = local_session_dict["det_x_value"]
        self.ui.det_x_doubleSpinBox.setValue(det_x_value)
        det_y_value = local_session_dict["det_y_value"]
        self.ui.det_y_doubleSpinBox.setValue(det_y_value)

        vox_xy_z_linked = local_session_dict["vox_xy_z_linked"]
        self.ui.vox_xy_z_radioButton.setChecked(vox_xy_z_linked)
        vox_xy_z_value = local_session_dict["vox_xy_z_value"]
        self.ui.vox_xy_z_doubleSpinBox.setValue(vox_xy_z_value)
        vox_xy_value = local_session_dict["vox_xy_value"]
        self.ui.vox_xy_doubleSpinBox.setValue(vox_xy_value)
        vox_z_value = local_session_dict["vox_z_value"]
        self.ui.vox_z_doubleSpinBox.setValue(vox_z_value)

        n_vox_x_y_linked = local_session_dict["n_vox_x_y_linked"]
        self.ui.n_vox_x_y_radioButton.setChecked(n_vox_x_y_linked)
        n_vox_x_y_value = local_session_dict["n_vox_x_y_value"]
        self.ui.n_vox_x_n_vox_y_spinBox.setValue(n_vox_x_y_value)
        n_vox_x = local_session_dict["n_vox_x_value"]
        self.ui.n_vox_x_spinBox.setValue(n_vox_x)
        n_vox_y = local_session_dict["n_vox_y_value"]
        self.ui.n_vox_y_spinBox.setValue(n_vox_y)
        n_vox_z = local_session_dict["n_vox_z_value"]
        self.ui.n_vox_z_spinBox.setValue(n_vox_z)

        output_flag = local_session_dict["write_output_flag"]
        self.ui.write_output_checkBox.setChecked(output_flag)

    def reset_button_clicked(self):
        config = self.parent.config["default widgets values"]

        self.local_session_dict["wavelet_level"] = config["wavelet level"]
        self.local_session_dict["max_number_of_iterations"] = config["max number of iterations"]
        self.local_session_dict["stop_threshold"] = str(config["stop threshold"])
        self.local_session_dict["median_filter_size"] = config["median filter size"]

        self.local_session_dict["det_x_y_linked"] = config["det_x, det_y"]["linked"]
        self.local_session_dict["det_x_y_value"] = config["det_x, det_y"]["value"]
        self.local_session_dict["det_x_value"] = config["det_x, det_y"]["det_x"]
        self.local_session_dict["det_y_value"] = config["det_x, det_y"]["det_y"]

        self.local_session_dict["vox_xy_z_linked"] = config["vox_xy, vox_z"]["linked"]
        self.local_session_dict["vox_xy_z_value"] = config["vox_xy, vox_z"]["value"]
        self.local_session_dict["vox_xy_value"] = config["vox_xy, vox_z"]["vox_xy"]
        self.local_session_dict["vox_z_value"] = config["vox_xy, vox_z"]["vox_z"]

        session_dict = self.parent.session_dict
        crop_width = session_dict['crop']['width']
        n_vox_x = crop_width / self.local_session_dict["vox_xy_z_value"]
        self.local_session_dict["n_vox_x_y_linked"] = config["n_vox_x, n_vox_y"]["linked"]
        self.local_session_dict["n_vox_x_y_value"] = n_vox_x
        self.local_session_dict["n_vox_x_value"] = n_vox_x
        self.local_session_dict["n_vox_y_value"] = n_vox_x

        crop_height = session_dict['crop']['to slice - from slice']
        n_vox_z = (crop_height) / self.local_session_dict["vox_xy_z_value"]
        self.local_session_dict["n_vox_z_value"] = n_vox_z

        self.local_session_dict["write_output_flag"] = config["write output"]

        self.update_widgets()

    def accept(self):
        self.save_widgets()
        self.close()

    def save_widgets(self):
        wavelet_level = self.ui.wavelet_level_slider.value()
        max_number_of_iterations = self.ui.max_nbr_iterations_spinBox.value()
        number_of_cores = self.ui.nbr_cores_slider.value()
        number_of_gpus = self.ui.nbr_gpu_slider.value()
        stop_threshold = self.ui.stop_threshold_lineEdit.text()
        median_filter_size = self.ui.median_filter_spinBox.value()

        det_x_y_linked = self.ui.det_x_y_radioButton.isChecked()
        det_x_y_value = self.ui.det_x_y_doubleSpinBox.value()
        det_x = self.ui.det_x_doubleSpinBox.value()
        det_y = self.ui.det_y_doubleSpinBox.value()

        if det_x_y_linked:
            det_x_to_use = det_x_y_value
            det_y_to_use = det_x_y_value
        else:
            det_x_to_use = det_x
            det_y_to_use = det_y

        vox_xy_z_linked = self.ui.vox_xy_z_radioButton.isChecked()
        vox_xy_z_value = self.ui.vox_xy_z_doubleSpinBox.value()
        vox_xy = self.ui.vox_xy_doubleSpinBox.value()
        vox_z = self.ui.vox_z_doubleSpinBox.value()

        if vox_xy_z_linked:
            vox_xy_to_use = vox_xy_z_value
            vox_z_to_use = vox_xy_z_value
        else:
            vox_xy_to_use = vox_xy
            vox_z_to_use = vox_z

        n_vox_x_y_linked = self.ui.n_vox_x_y_radioButton.isChecked()
        n_vox_x_y_value = self.ui.n_vox_x_n_vox_y_spinBox.value()
        n_vox_x = self.ui.n_vox_x_spinBox.value()
        n_vox_y = self.ui.n_vox_y_spinBox.value()
        n_vox_z = self.ui.n_vox_z_spinBox.value()

        if n_vox_x_y_linked:
            n_vox_y_to_use = n_vox_x_y_value
            n_vox_x_to_use = n_vox_x_y_value
        else:
            n_vox_x_to_use = n_vox_x
            n_vox_y_to_use = n_vox_y

        write_output_flag = self.ui.write_output_checkBox.isChecked()

        self.parent.session_dict["advanced settings"] = {"wavelet level": wavelet_level,
                                                         "max number of iterations": max_number_of_iterations,
                                                         "stop threshold": stop_threshold,
                                                         "number of cores": number_of_cores,
                                                         "number of gpus": number_of_gpus,
                                                         "median filter size": median_filter_size,
                                                         "det_x, det_y": {"linked": det_x_y_linked,
                                                                          "det_x_y": det_x_y_value,
                                                                          "det_x": det_x,
                                                                          "det_y": det_y,
                                                                          "det_x_to_use": det_x_to_use,
                                                                          "det_y_to_use": det_y_to_use,
                                                                          },
                                                         "vox_xy, vox_z": {"linked": vox_xy_z_linked,
                                                                           "vox_xy_z": vox_xy_z_value,
                                                                           "vox_xy": vox_xy,
                                                                           "vox_z": vox_z,
                                                                           "vox_xy_to_use": vox_xy_to_use,
                                                                           "vox_z_to_use": vox_z_to_use,
                                                                           },
                                                         "n_vox_x, n_vox_y": {"linked": n_vox_x_y_linked,
                                                                              "n_vox_x_y": n_vox_x_y_value,
                                                                              "n_vox_x": n_vox_x,
                                                                              "n_vox_y": n_vox_y,
                                                                              "n_vox_x_to_use": n_vox_x_to_use,
                                                                              "n_vox_y_to_use": n_vox_y_to_use,
                                                                              },
                                                         "n_vox_z": n_vox_z,
                                                         "write output": write_output_flag,
                                                         }


