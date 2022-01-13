from qtpy.QtWidgets import QMainWindow, QApplication
from qtpy.QtGui import QGuiApplication
import sys
import os
import logging
from . import load_ui
import versioneer
import numpy as np
from qtpy.QtCore import QObject, QThread, Signal

from .import_data_handler import ImportDataHandler
from .gui_initialization import GuiInitialization
from .event_handler import EventHandler
from .session_handler import SessionHandler
from .preview import PreviewHandler, PreviewLauncher
from .load_previous_session_launcher import LoadPreviousSessionLauncher
from .utilities.get import Get
from .log_launcher import LogLauncher
from . import DataType, TiltAlgorithm
from pyMBIR_UI.crop.crop_handler import CropHandler
from pyMBIR_UI.tilt.tilt_handler import TiltHandler
from pyMBIR_UI.center_of_rotation.center_of_rotation import CenterOfRotation
from .utilities.decorators import wait_cursor
from pyMBIR_UI.reconstruction_launcher import ReconstructionLiveLauncher, ReconstructionBatchLauncher
from pyMBIR_UI.advanced_settings.advanced_settings_handler import AdvancedSettingsPasswordHandler
from pyMBIR_UI.general_settings_handler import GeneralSettingsHandler
from .status_message_config import show_status_message, StatusMessageStatus

# warnings.filterwarnings('ignore')


