import os
from qtpy.QtWidgets import QMainWindow, QDialog, QFileDialog, QApplication
import logging
import json
import numpy as np

from pyMBIR_UI import load_ui
from pyMBIR_UI.session_handler import SessionHandler
from pyMBIR_UI.utilities.get import Get
from pyMBIR_UI.algorithm_dictionary_creator import AlgorithmDictionaryCreator
from pyMBIR_UI.general_settings_handler import GeneralSettingsHandler


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
        if nbr_cpu > 2:
            nbr_cpu -= 2
        else:
            nbr_cpu = 1
        self.ui.nbr_cores_slider.setValue(nbr_cpu)

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

        det_col_to_use = self.parent.session_dict['crop']['width']
        det_row_to_use = self.parent.session_dict['crop']['from slice'] - self.parent.session_dict['crop']['to slice']

        if session is None:
            self.reset_button_clicked()
        else:
            self.local_session_dict = {"wavelet_level"           : session["wavelet level"],
                                       "det_col_to_use"          : det_col_to_use,
                                       "det_row_to_use"          : det_row_to_use,
                                       "max_number_of_iterations": session["max number of iterations"],
                                       "number_of_cores"         : session["number of cores"],
                                       "number_of_gpus"          : session["number of gpus"],
                                       "stop_threshold"          : session["stop threshold"],
                                       "exporting_file_frequency": session["exporting file frequency"],
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
                                       "n_vox_x_n_vox_y_mode"    : session["n_vox_x, n_vox_y"]["mode"],
                                       "n_vox_x_y_value"         : session["n_vox_x, n_vox_y"]["n_vox_x_y"],
                                       "n_vox_x_value"           : session["n_vox_x, n_vox_y"]["n_vox_x"],
                                       "n_vox_y_value"           : session["n_vox_x, n_vox_y"]["n_vox_y"],
                                       "n_vox_z_mode"            : session["n_vox_z"]["mode"],
                                       "n_vox_z_value"           : session["n_vox_z"]["n_vox_z"],
                                       "write_output_flag"       : session["write output"],
                                       }
            self.update_widgets()
            self.update_fixed_values_of_n_vox_x_y_z()

    def update_fixed_values_of_n_vox_x_y_z(self):
        self.save_widgets()
        det_col = self.local_session_dict["det_col_to_use"]
        det_x_to_use = self.parent.session_dict["advanced settings"]["det_x, det_y"]["det_x_to_use"]
        vox_xy_to_use = self.parent.session_dict["advanced settings"]["vox_xy, vox_z"]["vox_xy_to_use"]
        n_vox_x = int(det_col * det_x_to_use / vox_xy_to_use)

        det_y_to_use = self.parent.session_dict["advanced settings"]["det_x, det_y"]["det_y_to_use"]
        vox_z_to_use = self.parent.session_dict["advanced settings"]["vox_xy, vox_z"]["vox_z_to_use"]
        det_row = np.abs(self.local_session_dict["det_row_to_use"]) + 1

        n_vox_z = int((det_row * det_y_to_use) / vox_z_to_use)

        self.ui.n_vox_x_n_vox_y_fixed_value.setText(str(n_vox_x))
        self.ui.n_vox_z_fixed_value.setText(str(n_vox_z))

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

        self.update_fixed_values_of_n_vox_x_y_z()

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

        self.update_fixed_values_of_n_vox_x_y_z()

    def det_xy_value_changed(self, new_value):
        self.det_clicked()

    def nbr_vox_xy_clicked(self):
        if self.ui.n_vox_x_y_fixed_radioButton.isChecked():
            mode = "fixed"
        elif self.ui.n_vox_x_y_user_radioButton.isChecked():
            mode = "user_linked"
        else:
            mode = "user_not_linked"

        widgets_dict = {'fixed': {'list_ui': [self.ui.n_vox_x_n_vox_y_fixed_label,
                                              self.ui.n_vox_x_n_vox_y_fixed_value,
                                             ],
                                  'state': True if mode == 'fixed' else False,
                                  },
                        'user_linked': {'list_ui': [self.ui.n_vox_x_n_vox_y_linked_label,
                                                    self.ui.n_vox_x_n_vox_y_linked_spinBox],
                                        'state': True if mode == 'user_linked' else False,
                                        },
                        'user_not_linked': {'list_ui': [self.ui.n_vox_x_user_not_linked_label,
                                                        self.ui.n_vox_x_user_not_linked_spinBox,
                                                        self.ui.n_vox_y_user_not_linked_label,
                                                        self.ui.n_vox_y_user_not_linked_spinBox],
                                            'state': True if mode == 'user_not_linked' else False,
                                            },
                        }

        for _key in widgets_dict.keys():
            for _ui in widgets_dict[_key]['list_ui']:
                _ui.setEnabled(widgets_dict[_key]['state'])

        self.update_fixed_values_of_n_vox_x_y_z()

    def vox_xy_z_value_changed(self, new_value):
        self.vox_clicked()

    def nbr_vox_z_clicked(self):
        if self.ui.n_vox_z_fixed_radioButton.isChecked():
            mode = 'fixed'
        else:
            mode = 'user'

        widgets_dict = {'fixed': {'list_ui': [self.ui.n_vox_z_fixed_label,
                                              self.ui.n_vox_z_fixed_value],
                                  'state': True if mode == 'fixed' else False,
                                  },
                        'user': {'list_ui': [self.ui.n_vox_z_user_label,
                                             self.ui.n_vox_z_user_spinBox],
                                 'state': True if mode == 'user' else False,
                                 }
                        }

        for _key in widgets_dict.keys():
            for _ui in widgets_dict[_key]['list_ui']:
                _ui.setEnabled(widgets_dict[_key]['state'])

        self.update_fixed_values_of_n_vox_x_y_z()

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
        stop_threshold = str(local_session_dict["stop_threshold"])
        self.ui.stop_threshold_lineEdit.setText(stop_threshold)
        median_filter_size = local_session_dict["median_filter_size"]
        self.ui.median_filter_spinBox.setValue(median_filter_size)
        exporting_file_frequency = local_session_dict["exporting_file_frequency"]
        self.ui.exporting_file_frequency_spinBox.setValue(exporting_file_frequency)

        number_of_cores = local_session_dict["number_of_cores"]
        number_of_cores_on_this_machine = self.ui.nbr_cores_slider.maximum()
        if number_of_cores <= number_of_cores_on_this_machine:
            self.ui.nbr_cores_slider.setValue(number_of_cores)
            self.ui.nbr_cores_label.setText(str(number_of_cores))

        number_of_gpus = local_session_dict["number_of_gpus"]
        number_of_gpus_on_this_machine = self.ui.nbr_gpu_slider.maximum()
        if number_of_gpus <= number_of_gpus_on_this_machine:
            self.ui.nbr_gpu_slider.setValue(number_of_gpus)
            self.ui.nbr_gpu_label.setText(str(number_of_gpus))

        det_x_det_y_linked = local_session_dict["det_x_y_linked"]
        if det_x_det_y_linked:
            self.ui.det_x_y_radioButton.setChecked(True)
        else:
            self.ui.det_x_det_x_radioButton.setChecked(True)
        self.det_clicked()
        det_x_y_value = local_session_dict["det_x_y_value"]
        self.ui.det_x_y_doubleSpinBox.setValue(det_x_y_value)
        det_x_value = local_session_dict["det_x_value"]
        self.ui.det_x_doubleSpinBox.setValue(det_x_value)
        det_y_value = local_session_dict["det_y_value"]
        self.ui.det_y_doubleSpinBox.setValue(det_y_value)

        vox_xy_z_linked = local_session_dict["vox_xy_z_linked"]
        if vox_xy_z_linked:
            self.ui.vox_xy_z_radioButton.setChecked(True)
        else:
            self.ui.vox_xy_vox_z_radioButton.setChecked(True)
        self.vox_clicked()
        self.ui.vox_xy_z_radioButton.setChecked(vox_xy_z_linked)
        vox_xy_z_value = local_session_dict["vox_xy_z_value"]
        self.ui.vox_xy_z_doubleSpinBox.setValue(vox_xy_z_value)
        vox_xy_value = local_session_dict["vox_xy_value"]
        self.ui.vox_xy_doubleSpinBox.setValue(vox_xy_value)
        vox_z_value = local_session_dict["vox_z_value"]
        self.ui.vox_z_doubleSpinBox.setValue(vox_z_value)

        n_vox_x_n_vox_y_mode = local_session_dict["n_vox_x_n_vox_y_mode"]
        if n_vox_x_n_vox_y_mode == "fixed":
            self.ui.n_vox_x_y_fixed_radioButton.setChecked(True)
        elif n_vox_x_n_vox_y_mode == "user_linked":
            self.ui.n_vox_x_y_user_radioButton.setChecked(True)
        else:
            self.ui.n_vox_x_n_vox_y_radioButton.setChecked(True)
        self.nbr_vox_xy_clicked()
        n_vox_x_y_value = local_session_dict["n_vox_x_y_value"]
        self.ui.n_vox_x_n_vox_y_fixed_value.setText(str(n_vox_x_y_value))
        self.ui.n_vox_x_n_vox_y_linked_spinBox.setValue(n_vox_x_y_value)
        n_vox_x = local_session_dict["n_vox_x_value"]
        self.ui.n_vox_x_user_not_linked_spinBox.setValue(n_vox_x)
        n_vox_y = local_session_dict["n_vox_y_value"]
        self.ui.n_vox_y_user_not_linked_spinBox.setValue(n_vox_y)

        n_vox_z_mode = local_session_dict["n_vox_z_mode"]
        if n_vox_z_mode == "fixed":
            self.ui.n_vox_z_fixed_radioButton.setChecked(True)
        else:
            self.ui.n_vox_z_user_radioButton.setChecked(True)
        self.nbr_vox_z_clicked()
        n_vox_z_value = local_session_dict["n_vox_z_value"]
        self.ui.n_vox_z_fixed_value.setText(str(n_vox_z_value))
        self.ui.n_vox_z_user_spinBox.setValue(n_vox_z_value)

        output_flag = local_session_dict["write_output_flag"]
        self.ui.write_output_checkBox.setChecked(output_flag)

    def reset_button_clicked(self):
        config = self.parent.config["default widgets values"]

        o_get = Get(parent=self.parent)
        number_of_cores = o_get.get_number_of_cpu()
        number_of_gpus = o_get.get_number_of_gpu()

        self.local_session_dict["number_of_cores"] = number_of_cores
        self.local_session_dict["number_of_gpus"] = number_of_gpus

        self.local_session_dict["wavelet_level"] = config["wavelet level"]
        self.local_session_dict["max_number_of_iterations"] = config["max number of iterations"]
        self.local_session_dict["stop_threshold"] = str(config["stop threshold"])
        self.local_session_dict["median_filter_size"] = config["median filter size"]
        self.local_session_dict["exporting_file_frequency"] = config["exporting file frequency"]

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
        det_x_to_use = config["det_x, det_y"]["value"]
        vox_xy_value = config["vox_xy, vox_z"]["value"]
        n_vox_x = int((crop_width / vox_xy_value) * det_x_to_use)
        self.local_session_dict["n_vox_x_n_vox_y_mode"] = config["n_vox_x, n_vox_y"]["mode"]
        self.local_session_dict["n_vox_x_y_value"] = n_vox_x
        self.local_session_dict["n_vox_x_value"] = n_vox_x
        self.local_session_dict["n_vox_y_value"] = n_vox_x

        crop_height = session_dict['crop']['to slice - from slice']
        det_y_to_use = config["det_x, det_y"]["value"]
        vox_z_value = config["vox_xy, vox_z"]["value"]
        n_vox_z = int((crop_height / vox_z_value) * det_y_to_use)

        self.local_session_dict["n_vox_z_value"] = n_vox_z
        self.local_session_dict["n_vox_z_mode"] = config["n_vox_z"]["mode"]

        self.local_session_dict["write_output_flag"] = config["write output"]

        self.update_widgets()
        self.nbr_vox_xy_clicked()
        self.nbr_vox_z_clicked()
        self.det_clicked()
        self.vox_clicked()

    def export_reconstruction_dictionary_clicked(self):
        export_file_name = QFileDialog.getSaveFileName(self.parent,
                                                       directory=self.parent.homepath,
                                                       caption="Select the location and the file name ...",
                                                       filter="reconstruction json (*.json)",
                                                       initialFilter="reconstruction")
        QApplication.processEvents()
        export_file_name = export_file_name[0]

        if export_file_name:
            self.save_widgets()
            o_advanced = GeneralSettingsHandler(parent=self.parent)
            reconstruction_algorithm_selected = o_advanced.get_reconstruction_algorithm_selected()
            o_dictionary = AlgorithmDictionaryCreator(parent=self.parent,
                                                      algorithm_selected=reconstruction_algorithm_selected)
            o_dictionary.build_dictionary()
            dictionary_of_arguments = o_dictionary.get_dictionary()
            logging.info(f"Exporting dictionary into json:")
            logging.info(f"-> dictionary: {dictionary_of_arguments}")
            logging.info(f"-> reconstruction algorithm selected: {reconstruction_algorithm_selected}")
            logging.info(f"-> output file name: {export_file_name}")

            with open(export_file_name, 'w') as outfile:
                json.dump(dictionary_of_arguments, outfile)

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
        exporting_file_frequency = self.ui.exporting_file_frequency_spinBox.value()

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

        n_vox_x_y_value = self.ui.n_vox_x_n_vox_y_linked_spinBox.value()
        n_vox_x = self.ui.n_vox_x_user_not_linked_spinBox.value()
        n_vox_y = self.ui.n_vox_y_user_not_linked_spinBox.value()
        if self.ui.n_vox_x_y_fixed_radioButton.isChecked():
            n_vox_x_y_mode = "fixed"
            n_vox_x_to_use = int(float(self.ui.n_vox_x_n_vox_y_fixed_value.text()))
            n_vox_y_to_use = n_vox_x_to_use
        elif self.ui.n_vox_x_y_user_radioButton.isChecked():
            n_vox_x_y_mode = "user_linked"
            n_vox_x_to_use = n_vox_x_y_value
            n_vox_y_to_use = n_vox_x_to_use
        else:
            n_vox_x_y_mode = "user_not_linked"
            n_vox_x_to_use = n_vox_x
            n_vox_y_to_use = n_vox_y

        n_vox_z = self.ui.n_vox_z_user_spinBox.value()
        if self.ui.n_vox_z_fixed_radioButton.isChecked():
            n_vox_z_mode = "fixed"
            n_vox_z_to_use = int(float(self.ui.n_vox_z_fixed_value.text()))
        else:
            n_vox_z_mode = "user"
            n_vox_z_to_use = n_vox_z

        write_output_flag = self.ui.write_output_checkBox.isChecked()

        self.parent.session_dict["advanced settings"] = {"wavelet level": wavelet_level,
                                                         "max number of iterations": max_number_of_iterations,
                                                         "stop threshold": stop_threshold,
                                                         "number of cores": number_of_cores,
                                                         "number of gpus": number_of_gpus,
                                                         "median filter size": median_filter_size,
                                                         "exporting file frequency": exporting_file_frequency,
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
                                                         "n_vox_x, n_vox_y": {"mode": n_vox_x_y_mode,
                                                                              "n_vox_x_y": n_vox_x_y_value,
                                                                              "n_vox_x": n_vox_x,
                                                                              "n_vox_y": n_vox_y,
                                                                              "n_vox_x_to_use": n_vox_x_to_use,
                                                                              "n_vox_y_to_use": n_vox_y_to_use,
                                                                              },
                                                         "n_vox_z": {"mode": n_vox_z_mode,
                                                                     "n_vox_z": n_vox_z,
                                                                     "n_vox_z_to_use": n_vox_z_to_use},
                                                         "write output": write_output_flag,
                                                         }
