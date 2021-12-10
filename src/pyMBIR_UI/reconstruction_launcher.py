import os
import glob
import logging
from pathlib import Path
from qtpy.QtCore import QObject, QThread, Signal
from abc import abstractmethod

from . import DataType, ReconstructionAlgorithm
from .session_handler import SessionHandler
from .general_settings_handler import GeneralSettingsHandler
from .algorithm_dictionary_creator import AlgorithmDictionaryCreator
from .fake_reconstruction_script import main as fake_reconstruction_script
# from pyMBIR_UI.venkat_function import TestWorker as Worker
from pyMBIR_UI.venkat_function import VenkatWorker as Worker
from .status_message_config import show_status_message, StatusMessageStatus
from .event_handler import EventHandler
from NeuNorm.normalization import Normalization


class ReconstructionLauncher:

    reconstruction_algorithm_selected = ReconstructionAlgorithm.pymbir

    def __init__(self, parent=None):
        self.parent = parent

    def initialization(self):
        self.set_reconstruction_algorithm()
        self.save_session_dict()

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

    def run(self):
        pass

    def check_output_file(self):
        # retrieve the latest output file from the folder
        output_folder = self.parent.session_dict[DataType.output]['folder']
        list_files = glob.glob(os.path.join(output_folder, '*.tiff'))
        list_atime = {_file: os.stat(_file).st_atime for _file in list_files}
        highest_atime = {'time': -1, 'file': None}

        for _file in list_atime.keys():
            _atime = list_atime[_file]
            if _atime > highest_atime['time']:
                highest_atime['time'] = _atime
                highest_atime['file'] = _file

        # if same timestamp as previous one, do nothing and just inform user
        if self.parent.batch_mode_last_added_file_time == highest_atime['time']:
            show_status_message(parent=self.parent,
                                message=f"No new files found in the output folder!",
                                status=StatusMessageStatus.warning,
                                duration_s=10)
            return

        # display it
        show_status_message(parent=self.parent,
                            message=f"New file found: {highest_atime['file']}",
                            status=StatusMessageStatus.ready,
                            duration_s=10)

        # load new file here and add it to the full_reconstructed_array
        o_norm = Normalization()
        o_norm.load(file=highest_atime['file'], notebook=False)
        reconstructed_array = o_norm.data['sample']['data'][0]

        if self.parent.full_reconstructed_array is None:
            self.parent.full_reconstructed_array = [reconstructed_array]
        else:
            self.parent.full_reconstructed_array.append(reconstructed_array)

        o_event = EventHandler(parent=self.parent)
        o_event.update_output_plot()

        self.parent.batch_mode_last_added_file_time = highest_atime['time']

    def stop(self):
        pass
