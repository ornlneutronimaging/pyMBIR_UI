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
from dxchange.writer import write_tiff_stack
import dxchange
from tomopy.misc.corr import median_filter
import os
import json

from tomoORNL.reconEngine import analytic, MBIR
from tomoORNL.corrections import apply_proj_tilt

import numpy as np
from astropy.io import fits
from skimage.io import imread
import glob
import string as str
from PIL import Image
from collections import OrderedDict

STOP_FILE_NAME = "OVER.json"


def get_angles(data_path):
    '''
    Script to read angles from tiff files at ORNL 
    '''
    ANGLE_KEY = 65039  #65048 
    x=retrieve_value_of_metadata_key(list_files=sorted(glob.glob(os.path.join(data_path,'*.tiff'))), list_key=[ANGLE_KEY])
    angles = np.zeros(len(x))
    for idx,val in enumerate(list(x.items())):
        temp=val[1]
        angles[idx]=float(next(iter(temp.values())).split(':')[1])
    return angles 


def get_value_of_metadata_key(filename='', list_key=None):
    '''
    From https://github.com/JeanBilheux/python_101/blob/master/working_with_images/images_metadata/using%20code%20from%20python%20notebooks.ipynb
    '''

    if filename == "":
        return {}

    image = Image.open(filename)
    metadata = image.tag_v2
    result = {}
    if list_key == []:
        for _key in metadata.keys():
            result[_key] = metadata.get(_key)
        return result

    for _meta in list_key:
        result[_meta] = metadata.get(_meta)

    image.close()
    return result

def retrieve_value_of_metadata_key(list_files=[], list_key=[]):
    '''
    From https://github.com/JeanBilheux/python_101/blob/master/working_with_images/images_metadata/using%20code%20from%20python%20notebooks.ipynb
    '''
    if list_files == []:
        return {}

    _dict = OrderedDict()
    for _file in list_files:
        _meta = get_value_of_metadata_key(filename=_file,
                                                         list_key=list_key)
        _dict[_file] = _meta

    return _dict

def readAverageFitsDir(fpath,z_start,z_numSlice):
    """Function to read and average a stack of fits images from the path - fpath
        """
    file_list = sorted(glob.glob(fpath + '/*.fit*'))
    num_im = len(file_list)
    print(num_im)
    data = fits.open(file_list[0])[0].data.astype('float')
    for file_elt in file_list[1:]:
        data = data + fits.open(file_elt)[0].data.astype('float')
    data = data / num_im
    if(data.ndim>2):
        data = np.squeeze(data,0) #Did this because of quirks with data set from Philip
    data = np.rot90(data[:,z_start:z_start+z_numSlice]) #Did this because of quirks with data set from Philip
    return data


def readRadiographFitsDir(fpath,z_start,z_numSlice):
    """Function to read  a stack of fits images from the path - fpath
    and return the data in a numpy array along with the list of angles
        """
    delimiter = '_'
    file_list = sorted(glob.glob(fpath + '/*.fits'))
    num_im = int(len(file_list))
    # Determine image size from header
    im_size = np.zeros(2).astype(np.int16)
    temp_file = fits.open(file_list[0])
    im_size[0] = int(temp_file[0]._header['NAXIS1'])
    im_size[1] = int(temp_file[0]._header['NAXIS2'])
    print(im_size)
    count_data = np.zeros((num_im, z_numSlice, im_size[1]))
    angle_list = np.zeros(num_im)
    count = 0
    for file_elt in file_list:
        count_data[count, :, :] = (fits.open(file_elt)[0].data.astype('float'))[z_start:z_start+z_numSlice,:]#np.rot90
        temp_split = file_elt.split(delimiter) #str.split(file_elt, delimiter)
        angle_list[count] = float(temp_split[-3] + '.' + temp_split[-2])
        count = count + 1

    return count_data, angle_list

def readAverageTiffDir(fpath,z_start,z_numSlice):
    """Function to read and average a stack of tiff images from the path - fpath
        """
    file_list = glob.glob(fpath + '/*.tiff')
    num_im = len(file_list)
    print(num_im)
    data = (imread(file_list[0])[z_start:z_start+z_numSlice,:].astype('float'))
    for file_elt in file_list[1:]:
        data = data + (imread(file_elt)[z_start:z_start+z_numSlice,:].astype('float'))
    data = data / num_im
    return data


