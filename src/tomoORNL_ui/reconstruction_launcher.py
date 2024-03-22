import numpy as np
import os
import glob
import logging
from pathlib import Path
from qtpy.QtCore import QObject, QThread, Signal
from abc import abstractmethod
import inflect
import subprocess
import json
import dxchange
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt

from tomoORNL_ui import DataType, ReconstructionAlgorithm
from tomoORNL_ui.session_handler import SessionHandler
from tomoORNL_ui.general_settings_handler import GeneralSettingsHandler
from tomoORNL_ui.algorithm_dictionary_creator import AlgorithmDictionaryCreator
from tomoORNL_ui.fake_reconstruction_script import main as fake_reconstruction_script
# from tomoORNL_ui.venkat_function import TestWorker as Worker
from tomoORNL_ui.venkat_function import VenkatWorker as Worker
from tomoORNL_ui.status_message_config import show_status_message, StatusMessageStatus
from tomoORNL_ui.event_handler import EventHandler
from NeuNorm.normalization import Normalization
from tomoORNL_ui.utilities.file_utilities import make_or_reset_folder, make_folder
from tomoORNL_ui.venkat_function import MBIR_fromGUI
# from .recon_HFIR_script_batch import recon_HFIR_script_launcher
from tomoORNL_ui.reconstructed_output_handler import ReconstructedOutputHandler


class ReconstructionLauncher:

    reconstruction_algorithm_selected = ReconstructionAlgorithm.pymbir

    def __init__(self, parent=None):
        self.parent = parent

    def initialization(self):
        self.init_widgets()
        self.set_reconstruction_algorithm()
        self.save_session_dict()

    def init_widgets(self):
        self.parent.ui.tabWidget_3.setTabEnabled(1, False)
        self.parent.ui.tabWidget_3.setCurrentIndex(0)

        self.parent.ui.tabWidget_2.setTabEnabled(1, False)
        self.parent.ui.tabWidget_2.setCurrentIndex(0)

    def reset_widgets(self):
        o_event = EventHandler(parent=self.parent)
        o_event.reset_output_plot()

    def set_reconstruction_algorithm(self):
        o_advanced = GeneralSettingsHandler(parent=self.parent)
        self.reconstruction_algorithm_selected = o_advanced.get_reconstruction_algorithm_selected()

    def save_session_dict(self):
        o_session = SessionHandler(parent=self.parent)
        o_session.save_from_ui()

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass


class ReconstructionLiveLauncher(ReconstructionLauncher):

    def run(self):

        self.reset_widgets()

        logging.info("Running reconstruction")
        logging.info(f"-> algorithm selected: {self.reconstruction_algorithm_selected}")

        o_dictionary = AlgorithmDictionaryCreator(parent=self.parent,
                                                  algorithm_selected=self.reconstruction_algorithm_selected)
        o_dictionary.build_dictionary()
        dictionary_of_arguments = o_dictionary.get_dictionary()
        dictionary_of_arguments['running_mode'] = 'live'
        logging.info(f"-> Dictionary of arguments: {dictionary_of_arguments}")

        # os.system(command_line)
        current_path = Path(__file__).parent
        script_name = str(Path(current_path) / 'fake_reconstruction_script.py')

        # fake_reconstruction_script(ui_id=self.parent,
        #                            progress_bar_id=self.parent.eventProgress)

        self.parent.thread = QThread()
        self.parent.worker = Worker()
        self.parent.worker.init(dictionary_of_arguments=dictionary_of_arguments, stop_thread=self.parent.stop_thread)
        self.parent.worker.moveToThread(self.parent.thread)
        self.parent.thread.started.connect(self.parent.worker.run)
        self.parent.worker.finished.connect(self.parent.thread.quit)
        self.parent.worker.finished.connect(self.parent.worker.deleteLater)
        self.parent.thread.finished.connect(self.parent.thread.deleteLater)
        self.parent.worker.progress.connect(self.parent.reportProgress)
        self.parent.worker.sent_reconstructed_array.connect(self.parent.display_reconstructed_array)
        self.parent.thread.setTerminationEnabled(True)

        self.parent.thread.start()
        self.parent.ui.reconstruction_run_pushButton.setEnabled(False)
        self.parent.ui.reconstruction_stop_pushButton.setEnabled(True)

        self.parent.thread.finished.connect(lambda: self.parent.ui.reconstruction_run_pushButton.setEnabled(True))
        self.parent.thread.finished.connect(lambda: self.parent.ui.reconstruction_stop_pushButton.setEnabled(False))
        self.parent.thread.finished.connect(lambda: show_status_message(parent=self.parent,
                                                                        message=f"Reconstruction ... DONE!",
                                                                        status=StatusMessageStatus.ready,
                                                                        duration_s=5))

    def stop(self):
        self.parent.stop_thread.emit(True)


