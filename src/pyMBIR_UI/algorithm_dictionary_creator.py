import os
import json

from . import ReconstructionAlgorithm, DataType
from pyMBIR_UI.center_of_rotation.center_of_rotation import CenterOfRotation
from pyMBIR_UI.advanced_settings.advanced_settings_initialization import AdvancedSettingsInitialization
from .utilities.get import Get


class AlgorithmDictionaryCreator:

    dictionary = None
    algorithm_selected = None

    def __init__(self, parent=None, algorithm_selected=ReconstructionAlgorithm.pymbir):
        self.parent = parent
        self.algorithm_selected = algorithm_selected

    def build_dictionary(self):
        if self.algorithm_selected == ReconstructionAlgorithm.pymbir:
            o_dictionary = PyMBIRDictionaryCreator(parent=self.parent)
            o_dictionary.build_dictionary()
            self.dictionary = o_dictionary.get_dictionary()
        else:
            raise NotImplementedError("Can no create dictionary, algorithm not implemented yet!")

    def get_dictionary(self):
        return self.dictionary


class PyMBIRDictionaryCreator:

    parent = None
    dictionary = None

    def __init__(self, parent=None):
        self.parent = parent

    def build_dictionary(self, session_dict=None, config_file_name=None):

        if config_file_name:
            if not os.path.exists(config_file_name):
                raise FileNotFoundError("Config file name does not exist!")

            try:
                with open(config_file_name, "r") as read_file:
                    session_dict = json.load(read_file)
            except json.JSONDecodeError:
                raise json.JSONDecodeError("The config file is not a valid JSON file!")

        elif session_dict is None:
            session_dict = self.parent.session_dict

        # adding arguments
        arguments = {}

        # full path to CT data (stack of tiffs)
        data_path = session_dict[DataType.projections]['folder']
        arguments['data_path'] = data_path

        # full path to open beam data (stack of tiffs)
        open_beam_path = session_dict[DataType.ob]['folder']
        arguments['brt_path'] = open_beam_path

        # full path to dark current data (stack of tiffs)
        dark_current_path = session_dict[DataType.df]['folder']
        arguments['drk_path'] = dark_current_path

        # starting detector pixel along z-direction
        z_start = session_dict['crop']['from slice']
        arguments['z_start'] = z_start

        # number of detector pixels to use along z-direction
        z_numSlice = session_dict['crop']['to slice - from slice']
        arguments['z_numSlice'] = z_numSlice

        # total number of detector pixels along col dimension
        tot_col = session_dict['general parameters']['image width']
        arguments['tot_col'] = tot_col

        # number of detector pixels to use along col dimension cropped from center of detector
        num_col = session_dict['crop']['width']
        arguments['num_col'] = num_col

        # projections domain sub-sampling factor for sparse view CT
        sub_sampling_factor = session_dict['general parameters']['sub sampling factor']
        arguments['view_subsamp'] = sub_sampling_factor

        # center of rotation of the object in units of detector pixels
        center_of_rotation_value = session_dict['center rotation']['center of rotation value']
        arguments['rot_center'] = center_of_rotation_value

        # use tilt
        tilt_state = session_dict['tilt']['state']
        arguments['use_det_tilt'] = tilt_state

        # tilt value
        tilt_value = session_dict['tilt']['tilt value to use in reconstruction']
        arguments['det_tilt'] = tilt_value

        # number of wavelet levels for tomopy based stripe suppression filter routines
        if session_dict.get('advanced settings', None) is None:
            if config_file_name:
                raise ValueError("Config file name is missing the advanced settings required!")

            o_init = AdvancedSettingsInitialization(parent=self.parent)
            o_init.from_config_to_session_dict()

            session_dict = self.parent.session_dict

        wavelet_level = session_dict['advanced settings']['wavelet level']
        arguments['wav_level'] = wavelet_level

        # 2D median filter window size to remove outliers
        median_filter = session_dict['advanced settings']['median filter size']
        arguments['med_filt_win'] = median_filter

        # maximum number of cores to use
        max_core = session_dict['advanced settings']['number of cores']
        arguments['max_core'] = max_core

        # Number of GPUs to use
        number_of_gpu = session_dict['advanced settings']['number of gpus']
        arguments['num_gpu'] = number_of_gpu

        # Maximum number of iterations
        max_number_of_iterations = session_dict['advanced settings']["max number of iterations"]
        arguments['max_iter'] = max_number_of_iterations

        # MRF p parameter
        mrf_p = session_dict['general parameters']['diffuseness'] + 1
        arguments['mrf_p'] = mrf_p

        # MRF sigma parameter
        mrf_sigma = session_dict['general parameters']['sigma / smoothness']
        arguments['mrf_sigma'] = mrf_sigma

        # Relative change stopping criteria in percentage
        stop_thresh = session_dict['advanced settings']['stop threshold']
        arguments['stop_thresh'] = float(stop_thresh)

        # Frequency of iterations to use to write out the files
        emit_freq = session_dict['advanced settings']['exporting file frequency']
        arguments['emit_freq'] = emit_freq

        # det pix size along x and y
        det_x = session_dict['advanced settings']['det_x, det_y']['det_x_to_use']
        det_y = session_dict['advanced settings']['det_x, det_y']['det_y_to_use']
        arguments['det_x'] = det_x
        arguments['det_y'] = det_y

        # Voxel size along plane dim (vox_xy)
        vox_xy = session_dict['advanced settings']['vox_xy, vox_z']['vox_xy_to_use']
        arguments['vox_xy'] = vox_xy

        # voxel size along axial z direction
        vox_z = session_dict['advanced settings']['vox_xy, vox_z']['vox_z_to_use']
        arguments['vox_z'] = vox_z

        # number of voxels along x, y and z dimension in the object to be reconstructed
        n_vox_x = session_dict['advanced settings']['n_vox_x, n_vox_y']['n_vox_x_to_use']
        n_vox_y = session_dict['advanced settings']['n_vox_x, n_vox_y']['n_vox_y_to_use']

        n_vox_z = session_dict['advanced settings']['n_vox_z']['n_vox_z_to_use']
        arguments['n_vox_x'] = n_vox_x
        arguments['n_vox_y'] = n_vox_y
        arguments['n_vox_z'] = n_vox_z

        # Write output
        write_output_flag = session_dict['advanced settings']['write output']
        arguments['write_op'] = write_output_flag

        # output folder
        output_folder = session_dict[DataType.output]['folder']
        arguments['op_path'] = output_folder

        # temp output folder
        temp_output_folder = self.parent.config['temp_local_output_folder']
        full_home_file_name = Get.full_home_file_name(temp_output_folder)
        arguments['temp_op_dir'] = full_home_file_name

        arguments['running_mode'] = ''  # ['live', 'batch']

        self.dictionary = arguments

    def get_dictionary(self):
        return self.dictionary
