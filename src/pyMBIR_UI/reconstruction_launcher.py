import logging
import os
from pathlib import Path
from qtpy.QtCore import QObject, QThread, Signal

from . import ReconstructionAlgorithm
from .session_handler import SessionHandler
from .general_settings_handler import GeneralSettingsHandler
from .command_line_creator import CommandLineCreator
from .fake_reconstruction_script import main as fake_reconstruction_script
from pyMBIR_UI.venkat_function import Worker
from .status_message_config import show_status_message, StatusMessageStatus


class ReconstructionLauncher:

    reconstruction_algorithm_selected = ReconstructionAlgorithm.pymbir

    def __init__(self, parent=None):
        self.parent = parent
        self.set_reconstruction_algorithm()
        self.save_session_dict()

    def set_reconstruction_algorithm(self):
        o_advanced = GeneralSettingsHandler(parent=self.parent)
        self.reconstruction_algorithm_selected = o_advanced.get_reconstruction_algorithm_selected()

    def save_session_dict(self):
        o_session = SessionHandler(parent=self.parent)
        o_session.save_from_ui()

    def run(self):
        logging.info("Running reconstruction")
        logging.info(f"-> algorithm selected: {self.reconstruction_algorithm_selected}")

        o_command_line = CommandLineCreator(parent=self.parent,
                                            algorithm_selected=self.reconstruction_algorithm_selected)
        o_command_line.build_command_line()
        command_line = o_command_line.get_command_line()
        logging.info(f"-> About to run the command line: {command_line}")

        # os.system(command_line)
        current_path = Path(__file__).parent
        script_name = str(Path(current_path) / 'fake_reconstruction_script.py')

        # fake_reconstruction_script(ui_id=self.parent,
        #                            progress_bar_id=self.parent.eventProgress)

        self.parent.thread = QThread()
        self.parent.worker = Worker()
        self.parent.worker.moveToThread(self.parent.thread)
        self.parent.thread.started.connect(self.parent.worker.run)
        self.parent.worker.finished.connect(self.parent.thread.quit)
        self.parent.worker.finished.connect(self.parent.worker.deleteLater)
        self.parent.thread.finished.connect(self.parent.thread.deleteLater)
        self.parent.worker.progress.connect(self.parent.reportProgress)
        self.parent.worker.sent_reconstructed_array.connect(self.parent.display_reconstructed_array)

        self.parent.thread.start()
        self.parent.ui.reconstruction_run_pushButton.setEnabled(False)

        self.parent.thread.finished.connect(lambda: self.parent.ui.reconstruction_run_pushButton.setEnabled(True))
        self.parent.thread.finished.connect(lambda: show_status_message(parent=self.parent,
                                                                 message=f"Reconstruction ... DONE!",
                                                                 status=StatusMessageStatus.ready,
                                                                 duration_s=5))