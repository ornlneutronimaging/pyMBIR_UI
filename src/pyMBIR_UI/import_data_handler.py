from qtpy.QtWidgets import QFileDialog
import os
import logging

from NeuNorm.normalization import Normalization

from .status_message_config import show_status_message, StatusMessageStatus
from .utilities.file_utilities import get_list_files, get_list_file_extensions
from . import DataType, normal_style, error_style, interact_me_style, file_extension_accepted
from pyMBIR_UI.crop.crop_handler import CropHandler
from pyMBIR_UI.center_of_rotation.center_of_rotation import CenterOfRotation
from pyMBIR_UI.tilt.tilt_handler import TiltHandler
from .loader import Loader
from pyMBIR_UI import SessionKeys


class ImportDataHandler:
    list_ui = None

    def __init__(self, parent=None, data_type=DataType.projections):
        """
        Parameters:
        data_type: DataType object (DataType.projections, ob or df)
        """
        self.parent = parent
        self.data_type = data_type
        self.list_ui = self.parent.list_ui

    # projections, ob and df
    def browse_via_filedialog(self):
        """
        retrieve the full list of files found in the defined location
        """
        folder_name = QFileDialog.getExistingDirectory(self.parent,
                                                       caption='Select directory',
                                                       directory=self.parent.session_dict[SessionKeys.homepath])
        if len(folder_name) > 0:
            logging.info(f"browse {self.data_type} via file dialog: {folder_name}")
            self.update_widgets_with_name_of_folder(folder_name=folder_name)
            if self.data_type == DataType.projections:
                self.parent.session_dict[SessionKeys.homepath] = os.path.dirname(folder_name)
        else:
            logging.info(f"User cancel browsing for {self.data_type}")

    def browse_via_manual_input(self):
        folder_name = self.list_ui['select lineEdit'][self.data_type].text()
        logging.info(f"browse {self.data_type} via manual input: {folder_name}")
        self.update_widgets_with_name_of_folder(folder_name=folder_name)

    # output folder
    def browse_output_folder_via_filedialog(self):
        folder_name = QFileDialog.getExistingDirectory(self.parent,
                                                       caption='Select directory',
                                                       directory=self.parent.session_dict[SessionKeys.homepath])
        if len(folder_name) > 0:
            logging.info(f"select output folder: {folder_name}")
            self.parent.ui.output_folder_lineEdit.setText(folder_name)
            self.activate_next_data_type()
            show_status_message(parent=self.parent,
                                message=f"Output folder selected",
                                status=StatusMessageStatus.ready,
                                duration_s=5)
            self.list_ui['select lineEdit'][self.data_type].setStyleSheet(normal_style)
        else:
            logging.info(f"User cancel browsing for {self.data_type}")

    def browse_output_folder_via_manual_input(self):
        folder_name = self.parent.ui.output_folder_lineEdit.text()
        if folder_name == "":
            return

        if os.path.exists(folder_name):
            logging.info(f"select output folder: {folder_name}")
            self.list_ui['select lineEdit'][self.data_type].setStyleSheet(normal_style)
            self.activate_next_data_type()
            show_status_message(parent=self.parent,
                                message=f"Output folder selected",
                                status=StatusMessageStatus.ready,
                                duration_s=5)
        else:
            show_status_message(parent=self.parent,
                                message=f"Folder does not exist! Create folder first.",
                                status=StatusMessageStatus.error,
                                duration_s=5)
            logging.info(f"You need to create the folder {folder_name}!")
            self.list_ui['select lineEdit'][self.data_type].setStyleSheet(error_style)
            self.deactivate_next_data_type()

        self.parent.ui.output_folder_lineEdit.setText(folder_name)

    def update_widgets_with_name_of_output_folder(self, folder_name=""):
        if len(folder_name) == 0:
            return

        show_status_message(parent=self.parent,
                            message=f"{self.data_type} folder selected!",
                            status=StatusMessageStatus.ready,
                            duration_s=5)
        self.list_ui['select lineEdit'][self.data_type].setStyleSheet(normal_style)
        self.list_ui['select lineEdit'][self.data_type].setText(folder_name)
        self.list_ui['select button'][self.data_type].setStyleSheet(normal_style)

    def update_widgets_with_name_of_folder(self, folder_name="./"):
        """
        this retrieve the list of files and then updated the widgets such as clear comboBox,
        populate them with list of files, and enable
        or not the widgets if files have been found or not.
        """
        if len(folder_name) == 0:
            return

        self.list_ui['select lineEdit'][self.data_type].setText(folder_name)
        folder_name = os.path.abspath(folder_name)

        if not os.path.exists(folder_name):
            # folder does not exist
            show_status_message(parent=self.parent,
                                message=f"{self.data_type} folder does not exist!",
                                status=StatusMessageStatus.error,
                                duration_s=5)
            logging.info(f"-> folder does not exist!")
            self.list_ui['select lineEdit'][self.data_type].setStyleSheet(error_style)

        else:
            self.list_ui['select lineEdit'][self.data_type].setStyleSheet(normal_style)

            list_of_files, list_of_files_extension = self.retrieve_list_of_files(folder_name=folder_name)

            if len(list_of_files_extension) > 1:
                show_status_message(parent=self.parent,
                                    message=f"More than 2 data format type in the same folder!",
                                    status=StatusMessageStatus.error,
                                    duration_s=5)
                logging.info(f"-> Folder contains several data type format!")
                logging.info(f"--> {list_of_files_extension}")

            elif not list_of_files:
                show_status_message(parent=self.parent,
                                    message=f"Folder is empty",
                                    status=StatusMessageStatus.error,
                                    duration_s=5)
                logging.info(f"-> Folder is empty!")

            elif not ImportDataHandler.accepted_file_extension(list_of_files_extension[0]):
                show_status_message(parent=self.parent,
                                    message=f"Incorrect file format: {list_of_files_extension[0]}",
                                    status=StatusMessageStatus.error,
                                    duration_s=5)
                logging.info(f"-> Wrong file extension")
                logging.info(f"--> file extension found: {list_of_files_extension[0]}")
                logging.info(f"--> list of file extension expected: {file_extension_accepted}")

            else:
                logging.info(f"--> number of files: {len(list_of_files)}")
                logging.info(f"--> extension: {list_of_files_extension[0]}")

                data_image_list = [None for _ in list_of_files]
                self.parent.input['data'][self.data_type] = data_image_list
                self.parent.input['list files'][self.data_type] = list_of_files

                o_loader = Loader(parent=self.parent,
                                  data_type=self.data_type)
                o_loader.load_data(file_index=0)
                o_loader.load_angles()

                if self.parent.preview_id:
                    self.parent.preview_id.update_radiobuttons_state()

                show_status_message(parent=self.parent,
                                    message="",
                                    status=StatusMessageStatus.ready)
                self.activate_next_data_type()
                self.parent.check_preview_button_status()

    def retrieve_list_of_files(self, folder_name="./"):
        list_files = get_list_files(directory=folder_name, file_extension=["*.fits", "*.tiff", "*.tif"])
        list_files.sort()
        list_extension = get_list_file_extensions(list_filename=list_files)
        return list_files, list_extension

    @staticmethod
    def accepted_file_extension(file_extension):
        for _file in file_extension_accepted:
            if _file in file_extension:
                return True
        return False

    def activate_next_data_type(self):
        previous_style = normal_style
        new_style = interact_me_style
        new_state = True
        self.change_next_data_type(previous_style=previous_style,
                                   new_style=new_style,
                                   new_state=new_state)

    def deactivate_next_data_type(self):
        previous_style = interact_me_style
        new_style = normal_style
        new_state = False
        self.change_next_data_type(previous_style=previous_style,
                                   new_style=new_style,
                                   new_state=new_state)

    def change_next_data_type(self, previous_style=normal_style, new_style=interact_me_style, new_state=True):

        list_data_type = [DataType.projections, DataType.ob, DataType.df, DataType.output]
        index_data_type = list_data_type.index(self.data_type)

        if index_data_type == 0:
            o_crop = CropHandler(parent=self.parent)
            o_crop.clean_all_items()
            o_crop.initialize_crop()
            o_crop.master_checkbox_clicked()

            o_center = CenterOfRotation(parent=self.parent)
            o_center.initialization()

            o_tilt = TiltHandler(parent=self.parent)
            o_tilt.initialize_tilt_correction()
            o_tilt.master_checkBox_clicked()
            o_tilt.correction_algorithm_changed()

        if index_data_type == len(list_data_type) - 1:
            # activate reconstitution setup tab
            self.parent.ui.tabWidget.setTabEnabled(1, new_state)
            # activate general settings tab
            self.parent.ui.tabWidget.setTabEnabled(2, new_state)
            # activate button that launch advanced window
            self.parent.ui.actionAdvanced_Settings.setEnabled(True)

        else:
            next_data_type = list_data_type[index_data_type+1]

            # no need to check widgets as we already loaded some data for this data type
            if not (next_data_type == DataType.output):
                if not (self.parent.input['data'][next_data_type] is None):
                    return

            self.list_ui['select button'][self.data_type].setStyleSheet(previous_style)
            self.list_ui['select button'][next_data_type].setStyleSheet(new_style)
            self.list_ui['select button'][next_data_type].setEnabled(new_state)
            self.list_ui['select lineEdit'][next_data_type].setEnabled(new_state)

        if self.data_type == DataType.projections:
            self.parent.ui.select_projections_pushButton.setStyleSheet(previous_style)
            self.parent.ui.select_ob_pushButton.setStyleSheet(new_style)
            self.parent.ui.ob_lineEdit.setEnabled(new_state)
            self.parent.ui.select_ob_pushButton.setEnabled(new_state)
        elif self.data_type == DataType.ob:
            self.parent.ui.select_ob_pushButton.setStyleSheet(previous_style)
            self.parent.ui.select_df_pushButton.setStyleSheet(new_style)
            self.parent.ui.df_lineEdit.setEnabled(new_state)
            self.parent.ui.select_df_pushButton.setEnabled(new_state)
        elif self.data_type == DataType.df:
            self.parent.ui.select_df_pushButton.setStyleSheet(previous_style)
            self.parent.ui.select_output_folder_pushButton.setStyleSheet(new_style)
            self.parent.ui.output_folder_lineEdit.setEnabled(new_state)
            self.parent.ui.select_output_folder_pushButton.setEnabled(new_state)
        elif self.data_type == DataType.output:
            self.parent.ui.select_output_folder_pushButton.setStyleSheet(previous_style)

    def loading_data(self, index=0):
        """
        method that only load the index specified

        Return:
            status of the loading (True or False)
        """
        # load_success = False
        # data_type = self.data_type

        list_of_files  = self.parent.input['list files'][self.data_type]
        file_to_load = list_of_files[index]

        o_norm = Normalization()
        o_norm.load(file=file_to_load, notebook=False)

        self.parent.input['data'][self.data_type][index] = o_norm.data['sample']['data'][0]

        return True  # FIX ME, add a try  catch that return False if error is thrown
