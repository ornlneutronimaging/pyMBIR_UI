import logging

from . import ReconstructionAlgorithm
from .session_handler import SessionHandler
from .general_settings_handler import GeneralSettingsHandler
from .command_line_creator import CommandLineCreator


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

        session_dict = self.parent.session_dict
        logging.info(f"-> About to run the command line: {command_line}")