def readRadiographTifDir(fpath,z_start,z_numSlice):
    """Function to read  a stack of tifs images from the path - fpath
    and return the data in a numpy array along with the list of angles
    TODO: Hacks to rotate the image
        """
    delimiter = '_'
#    num_digits = 4

    file_list = sorted(glob.glob(fpath + '/*.tif*'))
    num_im = len(file_list)
    # Determine image size from header
    im_size = np.zeros(2)
    temp_img = imread(file_list[0])
    im_size=temp_img.shape
    print(im_size)
    count_data = np.zeros((num_im, z_numSlice, im_size[0]))
    angle_list = np.zeros(num_im)
    count = 0
    for file_elt in file_list:
        count_data[count, :, :] = ((imread(file_elt)).astype('float')[z_start:z_start+z_numSlice,:])#np.rot90
        temp_split = file_elt.split(delimiter)
        angle_list[count] = float(temp_split[-3]+'.'+temp_split[-2])#float(temp_split[-1][1:1+num_digits] + '.' + temp_split[-1][6:6+num_digits])
        count = count + 1

    return count_data, angle_list


def readRadiographTifDir2(fpath,z_start,z_numSlice):
    """Function to read  a stack of tifs images from the path - fpath
    and return the data in a numpy array along with the list of angles
    TODO: Hacks to rotate the image
        """
    delimiter = '_'

    file_list = sorted(glob.glob(fpath + '/*.tif*'))
    num_im = len(file_list)
    # Determine image size from header
    im_size = np.zeros(2)
    temp_img = imread(file_list[0])
    im_size=temp_img.shape
    print(im_size)
    count_data = np.zeros((num_im, z_numSlice, im_size[1]))
    count = 0
    for file_elt in file_list:
        count_data[count, :, :] = ((imread(file_elt)).astype('float')[z_start:z_start+z_numSlice,:])#np.rot90
        count = count + 1

    return count_data

def readRadiographTifDirCont(fpath,z_start,z_numSlice,start_time_idx,end_time_idx):
    """Function to read  a stack of tifs images from the path - fpath
    and return the data in a numpy array along with the list of angles
    TODO: Hacks to rotate the image
        """
    delimiter = '_'

    file_list = sorted(glob.glob(fpath + '/*.tif*'))[start_time_idx:end_time_idx]
    num_im = len(file_list)
    # Determine image size from header
    im_size = np.zeros(2)
    temp_img = imread(file_list[0])
    im_size=temp_img.shape
    print(im_size)
    count_data = np.zeros((num_im, z_numSlice, im_size[1]))
    count = 0
    for file_elt in file_list:
        count_data[count, :, :] = ((imread(file_elt)).astype('float')[z_start:z_start+z_numSlice,:])#np.rot90
        count = count + 1

    return count_data


def readBurkhardCounts(fpath,delimiter,start_str,z_start,z_numSlice):
    """Function to read  a stack of tifs images from the path - fpath
    and return the data in a numpy array along with the list of angles
    TODO: Hacks to rotate the image
       """
    NUM_DIGITS=4
    file_list = glob.glob(fpath + '/' + start_str +'*.tif')
    num_im = len(file_list)
    #Determine image size from header
    im_size = np.zeros(2)
    temp_img = imread(file_list[0])
    im_size=temp_img.shape
    print(im_size)
    count_data = np.zeros((num_im, z_numSlice, im_size[1]))
    angle_list = np.zeros(num_im)
    count = 0
    for file_elt in file_list:
      count_data[count, :, :] = (imread(file_elt).astype('float')[z_start:z_start+z_numSlice,:])
      temp_split = str.split(file_elt,delimiter)[1][0:NUM_DIGITS] #file_elt.split(delimiter)[0][-NUM_DIGITS:]
#      print(str.split(file_elt,delimiter)[1][0:NUM_DIGITS])
      angle_list[count] = float(temp_split)
      count = count + 1

    return count_data, angle_list


