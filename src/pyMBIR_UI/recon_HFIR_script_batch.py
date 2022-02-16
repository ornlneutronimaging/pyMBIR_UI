# Copyright (C) 2019 by S. V. Venkatakrishnan (venkatakrisv@ornl.gov)
# All rights reserved. BSD 3-clause License.
# This file is part of the pyMBIR package. Details of the copyright
# and user license can be found in the 'LICENSE.txt' file distributed
# with the package.

# -----------------------------------------------------------------------
# Created by S.V. Venkatakrishnan
# Obtain MBIR reconstruction from HFIR CT data
# -----------------------------------------------------------------------

import argparse
from tomopy import remove_stripe_fw
try:
    from dxchange.writer import write_tiff_stack
    from pyMBIR.reconEngine import analytic, MBIR
    from pyMBIR.utils import apply_proj_tilt
    from src.pyMBIR_UI.readNeutronData import *
    import dxchange
except ModuleNotFoundError:
    pass
from tomopy.misc.corr import median_filter
import os
import json

STOP_FILE_NAME = "OVER.txt"


def main():

    # Parameters associated with the acquired data
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_json", help="Full path to the JSON file containig all the inputs")
    args = parser.parse_args()

    with open(args.input_json, "r") as read_file:
         input_dict = json.load(read_file)

    import pprint
    pprint.pprint(input_dict)

    # for testing only
    #import glob
   # list_files = glob.glob("/Volumes/G-DRIVE/IPTS/IPTS-25967-pymbir/output_folder/real_output_folder/*.tiff")

    # #import time
    # import shutil
    # for _file in list_files:
    #     time.sleep(.5)
    #     shutil.copy(_file, input_dict['temp_op_dir'])
    #
    # for _file in list_files:
    #     shutil.copy(_file, input_dict['op_path'])

    max_core = input_dict['max_core']
    num_wav_level = input_dict['wav_level']
    tot_col = input_dict['tot_col']
    num_col = input_dict['num_col']
    rot_center = input_dict['rot_center']

    rec_params = {}
    rec_params['debug'] = False
    rec_params['verbose'] = True
    rec_params['num_iter'] = input_dict['max_iter']
    rec_params['gpu_index'] = range(0, input_dict['num_gpu'])
    rec_params['MRF_P'] = input_dict['mrf_p']
    rec_params['MRF_SIGMA'] = input_dict['mrf_sigma']
    rec_params['stop_thresh'] = input_dict['stop_thresh']

    # Directory to store temporary files
    rec_params['run_mode'] = 'batch'
    rec_params['temp_op_dir'] = input_dict['temp_op_dir']
    rec_params['emit_freq'] = input_dict['emit_freq']

    # Miscalibrations - detector offset, tilt
    miscalib = {}
    miscalib['delta_u'] = (tot_col / 2 - rot_center)
    miscalib['delta_v'] = 0
    miscalib['phi'] = 0

    z_start = input_dict['z_start']
    z_numSlice = input_dict['z_numSlice']
    filt_size = input_dict['med_filt_win']  # window of median filter
    print(os.path.join(input_dict['brt_path'], '*.tiff'))
    brights = readMedianTifDir(os.path.join(input_dict['brt_path'], '*.tiff'), z_start, z_numSlice, filt_size)
    darks = readMedianTifDir(os.path.join(input_dict['drk_path'], '*.tiff'), z_start, z_numSlice, filt_size)
    count_data = readRadiographTifDir2(input_dict['data_path'], z_start, z_numSlice)
    angles = get_angles(input_dict['data_path'])
    print(angles)

    print('Applying median filter to remove gammas')
    count_data = median_filter(count_data, size=filt_size, axis=0, ncore=max_core)

    print(count_data.shape)
    print(brights.shape)
    print(darks.shape)

    norm_data = -np.log((count_data - darks) / (brights - darks))
    count_data[np.isnan(norm_data)] = 0  # remove the bad values
    count_data[np.isinf(norm_data)] = 0  # remove the bad values
    norm_data[np.isnan(norm_data)] = 0
    norm_data[np.isinf(norm_data)] = 0

    norm_data = remove_stripe_fw(norm_data, level=num_wav_level, ncore=max_core)

    if (input_dict['use_det_tilt'] == True):
        print('Tilt axis correction ..')
        count_data = apply_proj_tilt(count_data, input_dict['det_tilt'], ncore=max_core)
        norm_data = apply_proj_tilt(norm_data, input_dict['det_tilt'], ncore=max_core)

    ####Crop Data along the detector column axis #####
    count_data = count_data[:, :, tot_col // 2 - num_col // 2:tot_col // 2 + num_col // 2]
    norm_data = norm_data[:, :, tot_col // 2 - num_col // 2:tot_col // 2 + num_col // 2]
    ######End of data cropping #######

    norm_data = norm_data.swapaxes(0, 1)
    count_data = count_data.swapaxes(0, 1)

    # For data set 1
    print('Subsetting data ..')
    ang_idx = range(0, len(angles), input_dict['view_subsamp'])
    count_data = count_data[:, ang_idx, :]
    norm_data = norm_data[:, ang_idx, :]  # Subset to run on GPU
    angles = angles[ang_idx]

    print('Shape of data array')
    print(count_data.shape)

    proj_data = norm_data

    det_row, num_angles, det_col = proj_data.shape
    proj_dims = np.array([det_row, num_angles, det_col])

    proj_params = {}
    proj_params['type'] = 'par'
    proj_params['dims'] = proj_dims
    proj_params['angles'] = angles * np.pi / 180
    proj_params['forward_model_idx'] = 2
    proj_params['alpha'] = [np.pi / 2]
    proj_params['pix_x'] = input_dict['det_x']
    proj_params['pix_y'] = input_dict['det_y']

    vol_params = {}
    vol_params['vox_xy'] = input_dict['vox_xy']
    vol_params['vox_z'] = input_dict['vox_z']
    vol_params['n_vox_z'] = input_dict['n_vox_z']
    vol_params['n_vox_y'] = input_dict['n_vox_y']
    vol_params['n_vox_x'] = input_dict['n_vox_x']

    print('Starting MBIR..')
    rec_mbir = np.float32(MBIR(proj_data, count_data, proj_params, miscalib, vol_params, rec_params))
    #import pyqtgraph as pg
    #pg.image(rec_mbir);
    #pg.QtGui.QApplication.exec_()
    if input_dict["write_op"] == True:
        dxchange.write_tiff_stack(rec_mbir, fname=input_dict["op_path"], start=z_start, overwrite=True)

    # when done write stop file in batch mode
    #if input_dict["running_mode"] == "batch":


if __name__ == "__main__":
    main()
