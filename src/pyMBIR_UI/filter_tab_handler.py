from qtpy.QtWidgets import QDialog
import os
import logging
import numpy as np
import copy
import time

from dataio import DataType

from . import load_ui
from .utilities.get import Get
from .algorithms.gamma_spots_removal import gam_rem_adp_log
from .ngI_tool import ngItool as ngI
from .filter_preview import Filter_Preview
from .status_message_config import show_status_message, StatusMessageStatus
from .algorithms.epithermal_correction import epithermal_correction


class FilterTabHandler:

    list_filters_ui = None

    def __init__(self, parent=None):
        self.parent = parent
        self.list_filters_ui = self.parent.list_ui['filters']

    def update_widgets(self):
        """update the state of all the widgets (enabled or not) according to various checkboxes states"""

        pre_processing_sample_ob_checkBox_state = self.parent.ui.pre_processing_sample_ob_checkBox.isChecked()
        self.parent.ui.pre_processing_sample_ob_frame.setEnabled(pre_processing_sample_ob_checkBox_state)

        pre_processing_di_checkBox_state = self.parent.ui.pre_processing_di_checkBox.isChecked()
        self.parent.ui.pre_processing_di_frame.setEnabled(pre_processing_di_checkBox_state)

        pre_processing_image_binning_checkBox_state = self.parent.ui.pre_processing_image_binning_checkBox.isChecked()
        self.parent.ui.pre_processing_binned_pixels_label.setEnabled(pre_processing_image_binning_checkBox_state)
        self.parent.ui.pre_processing_binned_pixels_spinBox.setEnabled(pre_processing_image_binning_checkBox_state)

        pre_processing_outlier_checkBox_state = self.parent.ui.pre_processing_outlier_checkBox.isChecked()
        self.parent.ui.pre_processus_outlier_label.setEnabled(pre_processing_outlier_checkBox_state)
        self.parent.ui.pre_processing_outlier_threshold_spinBox.setEnabled(pre_processing_outlier_checkBox_state)

    def update_tab_content(self):
        if self.parent.selected_instrument == "ANTARES":
            show_outlier_removal_dc = True
        else:
            show_outlier_removal_dc = False
        list_outlier_ui = [self.parent.ui.pre_processing_outlier_checkBox,
                           self.parent.ui.pre_processus_outlier_label,
                           self.parent.ui.pre_processing_outlier_threshold_spinBox]
        for _ui in list_outlier_ui:
            _ui.setVisible(show_outlier_removal_dc)

    def gamma_filtering_help_clicked(self):
        o_help = GammaFilteringHelp(parent=self.parent)
        o_help.show()
        self.parent.gamma_help_id = o_help
        self.parent.ui.gamma_filtering_help_pushButton.setEnabled(False)

    def get_data_type_selected(self):
        if self.parent.ui.filter_sample_radioButton.isChecked():
            return DataType.sample
        elif self.parent.ui.filter_open_beam_radioButton.isChecked():
            return DataType.ob
        else:
            return DataType.di

    def data_run_to_use_radioButton_clicked(self):
        data_type = self.get_data_type_selected()
        working_list_of_files = self.parent.working_list_files[data_type]
        self.parent.ui.filter_data_to_use_comboBox.clear()
        if working_list_of_files:
            self.parent.ui.filter_data_to_use_comboBox.addItems(working_list_of_files)

    def test_filters_button_clicked(self):

        show_status_message(parent=self.parent,
                            message="testing filters ... IN PROGRESS",
                            status=StatusMessageStatus.working)
        start_time = time.time()
        test_name = ""

        file_name_image_to_test = str(self.parent.ui.filter_data_to_use_comboBox.currentText())
        o_get = Get(parent=self.parent)
        data_type = self.get_data_type_selected()
        image_to_test = o_get.get_data_of_file_with_data_type(file_name=file_name_image_to_test,
                                                              data_type=data_type)
        logging.info(f"Testing filters using {data_type}: {file_name_image_to_test}")

        # crop
        image, method_log = self.apply_crop(data=image_to_test)
        test_name += " " + method_log if method_log else ""
        image_cropped = copy.deepcopy(image)

        # binning of crop image (just to display before and after
        image_before, method_log = self.apply_binning(data=image_cropped)
        self.parent.test_filters_list['image'].append(image_before)

        # gamma
        image, image_parameters, method_log = self.apply_gamma_filter(data=image,
                                                                      data_type=data_type)
        test_name += " " + method_log if method_log else ""

        # binning
        image, method_log = self.apply_binning(data=image)
        height, width = np.shape(image)
        test_name += " " + method_log if method_log else ""

        # epithermal correciton
        image, method_log = self.apply_epithermal_correction(data=image)
        test_name += " " + method_log if method_log else ""

        self.parent.test_filters_list['name'].append(test_name)
        test_time = time.time() - start_time
        self.parent.test_filters_list['image_filtered'].append(image)



        # visualize results
        o_preview = Filter_Preview("Processing Preview", self.parent)
        list_ui = self.parent.list_ui['filters']['gamma']
        threshold1_value = list_ui[data_type]['threshold1'].value()
        threshold2_value = list_ui[data_type]['threshold2'].value()
        threshold3_value = list_ui[data_type]['threshold3'].value()
        sigma_for_log_value = list_ui[data_type]['sigma for log'].value()
        bin_value = self.parent.ui.pre_processing_binned_pixels_spinBox.value()

        test_para = [image_parameters[0],
                     image_parameters[1],
                     image_parameters[2],
                     image_parameters[3],
                     threshold1_value,
                     threshold2_value,
                     threshold3_value,
                     sigma_for_log_value,
                     test_time,
                     1,
                     bin_value,
                     height,
                     width,
                     [],   #  self.parent.sample_roi_list,
                     ]
        self.parent.test_filters_list['parameters'].append(test_para)

        o_preview.add_filtered(self.parent.test_filters_list['name'],
                               self.parent.test_filters_list['image'],
                               self.parent.test_filters_list['image_filtered'],
                               self.parent.test_filters_list['parameters'])
        o_preview.show()
        show_status_message(parent=self.parent,
                            message="testing filters: Done!",
                            status=StatusMessageStatus.working,
                            duration_s=10)


    def apply_crop(self, data=None):
        data = copy.deepcopy(data)
        if self.parent.sample_roi_list:
            y0, y1, x0, x1 = self.parent.sample_roi_list
            logging.info(f"-> crop data using y0:{y0}, y1:{y1}, x0:{x0}, x1:{x1}")
            cropped_data = data[y0: y1, x0: x1]
            return cropped_data, f"crop (y0, y1, x0, x1)=({y0}, {y1}, {x0}, {x1}"
        else:
            return data, ""

    def apply_gamma_filter(self, data=None, data_type=DataType.sample):
        """apply the gamma filter and return the new image and the parameters n3, n5, n7 and time it took to process it
        """
        data = copy.deepcopy(data)

        if data_type in [DataType.sample, DataType.ob]:
            is_apply_gamma_checked = self.parent.ui.pre_processing_sample_ob_checkBox.isChecked()
        else:
            is_apply_gamma_checked = self.parent.ui.pre_processing_di_checkBox.isChecked()

        logging.info(f"-> apply gamma filter: {is_apply_gamma_checked}")
        if is_apply_gamma_checked:
            threshold3, threshold5, threshold7, sigma_for_log = self._get_gamma_filter(data_type=data_type)
            image, image_parameters = gam_rem_adp_log(data,
                                                      thr3=threshold3,
                                                      thr5=threshold5,
                                                      thr7=threshold7,
                                                      sig_log=sigma_for_log)
            logging.info(f"-> gamma filter took: {image_parameters[-1]} seconds")
            method_log = f"gamma (3x3 filter: {threshold3}, " \
                         f"5x5 filter: {threshold5}, " \
                         f"7x7 filter: {threshold7}, " \
                         f"sigma LoG: {sigma_for_log}"
            return image, image_parameters, method_log
        else:
            return data, [0, 0, 0, 0], ""

    def apply_binning(self, data=None):
        is_apply_binning_filter = self.parent.ui.pre_processing_image_binning_checkBox.isChecked()
        logging.info(f"-> apply binning filter: {is_apply_binning_filter}")
        if is_apply_binning_filter:
            data = copy.deepcopy(data)
            bin_value = self.parent.ui.pre_processing_binned_pixels_spinBox.value()
            logging.info(f"--> binning value: {bin_value}")
            bin_image = ngI.rebin(data, bin_value)
            method_log = f"binning ({bin_value}x{bin_value})"
            return bin_image, method_log
        else:
            return data, ""

    def _get_gamma_filter(self, data_type=DataType.sample):
        list_ui = self.parent.list_ui['filters']['gamma']
        threshold1_value = list_ui[data_type]['threshold1'].value()
        threshold2_value = list_ui[data_type]['threshold2'].value()
        threshold3_value = list_ui[data_type]['threshold3'].value()
        sigma_for_log_value = list_ui[data_type]['sigma for log'].value()

        return threshold1_value, threshold2_value, threshold3_value, sigma_for_log_value

    def apply_epithermal_correction(self, data=None):
        is_apply_epithermal_correction = self.parent.ui.pre_processing_outlier_checkBox.isChecked()
        logging.info(f"-> apply epithermal correction: {is_apply_epithermal_correction}")
        if is_apply_epithermal_correction:
            data = copy.deepcopy(data)
            threshold = self.parent.ui.pre_processing_outlier_threshold_spinBox.value()
            new_data = epithermal_correction(image=data, threshold=threshold)
            logging.info(f"--> threshold: {threshold}")
            method_log = f"epithermal correction th:{threshold}"
            return data, method_log
        else:
            return data, ""


class GammaFilteringHelp(QDialog):

    def __init__(self, parent=None):
        self.parent = parent
        QDialog.__init__(self, parent=parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'gamma_filtering_help.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)

    def closeEvent(self, e):
        self.parent.ui.gamma_filtering_help_pushButton.setEnabled(True)
        self.close()

    def close_dialog(self):
        self.parent.ui.gamma_filtering_help_pushButton.setEnabled(True)
        self.close()