def readRadiographFitsDirBurkhard(fpath,delimiter,z_start,z_numSlice):
    """Function to read  a stack of fits images from the path - fpath
    and return the data in a numpy array along with the list of angles
        """
    file_list = glob.glob(fpath + '/*.fits')
    num_im = len(file_list)
    print(num_im)
    # Determine image size from header
    im_size = np.zeros(2).astype(np.int16)
    temp_file = fits.open(file_list[0])
    im_size[0] = int(temp_file[0]._header['NAXIS1'])
    im_size[1] = int(temp_file[0]._header['NAXIS2'])
    print(im_size)
    count_data = np.zeros((num_im, z_numSlice, im_size[0])) 
    angle_list = np.zeros(num_im)
    count = 0
    for file_elt in file_list:
        count_data[count, :, :] = fits.open(file_elt)[0].data.astype('float')[z_start:z_start+z_numSlice,:]
        angle_list[count] = float(str.split(str.split(file_elt,delimiter)[-1],'.fits')[0])
        count = count + 1

    return count_data,angle_list

def readAverageTifDir_Engine(fpath,z_start,z_numSlice):
    """Function to read and average a stack of tiff images from the path - fpath
        """
    file_list = glob.glob(fpath)
    num_im = len(file_list)
    print(num_im)
    data = (imread(file_list[0])[z_start:z_start+z_numSlice,:].astype('float'))
    for file_elt in file_list[1:]:
        data = data + (imread(file_elt)[z_start:z_start+z_numSlice,:].astype('float'))
    data = data / num_im
    return data

def readMedianTifDir(fpath,z_start,z_numSlice,filt_size=3):
    """Function to read, apply a "3D" median filter and then average a stack of images 
        """
    file_list = glob.glob(fpath)
    num_im = len(file_list)
    print(num_im)
    temp_data = imread(file_list[0])
    data = np.zeros((num_im,z_numSlice,temp_data.shape[1])).astype(np.float32)
    for idx,file_elt in enumerate(file_list):
        data[idx] = (imread(file_elt)[z_start:z_start+z_numSlice,:].astype('float'))
    #from tomopy.misc.corr import median_filter
    #data=median_filter(data,size=filt_size,axis=0)
    from scipy.ndimage import median_filter
    data=median_filter(data, size=(filt_size,filt_size,filt_size), mode='reflect')
    data=data.mean(axis=0)
    return data

def readRadiographTifDir_Engine(fpath,z_start,z_numSlice):
    """Function to read  a stack of tifs images from the path - fpath
    and return the data in a numpy array along with the list of angles
    TODO: Hacks to rotate the image
        """
    delimiter = '_'
#    num_digits = 4

    file_list = sorted(glob.glob(fpath))
    num_im = len(file_list)
    # Determine image size from header
    im_size = np.zeros(2)
    temp_img = imread(file_list[0])
    im_size=temp_img.shape
    print(im_size)
    count_data = np.zeros((num_im, z_numSlice, im_size[0]))
    angle_list = np.zeros(num_im)
    count = 0
    for file_elt in file_list:
        count_data[count, :, :] = (imread(file_elt).astype('float')[z_start:z_start+z_numSlice,:])#np.rot90
        temp_split = file_elt.split(delimiter) #str.split(file_elt, delimiter)
        angle_list[count] = float(temp_split[-3]+'.'+temp_split[-2])#float(temp_split[-1][1:1+num_digits] + '.' + temp_split[-1][6:6+num_digits])
        count = count + 1

    return count_data, angle_list

def readRadiographTifDir_Christina(fpath,z_start,z_numSlice):
    """Function to read  a stack of tifs images from the path - fpath
    and return the data in a numpy array along with the list of angles
    TODO: Hacks to rotate the image
        """
    delimiter = '_'
    file_list = sorted(glob.glob(fpath + '/*.tif*'))
    num_im = len(file_list)
    # Determine image size from header
    im_size = np.zeros(2)
    temp_img = imread(file_list[0])
    im_size=temp_img.shape
    print(im_size)
    count_data = np.zeros((num_im, z_numSlice, im_size[1])) #was im_size[0]
    count = 0
    for file_elt in file_list:
        count_data[count, :, :] = (imread(file_elt).astype('float'))[z_start:z_start+z_numSlice,:]#np.rot90
        count = count + 1

    return count_data


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
        print(f"input_dict['op_path']: {input_dict['op_path']}")
        temp_path = os.path.join(input_dict['op_path'], "mbir")
        dxchange.write_tiff_stack(rec_mbir, fname=temp_path, start=z_start, overwrite=True)

    # when done write stop file in batch mode
    if input_dict["running_mode"] == "batch":
        with open(STOP_FILE_NAME, 'w') as json_file:
            json.dump({"stop": True}, json_file)


if __name__ == "__main__":
    main()


