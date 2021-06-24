from qtpy.QtWidgets import QFileDialog
from qtpy import QtGui
import os
import logging

from NeuNorm.normalization import Normalization

from .status_message_config import show_status_message, StatusMessageStatus
from .utilities.file_utilities import get_list_files, get_list_file_extensions
from .filter_tab_handler import FilterTabHandler
from . import DataType, normal_style, error_style, interact_me_style, file_extension_accepted


class ImportDataHandler:
    list_ui = None

    def __init__(self, parent=None, data_type=DataType.projections):
        """
        Parameters:
        data_type: DataType object (DataType.projections, ob or df)
        """
        self.parent = parent
        self.data_type = data_type
        # self.config = self.parent.config
        self.list_ui = self.parent.list_ui

    # projections, ob and df
    def browse_via_filedialog(self):
        """
        retrieve the full list of files found in the defined location
        """
        folder_name = QFileDialog.getExistingDirectory(self.parent,
                                                       caption='Select directory',
                                                       directory=self.parent.homepath)
        if len(folder_name) > 0:
            logging.info(f"browse {self.data_type} via file dialog: {folder_name}")
            self.update_widgets_with_name_of_folder(folder_name=folder_name)
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
                                                       directory=self.parent.homepath)
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
            # show_status_message(parent=self.parent,
            #                     message=f"{self.data_type} folder selected!",
            #                     status=StatusMessageStatus.ready,
            #                     duration_s=5)
            self.list_ui['select lineEdit'][self.data_type].setStyleSheet(normal_style)

            list_of_files, list_of_files_extension = ImportDataHandler.retrieve_list_of_files(folder_name=folder_name)

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

                status = self.loading_data(list_of_files=list_of_files)
                if self.parent.preview_id:
                    self.parent.preview_id.update_radiobuttons_state()

                self.activate_next_data_type()
                self.parent.check_preview_button_status()

    @staticmethod
    def retrieve_list_of_files(folder_name="./"):
        list_files = get_list_files(directory=folder_name, file_extension=["*.fits", "*.tiff", "*.tif"])
        list_extension = get_list_file_extensions(list_filename=list_files)
        return list_files, list_extension

    @staticmethod
    def accepted_file_extension(file_extension):
        for _file in file_extension_accepted:
            if _file in file_extension:
                return True
        return False

    def activate_next_data_type(self):
        list_data_type = [DataType.projections, DataType.ob, DataType.df, DataType.output]
        index_data_type = list_data_type.index(self.data_type)
        if index_data_type == len(list_data_type) - 1:
            self.parent.ui.tabWidget.setTabEnabled(1, True)
        else:
            next_data_type = list_data_type[index_data_type+1]
            self.list_ui['select button'][self.data_type].setStyleSheet(normal_style)
            self.list_ui['select button'][next_data_type].setStyleSheet(interact_me_style)
            self.list_ui['select button'][next_data_type].setEnabled(True)
            self.list_ui['select lineEdit'][next_data_type].setEnabled(True)

        if self.data_type == DataType.projections:
            self.parent.ui.select_projections_pushButton.setStyleSheet(normal_style)
            self.parent.ui.select_ob_pushButton.setStyleSheet(interact_me_style)
            self.parent.ui.ob_lineEdit.setEnabled(True)
            self.parent.ui.select_ob_pushButton.setEnabled(True)
        elif self.data_type == DataType.ob:
            self.parent.ui.select_ob_pushButton.setStyleSheet(normal_style)
            self.parent.ui.select_df_pushButton.setStyleSheet(interact_me_style)
            self.parent.ui.df_lineEdit.setEnabled(True)
            self.parent.ui.select_df_pushButton.setEnabled(True)
        elif self.data_type == DataType.df:
            self.parent.ui.select_df_pushButton.setStyleSheet(normal_style)
            self.parent.ui.select_output_folder_pushButton.setStyleSheet(interact_me_style)
            self.parent.ui.output_folder_lineEdit.setEnabled(True)
            self.parent.ui.select_output_folder_pushButton.setEnabled(True)
        elif self.data_type == DataType.output:
            self.parent.ui.select_output_folder_pushButton.setStyleSheet(normal_style)

    def deactivate_next_data_type(self):
        list_data_type = [DataType.projections, DataType.ob, DataType.df, DataType.output]
        index_data_type = list_data_type.index(self.data_type)
        if index_data_type == len(list_data_type) - 1:
            self.parent.ui.tabWidget.setTabEnabled(1, False)
        else:
            next_data_type = list_data_type[index_data_type+1]
            self.list_ui['select button'][self.data_type].setStyleSheet(interact_me_style)
            self.list_ui['select button'][next_data_type].setStyleSheet(normal_style)
            self.list_ui['select button'][next_data_type].setEnabled(False)
            self.list_ui['select lineEdit'][next_data_type].setEnabled(False)

        if self.data_type == DataType.projections:
            self.parent.ui.select_projections_pushButton.setStyleSheet(interact_me_style)
            self.parent.ui.select_ob_pushButton.setStyleSheet(normal_style)
            self.parent.ui.ob_lineEdit.setEnabled(False)
            self.parent.ui.select_ob_pushButton.setEnabled(False)
        elif self.data_type == DataType.ob:
            self.parent.ui.select_ob_pushButton.setStyleSheet(interact_me_style)
            self.parent.ui.select_df_pushButton.setStyleSheet(normal_style)
            self.parent.ui.df_lineEdit.setEnabled(False)
            self.parent.ui.select_df_pushButton.setEnabled(False)
        elif self.data_type == DataType.df:
            self.parent.ui.select_df_pushButton.setStyleSheet(interact_me_style)
            self.parent.ui.select_output_folder_pushButton.setStyleSheet(normal_style)
            self.parent.ui.output_folder_lineEdit.setEnabled(False)
            self.parent.ui.select_output_folder_pushButton.setEnabled(False)
        else:
            self.parent.ui.select_output_folder_pushButton.setStyleSheet(interact_me_style)

    def loading_data(self, list_of_files=None):
        """
        method that loads the data arrays

        Return:
            status of the loading (True or False)
        """
        # load_success = False
        # data_type = self.data_type

        nbr_files = len(list_of_files)

        self.parent.eventProgress.setMaximum(nbr_files-1)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        dataimage_list = list()
        for _index, _file in enumerate(list_of_files):
            o_norm = Normalization()
            o_norm.load(file=_file, notebook=False)
            dataimage_list.append(o_norm.data['sample']['data'][0])

            self.parent.eventProgress.setValue(_index+1)
            QtGui.QGuiApplication.processEvents()

        self.parent.input['data'][self.data_type] = dataimage_list
        self.parent.input['list files'][self.data_type] = list_of_files

        self.parent.eventProgress.setVisible(False)

        return True  # FIX ME, add a try  catch that return False if error is thrown















    def _fill_list_of_files_combo_boxes(self, list_files=None):
        data_type = self.data_type

        self.list_ui['first file comboBox'][data_type].blockSignals(True)
        self.list_ui['last file comboBox'][data_type].blockSignals(True)
        self.list_ui['first file comboBox'][data_type].addItems(list_files)

        self.list_ui['first file comboBox'][data_type].setCurrentIndex(0)
        self.list_ui['last file comboBox'][data_type].addItems(list_files)
        self.list_ui['last file comboBox'][data_type].setCurrentIndex(len(list_files) - 1)
        self.list_ui['first file comboBox'][data_type].blockSignals(False)
        self.list_ui['last file comboBox'][data_type].blockSignals(False)



    def load(self):
        data_type = self.data_type

        show_status_message(parent=self.parent,
                            message="Loading {} ...".format(self.data_type),
                            status=StatusMessageStatus.working)

        load_success = self.loading_data()
        if load_success:
            self.list_ui['load pushButton'][data_type].setStyleSheet("")
            self.list_ui['preview pushButton'][data_type].setStyleSheet(self.parent.interact_me_style)
            self.list_ui['preview pushButton'][data_type].setEnabled(True)
            if self.data_type == DataType.sample:
                self.parent.ui.region_of_interest_groupBox.setEnabled(True)
                self.parent.ui.select_roi_pushButton.setStyleSheet(self.parent.interact_me_style)
            self.activate_next_data_type()
            show_status_message(parent=self.parent,
                                message="{} LOADED!".format(self.data_type),
                                status=StatusMessageStatus.ready,
                                duration_s=10)
            logging.info(f"{self.data_type} data have been loaded!")

            self.update_preview_window()
            self.list_ui['load pushButton'][data_type].setEnabled(False)

        else:
            show_status_message(parent=self.parent,
                                message="Loading of {} FAILED!".format(self.data_type),
                                status=StatusMessageStatus.error,
                                duration_s=10)
            logging.error(f"loading of {self.data_type} data FAILED!")

        self.update_list_of_selected_files(load_success=load_success)

        if data_type == DataType.sample:
            o_pre_processing = FilterTabHandler(parent=self.parent)
            o_pre_processing.data_run_to_use_radioButton_clicked()

    def update_preview_window(self):
        if self.parent.preview_id:
            self.parent.preview_id.change_data_type(new_data_type=self.data_type)
            self.parent.preview_id.update_radiobuttons_state()



    def get_list_of_files_to_load(self):
        """
        return the list of files we really need to load
        """
        data_type = self.data_type
        from_file = str(self.list_ui['first file comboBox'][data_type].currentText())
        to_file = str(self.list_ui['last file comboBox'][data_type].currentText())

        from_file_index = self.parent.list_files[data_type].index(from_file)
        to_file_index = self.parent.list_files[data_type].index(to_file)

        list_files = self.parent.list_files[data_type]

        return list_files[from_file_index: to_file_index + 1]


    def check_widgets_state(self):
        """
        according to the info selected, will enabled or not the load button for example and display a status
        message
        """
        data_type = self.data_type

        def _load_push_button_widget_status(parent=None,
                                            button_enabled=True,
                                            button_style=None,
                                            message="",
                                            message_style=None):
            """
            this method takes care of the style sheet of the load button and status message
            """
            self.list_ui['load pushButton'][data_type].setEnabled(button_enabled)
            self.list_ui['load pushButton'][data_type].setStyleSheet(button_style)
            show_status_message(parent=parent, message=message, status=message_style)

        from_file = str(self.list_ui['first file comboBox'][data_type].currentText())
        to_file = str(self.list_ui['last file comboBox'][data_type].currentText())

        if from_file == "":
            _load_push_button_widget_status(parent=self.parent,
                                            button_enabled=False,
                                            button_style="",
                                            message="No {} files found!".format(
                                                    self.data_type),
                                            message_style=StatusMessageStatus.error)
            logging.error(f"No {self.data_type} files found!")
            return

        if from_file == to_file:
            _load_push_button_widget_status(parent=self.parent,
                                            button_enabled=False,
                                            button_style="",
                                            message="{} 'from file' and 'to file' can not be identical!".format(
                                                    data_type),
                                            message_style=StatusMessageStatus.error)
        else:

            from_file_index = self.parent.list_files[data_type].index(from_file)
            to_file_index = self.parent.list_files[data_type].index(to_file)

            if from_file_index > to_file_index:
                _load_push_button_widget_status(parent=self.parent,
                                                button_enabled=False,
                                                button_style="",
                                                message="{} 'from file' must be before 'to file'".format(
                                                        self.data_type),
                                                message_style=StatusMessageStatus.error)
            else:
                _load_push_button_widget_status(parent=self.parent,
                                                button_enabled=True,
                                                button_style=self.parent.interact_me_style,
                                                message="",
                                                message_style=StatusMessageStatus.ready)

    def update_list_of_selected_files(self, load_success=True):
        """use the from and to index to keep only the files between (including the first and last file selected
        in the range)"""
        data_type = self.data_type
        if load_success:
            from_index = self.list_ui['first file comboBox'][data_type].currentIndex()
            to_index = self.list_ui['last file comboBox'][data_type].currentIndex()

            if from_index >= to_index:
                working_list = []
            else:
                full_list = self.parent.list_files[data_type]
                working_list = full_list[from_index: to_index+1]

        else:
            working_list = []

        self.parent.working_list_files[data_type] = working_list
        self.parent.ui.pre_processing_sample_run_comboBox.addItems(working_list)
