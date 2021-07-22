from . import ReconstructionAlgorithm


class CommandLineCreator:

    command_line = None
    algorithm_selected = None

    def __init__(self, parent=None, algorithm_selected=ReconstructionAlgorithm.pymbir):
        self.parent = parent

    def build_command_line(self):
        if self.algorithm_selected == ReconstructionAlgorithm.pymbir:
            o_command_line = PyMBIRCommandLineCreator(parent=self.parent)
            o_command_line.build_command_line()
            self.command_line = o_command_line.get_command_line()
        else:
            raise NotImplementedError("Algorithm not implemented yet!")

    def get_command_line(self):
        return self.command_line


class PyMBIRCommandLineCreator:

    parent = None
    command_line = None

    def __init__(self, parent=None):
        self.parent = parent

    def build_command_line(self):
        self.command_line = "test"

    def get_command_line(self):
        return self.command_line