class PyMBIRUILauncher(QMainWindow):

    automatic_config_file_name = None
    loading_from_config = False

    config = None  # dictionary created out of config.json
    homepath = "./"

    image_size = {'width': None, 'height': None}

    # all infos from the UI  used to save the entire session
    session_dict = {}
    # {DataType.projections: {'folder': 'name_of_folder',
    #                         'list_files': [file1, file2, file3],
    #                        },
    #  DataType.ob: {},
    #  DataType.df: {},
    #  DataType.output: "name_of_output_folder",
    #  "advanced settings": {},
    #  }

    # QDialog/QMainWindow ids
    preview_id = None
    log_id = None

    # pyqtgrpah
    crop_image_view = None
    center_of_rotation_image_view = None
    tilt_correction_image_view = None

    # infinite line and their labels
    crop_from_slice_item = None
    crop_from_slice_label_item = None
    crop_to_slice_item = None
    crop_to_slice_label_item = None

    # full image width and height
    crop_image_height = np.NaN
    crop_image_width = np.NaN

    crop_top_region_item = None
    crop_bottom_region_item = None
    crop_left_region_item = None
    crop_right_region_item = None

    # center of rotation
    center_of_rotation_item = None

    # tilt correction
    tilt_correction_index_dict = {'0_degree': -1,
                                  '180_degree': -1}
    tilt_calculation = {TiltAlgorithm.phase_correlation: None,
                        TiltAlgorithm.direct_minimization: None,
                        TiltAlgorithm.use_center: None}
    tilt_grid_item = None

    # histogram of preview dialog
    preview_histogram = None

    # reconstructed full array
    full_reconstructed_array = None

    stop_thread = Signal(bool)

    # batch mode - last time a file was added to output folder
    list_file_found_in_output_folder = None

    def __init__(self, parent=None):

        super(PyMBIRUILauncher, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('ui',
                                                 'main_application.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("pyMBIR_UI")

        self.list_ui = {'select button': {DataType.projections: self.ui.select_projections_pushButton,
                                          DataType.ob: self.ui.select_ob_pushButton,
                                          DataType.df: self.ui.select_df_pushButton,
                                          DataType.output: self.ui.select_output_folder_pushButton},
                        'select lineEdit': {DataType.projections: self.ui.projections_lineEdit,
                                            DataType.ob: self.ui.ob_lineEdit,
                                            DataType.df: self.ui.df_lineEdit,
                                            DataType.output: self.ui.output_folder_lineEdit},
                        }

        self.input = {'list files': {DataType.projections: None,
                                     DataType.ob: None,
                                     DataType.df: None,
                                     },
                      'list angles': None,
                      'full list files': {DataType.projections: None,
                                          DataType.ob: None,
                                          DataType.df: None,
                                          },
                      'data': {DataType.projections: None,
                               DataType.ob: None,
                               DataType.df: None},
                      }

        o_get = Get(parent=self)
        o_init = GuiInitialization(parent=self)
        o_init.all()

        # configuration of config
        log_file_name = o_get.get_log_file_name()
        logging.basicConfig(filename=log_file_name,
                            filemode='a',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)
        logging.info("*** Starting a new session ***")
        logging.info(f" Version: {versioneer.get_version()}")

        self.automatic_load_of_previous_session()

    def automatic_load_of_previous_session(self):
        o_get = Get(parent=self)
        full_config_file_name = o_get.get_automatic_config_file_name()
        if os.path.exists(full_config_file_name):
            load_session_ui = LoadPreviousSessionLauncher(parent=self)
            load_session_ui.show()

    # menu
    def load_session_clicked(self):
        o_session = SessionHandler(parent=self)
        o_session.load_from_file()
        o_session.load_to_ui()

    def save_session_clicked(self):
        o_session = SessionHandler(parent=self)
        o_session.save_from_ui()
        o_session.save_to_file()

    def full_reset_clicked(self):
        o_event = EventHandler(parent=self)
        o_event.full_reset_clicked()

    def menu_log_clicked(self):
        LogLauncher(parent=self)

    def advanced_settings_clicked(self):
        o_advanced = AdvancedSettingsPasswordHandler(parent=self)
        o_advanced.show()

    # Input tab
    def main_tab_changed(self, new_tab):
        if new_tab == 2:
            self.sub_sampling_value_changed(-1)

    def projections_select_clicked(self):
        o_import = ImportDataHandler(parent=self,
                                     data_type=DataType.projections)
        o_import.browse_via_filedialog()

    def projections_text_field_returned(self):
        o_import = ImportDataHandler(parent=self,
                                     data_type=DataType.projections)
        o_import.browse_via_manual_input()

    def ob_select_clicked(self):
        o_import = ImportDataHandler(parent=self,
                                     data_type=DataType.ob)
        o_import.browse_via_filedialog()

    def ob_text_field_returned(self):
        o_import = ImportDataHandler(parent=self,
                                     data_type=DataType.ob)
        o_import.browse_via_manual_input()

    def df_select_clicked(self):
        o_import = ImportDataHandler(parent=self,
                                     data_type=DataType.df)
        o_import.browse_via_filedialog()

    def df_text_field_returned(self):
        o_import = ImportDataHandler(parent=self,
                                     data_type=DataType.df)
        o_import.browse_via_manual_input()

    def preview_clicked(self):
        PreviewLauncher(parent=self)

    def output_folder_select_clicked(self):
        o_import = ImportDataHandler(parent=self,
                                     data_type=DataType.output)
        o_import.browse_output_folder_via_filedialog()

    def output_folder_text_field_returned(self):
        o_import = ImportDataHandler(parent=self,
                                     data_type=DataType.output)
        o_import.browse_output_folder_via_manual_input()

    def check_preview_button_status(self):
        o_preview = PreviewHandler(parent=self)
        o_preview.check_status_of_button()

    # Reconstruction setup tab

    # crop
    def crop_checkBox_clicked(self):
        o_crop = CropHandler(parent=self)
        o_crop.master_checkbox_clicked()

    def crop_file_index_moved(self, value):
        o_crop = CropHandler(parent=self)
        o_crop.file_index_changed()

    def crop_file_index_pressed(self):
        o_crop = CropHandler(parent=self)
        o_crop.file_index_changed()

    def crop_width_moved(self, value):
        o_crop = CropHandler(parent=self)
        o_crop.width_changed()

    def crop_width_pressed(self):
        o_crop = CropHandler(parent=self)
        o_crop.width_changed()

    def crop_from_slice_changed(self):
        o_crop = CropHandler(parent=self)
        o_crop.crop_slice_moved(widget='from')

    def crop_from_slice_spinBox_finished_editing(self):
        o_crop = CropHandler(parent=self)
        o_crop.crop_slice_spinBox_changed(widget='from')

    def crop_to_slice_spinBox_finished_editing(self):
        o_crop = CropHandler(parent=self)
        o_crop.crop_slice_spinBox_changed(widget='to')

    def crop_to_slice_changed(self):
        o_crop = CropHandler(parent=self)
        o_crop.crop_slice_moved(widget='to')

    # center of rotation
    def center_of_rotation_checkBox_clicked(self):
        o_center = CenterOfRotation(parent=self)
        o_center.master_checkbox_clicked()

    def center_of_rotation_file_index_changed(self, value):
        o_center = CenterOfRotation(parent=self)
        o_center.display_images()
        o_center.calculate_center_of_rotation()

    @wait_cursor
    def center_of_rotation_algorithm_clicked(self):
        o_center = CenterOfRotation(parent=self)
        o_center.update_widgets()
        o_center.calculate_center_of_rotation()
        o_center.display_center_of_rotation()

    def center_of_rotation_user_value_changed(self, value):
        o_center = CenterOfRotation(parent=self)
        o_center.calculate_center_of_rotation()
        o_center.display_center_of_rotation()

    # tilt correction
    def tilt_correction_checkBox_clicked(self):
        o_tilt = TiltHandler(parent=self)
        o_tilt.master_checkBox_clicked()

    def tilt_correction_file_index_moved(self, value):
        o_tilt = TiltHandler(parent=self)
        o_tilt.file_index_changed()

    def tilt_correction_file_index_pressed(self):
        o_tilt = TiltHandler(parent=self)
        o_tilt.file_index_changed()

    def tilt_correction_algorithm_changed(self):
        o_tilt = TiltHandler(parent=self)
        o_tilt.correction_algorithm_changed()

    def tilt_correction_set_up_images_at_0_and_180_degrees_pushed(self):
        o_tilt = TiltHandler(parent=self)
        o_tilt.set_up_images_at_0_and_180_degrees()

    def tilt_correction_show_tilt_clicked(self):
        o_tilt = TiltHandler(parent=self)
        o_tilt.file_index_changed()

    @wait_cursor
    def tilt_refresh_calculation_clicked(self):
        o_tilt = TiltHandler(parent=self)
        o_tilt.refresh_calculation()

    # general tab
    def sub_sampling_value_changed(self, value):
        o_general = GeneralSettingsHandler(parent=self)
        o_general.sub_sampling_value_changed()

    def run_reconstruction(self):
        o_reconstruction = ReconstructionLiveLauncher(parent=self)
        o_reconstruction.initialization()
        o_reconstruction.run()

    def stop_reconstruction(self):
        o_reconstruction = ReconstructionLiveLauncher(parent=self)
        o_reconstruction.stop()

    def launch_reconstruction(self):
        self.o_reconstruction = ReconstructionBatchLauncher(parent=self)
        self.o_reconstruction.initialization()
        self.o_reconstruction.run()

    def display_latest_output_file_button_clicked(self):
        self.o_reconstruction.check_output_file()
        self.o_reconstruction.check_output_3d_volume()

    def stop_batch_reconstruction_clicked(self):
        self.o_reconstruction.kill()

    def reportProgress(self, iteration, stopping_criteria):
        show_status_message(parent=self,
                            message=f"Iteration {iteration} and stopping criteria: {int(100*stopping_criteria)}",
                            status=StatusMessageStatus.working)
        self.ui.tabWidget_2.setTabEnabled(1, True)
        self.ui.tabwidget_2.setCurrentIndex(1)
        QGuiApplication.processEvents()

    def display_reconstructed_array(self, reconstructed_array):
        if self.full_reconstructed_array is None:
            self.full_reconstructed_array = [reconstructed_array]
        else:
            self.full_reconstructed_array.append(reconstructed_array)

        o_event = EventHandler(parent=self)
        o_event.update_output_plot()

    # output tab
    def update_output_plot(self, data):
        o_event = EventHandler(parent=self)
        o_event.update_output_plot(data)
        QGuiApplication.processEvents()

    def output_slider_changed(self, value):
        self.ui.output_checkBox.setChecked(False)
        o_event = EventHandler(parent=self)
        o_event.display_output_plot(array_index_to_show=value)

    def output_slider_clicked(self):
        self.ui.output_checkBox.setChecked(False)
        value = self.ui.output_horizontalSlider.value()
        o_event = EventHandler(parent=self)
        o_event.display_output_plot(array_index_to_show=value)

    def output_checkbox_clicked(self):
        value = self.ui.output_checkBox.isChecked()
        if value:
            max_slider_value = self.ui.output_horizontalSlider.maximum()
            self.ui.output_horizontalSlider.setValue(max_slider_value)
            self.ui.output_slider_label.setText(str(max_slider_value))

    # leaving ui
    def closeEvent(self, c):
        o_session = SessionHandler(parent=self)
        o_session.save_from_ui()
        o_session.automatic_save()
        logging.info(" #### Leaving pyMBIR_UI ####")

        self.close()


def main(args):
    app = QApplication(args)
    app.setStyle('Fusion')
    app.aboutToQuit.connect(clean_up)
    app.setApplicationDisplayName("pyMBIR_UI")
    window = PyMBIRUILauncher()
    window.show()
    sys.exit(app.exec_())


def clean_up():
    app = QApplication.instance()
    app.closeAllWindows()
