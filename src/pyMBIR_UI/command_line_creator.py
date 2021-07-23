from . import ReconstructionAlgorithm, DataType
from pyMBIR_UI.center_of_rotation.center_of_rotation import CenterOfRotation


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
        sub_sampling_factor = session_dict['general parameters']['sub sampling factor']
        arguments['--view_subsamp'] = sub_sampling_factor

        # center of rotation of the object in units of detector pixels
        center_of_rotation_value = session_dict['center rotation']['center of rotation value']
        arguments['--rot_center'] = center_of_rotation_value

        # use tilt
        tilt_state = session_dict['tilt']['state']
        arguments['--use_det_tilt'] = tilt_state

        # tilt value
        tilt_value = session_dict['tilt']['tilt value to use in reconstruction']
        arguments['--det_tilt'] = tilt_value

        # number of wavelet levels for tomopy based stripe suppression filter routines
        wavelet_level = session_dict['advanced settings']['wavelet level']
        arguments['--wav_level'] = wavelet_level

        # 2D median filter window size to remove outliers
        # ??

        # maximum number of cores to use
        max_core = session_dict['advanced settings']['number of cores']
        arguments['--max_core'] = max_core

        # Number of GPUs to use
        number_of_gpu = session_dict['advanced settings']['number of gpus']
        arguments['--num_gpu'] = number_of_gpu

        # Maximum number of iterations
        max_number_of_iterations = session_dict['advanced settings']["max number of iterations"]
        arguments['--max_iter'] = max_number_of_iterations

        # MRF p parameter
        mrf_p = session_dict['general parameters']['diffuseness'] + 1
        arguments['--mrf_p'] = mrf_p

        # MRF sigma parameter
        mrf_sigma = session_dict['general parameters']['sigma / smoothness']
        arguments['--mrf_sigma'] = mrf_sigma

        # Relative change stopping criteria in percentage
        stop_thresh = session_dict['advanced settings']['stop threshold']
        arguments['--stop_thresh'] = stop_thresh

        # det pix size along x




    def get_command_line(self):
        return self.command_line
