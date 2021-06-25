from qtpy.QtWidgets import QFileDialog, QApplication
import json
import logging
import numpy as np

from .import_data_handler import ImportDataHandler
from .status_message_config import StatusMessageStatus, show_status_message
from .utilities.get import Get
from . import DataType
from .crop_handler import CropHandler


class SessionHandler:

    config_file_name = ""
    load_successful = True

    def __init__(self, parent=None):
        self.parent = parent

    def save_from_ui(self):
        session_dict = {}

        # import input tab data
        list_ui = self.parent.list_ui

        def retrieve_infos_from_import_data(data_type=DataType.projections):
            folder = str(list_ui['select lineEdit'][data_type].text())
            return {'folder': folder}

        # projections, ob, df
        session_dict[DataType.projections] = retrieve_infos_from_import_data(data_type=DataType.projections)
        session_dict[DataType.ob] = retrieve_infos_from_import_data(data_type=DataType.ob)
        session_dict[DataType.df] = retrieve_infos_from_import_data(data_type=DataType.df)

        # output folder
        session_dict[DataType.output] = {'folder': str(list_ui['select lineEdit'][DataType.output].text())}

        # crop tab
        crop_state = self.parent.ui.cropping_checkBox.isChecked()
        crop_width = self.parent.ui.crop_width_horizontalSlider.value()
        crop_from_slice = np.int(self.parent.ui.crop_from_slice_label.text())
        crop_to_slice = np.int(self.parent.ui.crop_to_slice_label.text())
        file_index = self.parent.ui.crop_file_index_horizontalSlider.value()
        crop_dict ={'state': crop_state,
                    'width': crop_width,
                    'from slice': crop_from_slice,
                    'to slice': crop_to_slice,
                    'file index': file_index}
        session_dict['crop'] = crop_dict

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
                                status=StatusMessageStatus.ready,
                                duration_s=10)

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

        list_load_method = {DataType.projections: self.parent.projections_text_field_returned,
                            DataType.ob: self.parent.ob_text_field_returned,
                            DataType.df: self.parent.df_text_field_returned,
                            DataType.output: self.parent.output_folder_text_field_returned}

        # input tab
        for data_type in list_load_method.keys():
            _session = session_dict[data_type]
            folder = _session['folder']
            list_ui['select lineEdit'][data_type].setText(folder)
            list_load_method[data_type]()

        o_crop = CropHandler(parent=self.parent)
        o_crop.initialize_crop()

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
