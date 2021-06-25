from qtpy.QtWidgets import QMainWindow, QApplication
import sys
import os
import logging
from . import load_ui
import versioneer
import numpy as np
import multiprocessing
import warnings


# from .select_instrument_launcher import SelectInstrumentLauncher
from .import_data_handler import ImportDataHandler
from .gui_initialization import GuiInitialization
# from .parameters_tab_handler import ParametersTabHandler
# from .event_handler import EventHandler
from .session_handler import SessionHandler
# from .help_handler import HelpHandler
from .preview import PreviewHandler, PreviewLauncher
# from .filter_tab_handler import FilterTabHandler
from .load_previous_session_launcher import LoadPreviousSessionLauncher
from .utilities.decorators import check_ui
from .utilities.get import Get
# from .roi_handler import RoiHandler
from .log_launcher import LogLauncher
# from .fitting import Fitting
# from .utility_backend import multi_logger as ml
from . import DataType
from .crop_handler import CropHandler

# warnings.filterwarnings('ignore')


class PyMBIRUILauncher(QMainWindow):
    automatic_config_file_name = None

    config = None  # dictionary created out of config.json
    homepath = "./"

    # all infos from the UI  used to save the entire session
    session_dict = {}
    # {DataType.projections: {'folder': 'name_of_folder',
    #                         'list_files': [file1, file2, file3],
    #                        },
    #  DataType.ob: {},
    #  DataType.df: {},
    #  DataType.output: "name_of_output_folder",
    #
    #  }

    # QDialog/QMainWindow ids
    preview_id = None
    log_id = None

    # pyqtgrpah
    crop_image_view = None

    # infinite line and their labels
    crop_from_slice_item = None
    crop_from_slice_label_item = None
    crop_to_slice_item = None
    crop_to_slice_label_item = None

    crop_image_height = np.NaN
    crop_image_width = np.NaN

    # histogram of preview dialog
    preview_histogram = None

    def __init__(self, parent=None):
        super(PyMBIRUILauncher, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
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

    def menu_log_clicked(self):
        LogLauncher(parent=self)

    # Input tab
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
    def crop_checkBox_clicked(self):
        o_crop = CropHandler(parent=self)
        o_crop.master_checkbox_clicked()

    def crop_file_index_moved(self, value):
        o_crop = CropHandler(parent=self)
        o_crop.file_index_changed()

    def crop_file_index_pressed(self):
        pass

    def crop_width_moved(self, value):
        pass

    def crop_width_pressed(self):
        pass

    def crop_from_slice_changed(self):
        o_crop = CropHandler(parent=self)
        o_crop.crop_slice_moved()

    def crop_to_slice_changed(self):
        o_crop = CropHandler(parent=self)
        o_crop.crop_slice_moved()

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
