from qtpy.QtWidgets import QMainWindow, QApplication
import sys
import os
import logging
from . import load_ui
import versioneer
import multiprocessing
import warnings


# from .select_instrument_launcher import SelectInstrumentLauncher
from .import_data_handler import ImportDataHandler
from .gui_initialization import GuiInitialization
# from .parameters_tab_handler import ParametersTabHandler
# from .event_handler import EventHandler
# from .session_handler import SessionHandler
# from .help_handler import HelpHandler
from .preview import PreviewHandler, PreviewLauncher
# from .filter_tab_handler import FilterTabHandler
# from .load_previous_session_launcher import LoadPreviousSessionLauncher
from .utilities.decorators import check_ui
from .utilities.get import Get
# from .roi_handler import RoiHandler
from .log_launcher import LogLauncher
# from .fitting import Fitting
# from .utility_backend import multi_logger as ml
from . import DataType

# warnings.filterwarnings('ignore')


class PyMBIRUILauncher(QMainWindow):
    # automatic_config_file_name = None
    #
    # selected_instrument = None  # list of instrument can be found in config.json
    config = None  # dictionary created out of config.json
    homepath = "./"

    # interact_me_style = "background-color: lime"
    #
    # list_files = {DataType.sample: None,
    #               DataType.ob    : None,
    #               DataType.di    : None}
    #
    # working_list_files = {DataType.sample: None,
    #                       DataType.ob    : None,
    #                       DataType.di    : None}
    #
    # parameters_lock_activated = True
    #
    # # dataio.experiment object that will contain the sample, ob and di data
    # o_experiment = None
    #
    # # {ui: [True, False, True]}
    # tab_to_enabled = None
    #
    # # {'Path of sample images': {'row': 0, 'ui': None},
    # #  'Fit procedure': {'row': 10, 'ui': widgets.comboBox()},
    # #  ...
    # # }
    # parameters_list_ui = {}
    # tab_index_was = 0
    # # main_tab_index = {'previous': 1,
    # #                   'expected': 1
    # #                   }
    #
    # # all infos from the UI  used to save the entire session, populates the parameters table
    # session_dict = {}

    # QDialog/QMainWindow ids
    preview_id = None
    # gamma_help_id = None
    log_id = None
    # algo_help_id = None

    # histogram of preview dialog
    preview_histogram = None
    #
    # # roi
    # sample_roi_list = None  # used to be called roi_list in old ui [y0, y1, x0, x1]
    # norm_roi_list = None
    #
    # log = []
    #
    # # test of filters
    # test_filters_list = {'name': [],
    #                      'image': [],
    #                      'image_filtered': [],
    #                      'parameters': [],
    #                     }
    #
    # ngi_thread = None
    #
    # queue = multiprocessing.Queue(-1)
    # listener = multiprocessing.Process(target=ml.listener_process,
    #                                    args=(queue, ml.listener_configurer))

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

        # self.list_ui = {'folder lineEdit'    : {DataType.sample: self.ui.sample_data_folder_lineEdit,
        #                                         DataType.ob    : self.ui.open_beam_folder_lineEdit,
        #                                         DataType.di    : self.ui.dark_image_folder_lineEdit,
        #                                         },
        #                 'first file comboBox': {DataType.sample: self.ui.sample_data_first_file_comboBox,
        #                                         DataType.ob    : self.ui.open_beam_first_file_comboBox,
        #                                         DataType.di    : self.ui.dark_image_first_file_comboBox,
        #                                         },
        #                 'last file comboBox' : {DataType.sample: self.ui.sample_data_last_file_comboBox,
        #                                         DataType.ob    : self.ui.open_beam_last_file_comboBox,
        #                                         DataType.di    : self.ui.dark_image_last_file_comboBox,
        #                                         },
        #                 'load pushButton'    : {DataType.sample: self.ui.sample_data_load_pushButton,
        #                                         DataType.ob    : self.ui.open_beam_load_pushButton,
        #                                         DataType.di    : self.ui.dark_image_load_pushButton,
        #                                         },
        #                 'preview pushButton' : {DataType.sample: self.ui.sample_data_preview_pushButton,
        #                                         DataType.ob    : self.ui.open_beam_preview_pushButton,
        #                                         DataType.di    : self.ui.dark_image_preview_pushButton,
        #                                         },
        #                 'folder browse'      : {DataType.sample: self.ui.sample_data_browse_pushButton,
        #                                         DataType.ob    : self.ui.open_beam_browse_pushButton,
        #                                         DataType.di    : self.ui.dark_image_browse_pushButton},
        #                 'filters'            : {'gamma': {DataType.sample: {'threshold1'   :
        #                                                                         self.ui.sample_ob_threshold1_spinBox,
        #                                                                     'threshold2'   :
        #                                                                         self.ui.sample_ob_threshold2_spinBox,
        #                                                                     'threshold3'   :
        #                                                                         self.ui.sample_ob_threshold3_spinBox,
        #                                                                     'sigma for log':
        #                                                                         self.ui.sample_ob_sigma_for_log_spinBox},
        #                                                   DataType.ob    : {},
        #                                                   DataType.di    : {'threshold1'   : self.ui.di_threshold1_spinBox,
        #                                                                     'threshold2'   : self.ui.di_threshold2_spinBox,
        #                                                                     'threshold3'   : self.ui.di_threshold3_spinBox,
        #                                                                     'sigma for log': self.ui.di_sigma_for_log_spinBox},
        #                                                   },
        #                                         },
        #                 }
        # self.list_ui['filters']['gamma'][DataType.ob] = self.list_ui['filters']['gamma'][DataType.sample]

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

        # self.automatic_load_of_previous_session()

    # menu
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

    # leaving ui
    def closeEvent(self, c):
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
