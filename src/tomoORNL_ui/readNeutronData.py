import numpy as np
from astropy.io import fits
from skimage.io import imread
import glob
import string as str
from PIL import Image
from collections import OrderedDict
import os


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