class ReconstructionBatchLauncher(ReconstructionLauncher):

    batch_process_id = None
    tmp_output_folder = None  # where the images will be saved
    dictionary_of_arguments = {}

    def initialization(self):
        ReconstructionLauncher.initialization(self)
        self.parent.list_file_found_in_output_folder = None

    @staticmethod
    def _fix_n_vox(dictionary_of_arguments):
        dictionary_of_arguments["n_vox_x"] = dictionary_of_arguments["n_vox_x"] - 1
        dictionary_of_arguments["n_vox_y"] = dictionary_of_arguments["n_vox_y"] - 1
        dictionary_of_arguments["n_vox_z"] = dictionary_of_arguments["n_vox_z"] - 1

    def run(self):
        logging.info("Running reconstruction in Batch mode")
        logging.info(f"-> algorithm selected: {self.reconstruction_algorithm_selected}")

        o_dictionary = AlgorithmDictionaryCreator(parent=self.parent,
                                                  algorithm_selected=self.reconstruction_algorithm_selected)
        o_dictionary.build_dictionary()
        dictionary_of_arguments = o_dictionary.get_dictionary()
        dictionary_of_arguments['running_mode'] = 'batch'

        full_output_folder = os.path.join(dictionary_of_arguments['op_path'])

        logging.info(f"Final image will be output in {full_output_folder}")
        make_folder(dictionary_of_arguments['op_path'])
        logging.info(f"Making sure output folder ({full_output_folder}) exists!")

        self.tmp_output_folder = os.path.join(dictionary_of_arguments['op_path'], "temporary_pymbir_reconstructed")
        self.output_folder = dictionary_of_arguments['op_path']
        dictionary_of_arguments['temp_op_dir'] = self.tmp_output_folder
        logging.info(f"-> reset temporary folder: {dictionary_of_arguments['temp_op_dir']}")
        make_or_reset_folder(dictionary_of_arguments['temp_op_dir'])

        # fix n_vox_x, n_vox_y and n_vox_z to follow pymbir convention
        # n_vox_x, y and z have a start index of 1 in the UI, 0 in the algorithm
        ReconstructionBatchLauncher._fix_n_vox(dictionary_of_arguments)

        logging.info(f"-> Dictionary of arguments: {dictionary_of_arguments}")

        self.parent.ui.reconstruction_launch_pushButton.setEnabled(False)
        self.parent.ui.reconstruction_display_latest_output_file_pushButton.setEnabled(True)
        self.parent.ui.reconstruction_batch_stop_pushButton.setEnabled(True)

        self.dictionary_of_arguments = dictionary_of_arguments

        home_folder = os.path.expanduser("~")
        json_file_name = os.path.join(home_folder, "config_batch_mode.json")
        logging.info(f"-> Saving config file to be called from command line script into {json_file_name}")
        with open(json_file_name, 'w') as json_file:
            json.dump(dictionary_of_arguments, json_file)

        current_location = os.path.abspath(os.path.dirname(__file__))
        script = 'recon_HFIR_script_batch.py'
        script_exe = os.path.abspath(os.path.join(current_location, script))
        print(f"{script_exe =}")
        print(f"{json_file_name =}")
        proc = subprocess.Popen(['python',
                                 script_exe,
                                 '--input_json',
                                 json_file_name],
                                shell=False)
        self.batch_process_id = proc

    def kill(self):
        logging.info("Batch process has been stopped by user!")
        self.batch_process_id.terminate()
        self.parent.ui.reconstruction_batch_stop_pushButton.setEnabled(False)
        self.parent.ui.reconstruction_display_latest_output_file_pushButton.setEnabled(False)
        self.parent.ui.reconstruction_launch_pushButton.setEnabled(True)

    def check_output_file(self):
        # retrieve the latest output file from the folder
        # output_folder = self.tmp_output_folder
        output_folder = self.output_folder
        list_files = glob.glob(os.path.join(output_folder, '*.tiff'))
        list_files.sort()

        if not list_files:

            # no files found in the output folder
            show_status_message(parent=self.parent,
                                message=f"No files found in the output folder yet!",
                                status=StatusMessageStatus.warning,
                                duration_s=5)
            return

        if not (self.parent.list_file_found_in_output_folder is None):
            # we already found at least one file in the output folder

            if len(list_files) == len(self.parent.list_file_found_in_output_folder):

                # no new files found in the output folder
                show_status_message(parent=self.parent,
                                    message=f"No new files found in the output folder!",
                                    status=StatusMessageStatus.warning,
                                    duration_s=5)
                return

        if self.parent.list_file_found_in_output_folder is None:
            
            self.parent.full_reconstructed_array = []
            self.parent.list_file_found_in_output_folder = []

            # load all files in the folder
            for _file in list_files:
                o_norm = Normalization()
                try:
                    o_norm.load(file=_file, notebook=False)
                except OSError:
                    show_status_message(parent=self.parent,
                                        message=f"No new files found in the output folder!",
                                        status=StatusMessageStatus.warning,
                                        duration_s=5)
                    return

                reconstructed_array = o_norm.data['sample']['data'][0]
                self.parent.full_reconstructed_array.append(reconstructed_array)
                self.parent.list_file_found_in_output_folder.append(_file)

                nbr_files = len(list_files)
                p = inflect.engine()
                show_status_message(parent=self.parent,
                                    message=f"{nbr_files} new {p.plural('file', nbr_files)} found in the "
                                            f"output "
                                            f"folder!",
                                    status=StatusMessageStatus.ready,
                                    duration_s=5)

        else:

            new_file_found = 0
            for _file in list_files:
                if not (_file in self.parent.list_file_found_in_output_folder):
                    try:
                        o_norm = Normalization()
                        o_norm.load(file=_file, notebook=False)
                    except OSError:
                        show_status_message(parent=self.parent,
                                            message=f"No new files found in the output folder!",
                                            status=StatusMessageStatus.warning,
                                            duration_s=5)
                        return

                    reconstructed_array = o_norm.data['sample']['data'][0]

                    if self.parent.full_reconstructed_array is None:
                        self.parent.full_reconstructed_array = [reconstructed_array]
                    else:
                        self.parent.full_reconstructed_array.append(reconstructed_array)

                    self.parent.list_file_found_in_output_folder.append(_file)
                    new_file_found += 1

            if new_file_found > 0:

                p = inflect.engine()
                show_status_message(parent=self.parent,
                                    message=f"{new_file_found} new {p.plural('file', new_file_found)} found in the "
                                            f"output "
                                            f"folder!",
                                    status=StatusMessageStatus.ready,
                                    duration_s=5)

            else:

                show_status_message(parent=self.parent,
                                    message=f"No new files found in the output folder!",
                                    status=StatusMessageStatus.warning,
                                    duration_s=5)
                return

        self.parent.ui.tabWidget_2.setTabEnabled(1, True)
        self.parent.ui.tabWidget_2.setCurrentIndex(1)
        self.parent.ui.tabWidget_3.setCurrentIndex(0)

        o_event = EventHandler(parent=self.parent)
        o_event.update_output_plot()

    def check_output_3d_volume(self):
        output_folder = self.dictionary_of_arguments['op_path']
        list_tiff_files_in_output_folder = glob.glob(os.path.join(output_folder, "*.tif?"))
        number_of_files_in_output_folder = len(list_tiff_files_in_output_folder)
        if number_of_files_in_output_folder == 0:
            self.parent.ui.tabWidget_3.setTabEnabled(1, False)
            return

        if (number_of_files_in_output_folder > 0) and \
                (number_of_files_in_output_folder < self.dictionary_of_arguments['n_vox_z']):
            self.parent.ui.tabWidget_3.setTabEnabled(1, True)

            show_status_message(parent=self.parent,
                                message=f"Reconstructed volume is about to be available ... check back in a few "
                                        f"seconds",
                                status=StatusMessageStatus.warning)
            return

        else:

            o_reconstruction = ReconstructedOutputHandler(parent=self.parent)
            o_reconstruction.load_reconstructed_slices(list_tiff_files=list_tiff_files_in_output_folder)

            if not o_reconstruction.loading_worked:
                self.parent.eventProgress.setVisible(False)

                logging.info("Error while loading the stack")
                show_status_message(parent=self.parent,
                                    message=f"Give it another try in a few seconds ...",
                                    status=StatusMessageStatus.warning)

            else:

                o_reconstruction.initialize_widgets()
                self.parent.eventProgress.setVisible(False)

                self.parent.ui.tabWidget_3.setTabEnabled(1, True)
                self.parent.ui.tabWidget_3.setCurrentIndex(1)

                self.parent.ui.reconstruction_batch_stop_pushButton.setEnabled(False)
                self.parent.ui.reconstruction_display_latest_output_file_pushButton.setEnabled(False)
                self.parent.ui.reconstruction_launch_pushButton.setEnabled(True)

                show_status_message(parent=self.parent,
                                    message=f"Loading reconstructed volume ... Done !",
                                    status=StatusMessageStatus.ready,
                                    duration_s=10)

    def stop(self):
        pass
