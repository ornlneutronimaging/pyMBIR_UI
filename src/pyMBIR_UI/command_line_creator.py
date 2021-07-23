from . import ReconstructionAlgorithm, DataType


class CommandLineCreator:

    command_line = None
    algorithm_selected = None

    def __init__(self, parent=None, algorithm_selected=ReconstructionAlgorithm.pymbir):
        self.parent = parent
        self.algorithm_selected = algorithm_selected

    def build_command_line(self):
        if self.algorithm_selected == ReconstructionAlgorithm.pymbir:
            o_command_line = PyMBIRCommandLineCreator(parent=self.parent)
            o_command_line.build_command_line()
            self.command_line = o_command_line.get_command_line()
        else:
            raise NotImplementedError("Can no build command line, algorithm not implemented yet!")

    def get_command_line(self):
        return self.command_line


class PyMBIRCommandLineCreator:

    parent = None
    command_line = None

    def __init__(self, parent=None):
        self.parent = parent

    def build_command_line(self):
        self.command_line = "recon_HFIR_script.py"

        session_dict = self.parent.session_dict

        # adding arguments
        arguments = {}

        # full path to CT data (stack of tiffs)
        data_path = session_dict[DataType.projections]['folder']
        arguments['--data_path'] = data_path

        # full path to open beam data (stack of tiffs)
        open_beam_path = session_dict[DataType.ob]['folder']
        arguments['--brt_path'] = open_beam_path

        # full path to dark current data (stack of tiffs)
        dark_current_path = session_dict[DataType.df]['folder']
        arguments['--drk_path'] = dark_current_path

        # starting detector pixel along z-direction
        z_start = session_dict['crop']['from slice']
        arguments['--z_start'] = z_start

        # number of detector pixels to use along z-direction
        z_numSlice = session_dict['crop']['to slice - from slice']
        arguments['--z_numSlice'] = z_numSlice

        # total number of detector pixels along col dimension
        tot_col = session_dict['general parameters']['image width']
        arguments['--tot_col'] = tot_col

        # number of detector pixels to use along col dimension cropped from center of detector
        num_col = session_dict['crop']['width']
        arguments['--num_col'] = num_col

        # projections domain sub-sampling factor for sparse view CT
        # ??

        # center of rotation of the object in units of detector pixels
        #rot_center = session_dict



    def get_command_line(self):
        return self.command_line
