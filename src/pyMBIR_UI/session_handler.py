from dataio import DataType
from qtpy.QtWidgets import QFileDialog, QApplication
import json
import numpy as np
import logging

from .import_data_handler import ImportDataHandler
from .status_message_config import StatusMessageStatus, show_status_message
from .utilities.get import Get

class SessionHandler:

    config_file_name = ""
    load_successful = True

    def __init__(self, parent=None):
        self.parent = parent

    def save_from_ui(self):
        session_dict = {}

        # import data tab
        list_ui = self.parent.list_ui

        def retrieve_infos_from_import_data(data_type=DataType.sample):
            folder = str(list_ui['folder lineEdit'][data_type].text())
            first_file = str(list_ui['first file comboBox'][data_type].currentText())
            last_file = str(list_ui['last file comboBox'][data_type].currentText())
            first_file_index = list_ui['first file comboBox'][data_type].currentIndex()
            last_file_index = list_ui['last file comboBox'][data_type].currentIndex()

            nbr_files = list_ui['first file comboBox'][data_type].count()
            full_list_files = []
            for _file_index in np.arange(nbr_files):
                full_list_files.append(list_ui['first file comboBox'][data_type].itemText(_file_index))

            return {'folder': folder,
                    'first file': first_file,
                    'first file index': first_file_index,
                    'last file': last_file,
                    'last file index': last_file_index,
                    'full list': full_list_files}

        # sample, ob and di
        session_dict[DataType.sample] = retrieve_infos_from_import_data(data_type=DataType.sample)
        session_dict[DataType.ob] = retrieve_infos_from_import_data(data_type=DataType.ob)
        session_dict[DataType.di] = retrieve_infos_from_import_data(data_type=DataType.di)

        # roi
        session_dict['sample region of interest ([y0,y1,x0,x1])'] = self.parent.sample_roi_list
        session_dict['norm region of interest ([y0,y1,x0,x1])'] = self.parent.norm_roi_list
        session_dict['use norm region of interest'] = self.parent.ui.use_normalization_roi_checkBox.isChecked()

        # filters tab
        session_dict['sample/ob gamma filter'] = self.parent.ui.pre_processing_sample_ob_checkBox.isChecked()
        session_dict['sample/ob threshold 3x3'] = self.parent.ui.sample_ob_threshold1_spinBox.value()
        session_dict['sample/ob threshold 5x5'] = self.parent.ui.sample_ob_threshold2_spinBox.value()
        session_dict['sample/ob threshold 7x7'] = self.parent.ui.sample_ob_threshold3_spinBox.value()
        session_dict['sample/ob sigma for LoG'] = self.parent.ui.sample_ob_sigma_for_log_spinBox.value()
        
        session_dict['dc gamma filter'] = self.parent.ui.pre_processing_di_checkBox.isChecked()
        session_dict['dc threshold 3x3'] = self.parent.ui.di_threshold1_spinBox.value()
        session_dict['dc threshold 5x5'] = self.parent.ui.di_threshold2_spinBox.value()
        session_dict['dc threshold 7x7'] = self.parent.ui.di_threshold3_spinBox.value()
        session_dict['dc sigma for LoG'] = self.parent.ui.di_sigma_for_log_spinBox.value()

        session_dict['image binning size'] = self.parent.ui.pre_processing_binned_pixels_spinBox.value()
        session_dict['image binning flag'] = self.parent.ui.pre_processing_image_binning_checkBox.isChecked()
        session_dict['outlier removal in epithermal dc'] = \
            self.parent.ui.pre_processing_outlier_threshold_spinBox.value()
        session_dict['outlier removal in epithermal dc flag'] = \
            self.parent.ui.pre_processing_outlier_checkBox.isChecked()

        # fitting tab
        session_dict['fit procedure index selected'] = \
            self.parent.ui.pre_processing_fitting_procedure_comboBox.currentIndex()
        # combo_box = self.parent.ui.pre_processing_fitting_procedure_comboBox
        # setattr(combo_box, "allItems", lambda: [combo_box.itemText(i) for i in range(combo_box.count())])
        # # session_dict['fit procedure list'] = combo_box.allItems()

        # general settings
        session_dict["general settings"] = self._retrieve_general_settings()
        session_dict["default_instrument"] = self.parent.selected_instrument

        self.parent.session_dict = session_dict

    def save_to_file(self, config_file_name=None):

        if config_file_name is None:
            config_file_name = QFileDialog.getSaveFileName(self.parent,
                                                           caption="Select session file name ...",
                                                           directory=self.parent.homepath,
                                                           filter="session (*.json)",
                                                           initialFilter="session")

            QApplication.processEvents()
            config_file_name = config_file_name[0]

        if config_file_name:
            output_file_name = config_file_name
            session_dict = self.parent.session_dict
            with open(output_file_name, 'w') as json_file:
                json.dump(session_dict, json_file)

            show_status_message(parent=self.parent,
                                message=f"Session saved in {config_file_name}",
                                status=StatusMessageStatus.ready,
                                duration_s=10)
            logging.info(f"Saving configuration into {config_file_name}")

    def load_from_file(self, config_file_name=None):

        if config_file_name is None:
            config_file_name = QFileDialog.getOpenFileName(self.parent,
                                                           directory=self.parent.homepath,
                                                           caption="Select session file ...",
                                                           filter="session (*.json)",
                                                           initialFilter="session")
            QApplication.processEvents()
            config_file_name = config_file_name[0]

        if config_file_name:
            config_file_name = config_file_name
            self.config_file_name = config_file_name
            show_status_message(parent=self.parent,
                                message=f"Loading {config_file_name} ...",
                                status=StatusMessageStatus.ready)

            with open(config_file_name, "r") as read_file:
                self.parent.session_dict = json.load(read_file)
            logging.info(f"Loaded from {config_file_name}")

        else:
            self.load_successful = False

    def load_to_ui(self):

        if not self.load_successful:
            return

        session_dict = self.parent.session_dict
        list_ui = self.parent.list_ui

        list_load_method = {DataType.sample: self.parent.sample_data_load_button_clicked,
                            DataType.ob: self.parent.open_beam_load_button_clicked,
                            DataType.di: self.parent.dark_image_load_button_clicked}

        for data_type in self.parent.list_files.keys():

            _session = session_dict[data_type]
            first_file_index = _session['first file index']
            last_file_index = _session['last file index']
            full_list = _session['full list']
            folder = _session['folder']

            o_import = ImportDataHandler(parent=self.parent, data_type=data_type)
            o_import.update_widgets_with_list_of_files(folder_name=folder)

            list_ui['first file comboBox'][data_type].setCurrentIndex(first_file_index)
            list_ui['last file comboBox'][data_type].setCurrentIndex(last_file_index)

            # load data
            if full_list:
                list_load_method[data_type](None)
                logging.info(f"Loading data: {data_type}")

            # only for sample data type, update roi list of files
            if data_type == DataType.sample:
                self.parent.ui.pre_processing_sample_run_comboBox.clear()
                self.parent.ui.pre_processing_sample_run_comboBox.addItems(full_list)

        # general settings
        general_settings = session_dict["general settings"]
        self.parent.ui.number_of_scanned_periods_spinBox.setValue(general_settings["number of scanned periods"])
        self.parent.selected_instrument = session_dict["default_instrument"]

        # roi
        self.parent.sample_roi_list = session_dict['sample region of interest ([y0,y1,x0,x1])']
        self.parent.norm_roi_list = session_dict['norm region of interest ([y0,y1,x0,x1])']

        full_period_true = general_settings["full period"]
        if full_period_true:
            self.parent.ui.full_period_true_radioButton.setChecked(True)
        else:
            self.parent.ui.full_period_false_radioButton.setChecked(True)
        self.parent.ui.rotation_of_g0rz_doubleSpinBox.setValue(general_settings["rotation of g0rz"])
        self.parent.ui.images_per_step_spinBox.setValue(general_settings["number of images per step"])

        # filters tab
        self.parent.ui.pre_processing_sample_ob_checkBox.setChecked(session_dict['sample/ob gamma filter'])
        self.parent.ui.sample_ob_threshold1_spinBox.setValue(session_dict['sample/ob threshold 3x3'])
        self.parent.ui.sample_ob_threshold2_spinBox.setValue(session_dict['sample/ob threshold 5x5'])
        self.parent.ui.sample_ob_threshold3_spinBox.setValue(session_dict['sample/ob threshold 7x7'])
        self.parent.ui.sample_ob_sigma_for_log_spinBox.setValue(session_dict['sample/ob sigma for LoG'])

        self.parent.ui.pre_processing_di_checkBox.setChecked(session_dict['dc gamma filter'])
        self.parent.ui.di_threshold1_spinBox.setValue(session_dict['dc threshold 3x3'])
        self.parent.ui.di_threshold2_spinBox.setValue(session_dict['dc threshold 5x5'])
        self.parent.ui.di_threshold3_spinBox.setValue(session_dict['dc threshold 7x7'])
        self.parent.ui.di_sigma_for_log_spinBox.setValue(session_dict['dc sigma for LoG'])

        self.parent.ui.pre_processing_binned_pixels_spinBox.setValue(session_dict['image binning size'])
        self.parent.ui.pre_processing_image_binning_checkBox.setChecked(session_dict['image binning flag'])
        self.parent.ui.pre_processing_outlier_threshold_spinBox.setValue(session_dict['outlier removal in ' \
                                                                                        'epithermal dc'])
        self.parent.ui.pre_processing_outlier_checkBox.setChecked(session_dict['outlier removal in epithermal dc flag'])

        # fitting tab
        # self.parent.ui.pre_processing_fitting_procedure_comboBox.clear()
        # self.parent.ui.pre_processing_fitting_procedure_comboBox.addItems(session_dict['fit procedure list'])
        self.parent.ui.pre_processing_fitting_procedure_comboBox.setCurrentIndex(
                session_dict['fit procedure index selected'])

        self.parent.pre_processing_widgets_changed()

        # status of norm roi error message
        self.parent.use_normalization_roi_clicked(True)

        show_status_message(parent=self.parent,
                            message=f"Loaded {self.config_file_name}",
                            status=StatusMessageStatus.ready,
                            duration_s=10)

    def _retrieve_general_settings(self):
        number_of_scanned_periods = self.parent.ui.number_of_scanned_periods_spinBox.value()
        full_period_true = self.parent.ui.full_period_true_radioButton.isChecked()
        rotation_of_g0rz = self.parent.ui.rotation_of_g0rz_doubleSpinBox.value()
        images_per_step = self.parent.ui.images_per_step_spinBox.value()
        general_settings = {'number of scanned periods': number_of_scanned_periods,
                            'full period': full_period_true,
                            'rotation of g0rz': rotation_of_g0rz,
                            'number of images per step': images_per_step}
        return general_settings

    def automatic_save(self):
        o_get = Get(parent=self.parent)
        full_config_file_name = o_get.get_automatic_config_file_name()
        self.save_to_file(config_file_name=full_config_file_name)
