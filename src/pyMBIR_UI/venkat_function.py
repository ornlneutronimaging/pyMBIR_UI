import numpy as np
import logging
from qtpy.QtCore import QObject, QThread, Signal
from tomopy import remove_stripe_fw
from pyMBIR.reconEngine import analytic, MBIR
from pyMBIR.utils import apply_proj_tilt
from readNeutronData import *
from tomopy.misc.corr import median_filter
import os
import dxchange
import time



class Worker(QObject):
    finished = Signal()
    progress = Signal(int, float)
    sent_reconstructed_array = Signal(np.ndarray)

    def init(self, dictionary_of_arguments=None):
        self.dictionary_of_arguments = dictionary_of_arguments

    def run(self):

        nbr_iteration = 20
        sleeping_time = 3  # s
        dictionary_of_arguments = self.dictionary_of_arguments

        my_function(nbr_iteration, sleeping_time, self.finished, self.progress, self.sent_reconstructed_array)

        # for _i in np.arange(nbr_iteration):
        #     time.sleep(sleeping_time)
        #     fake_2d_array = np.random.random((512, 512))
        #     self.sent_reconstructed_array.emit(fake_2d_array)    # I need this
        #
        #     logging.info(f"worker iteration {_i+1}/{nbr_iteration}")
        #
        #     self.progress.emit(_i+1, 0.5)
        # self.finished.emit()

def my_function(nbr_iteration, sleeping_time, finished, progress, sent_reconstructed_array):

    for _i in np.arange(nbr_iteration):
        time.sleep(sleeping_time)
        fake_2d_array = np.random.random((512, 512))
        sent_reconstructed_array.emit(fake_2d_array)  # I need this

        logging.info(f"worker iteration {_i + 1}/{nbr_iteration}")

        progress.emit(_i + 1, 0.5)
    finished.emit()


class VenkatWorker(QObject):
    finished = Signal()
    progress = Signal(int,float)
    sent_reconstructed_array = Signal(np.ndarray)

    def init(self, dictionary_of_arguments=None):
        self.dictionary_of_arguments = dictionary_of_arguments

    def run(self):
        #venkat_my_function(self.progress, self.finished)
        MBIR_fromGUI(self.dictionary_of_arguments,
                     {'progress': self.progress,
                      'finished': self.finished,
                      'sent_recon_array': self.sent_reconstructed_array,
                      'emit_freq': 5})

# def venkat_my_function(progress, finished):
#
#     for _i in np.arange(10):
#         time.sleep(2)
#         progress.emit(_i)
#     finished.emit()


def run_venkat_function(parent=None):
    parent.thread = QThread()
    parent.worker = VenkatWorker()
    parent.worker.moveToThread(parent.thread)
    parent.thread.started.connect(parent.worker.run)
    parent.worker.finished.connect(parent.thread.quit)
    parent.worker.finished.connect(parent.worker.deleteLater)
    parent.thread.finished.connect(parent.thread.deleteLater)
    parent.worker.progress.connect(reportProgress)
    parent.thread.start()


def reportProgress():
    print("in report progress")

def create_circle_mask(y,x,center,rad):
    mask = (x-center[0])*(x-center[0]) + (y-center[1])*(y-center[1]) <= rad*rad
    return mask
    
def MBIR_fromGUI(input_params, gui_params):
    '''
    2 dictionaries from the GUI interface
    input_params : Has all the user inputs including advanced params 
    gui_params : Broad cast arrays and other params that are required for GUI code 
    '''
    
    max_core = input_params['max_core']
    num_wav_level = input_params['wav_level']
    tot_col = input_params['tot_col']
    num_col = input_params['num_col']
    rot_center = input_params['rot_center']
    
    rec_params={}
    rec_params['debug']=False
    rec_params['verbose']=True
    rec_params['num_iter']=input_params['max_iter']
    rec_params['gpu_index']=range(0,input_params['num_gpu'])
    rec_params['MRF_P']=input_params['mrf_p']
    rec_params['MRF_SIGMA']=input_params['mrf_sigma']
    rec_params['stop_thresh']=float(input_params['stop_thresh'])

    #GUI related params 
    rec_params['gui_emit']=True
    rec_params['emit_freq']=gui_params['emit_freq']
    rec_params['sent_recon_array']=gui_params['sent_recon_array']
    rec_params['progress']=gui_params['progress']
    rec_params['finished']=gui_params['finished']

    #rec_params['filt_type']='Ram-Lak'
    #rec_params['filt_cutoff']=f_c

    #Miscalibrations - detector offset, tilt
    miscalib={}
    miscalib['delta_u']=(tot_col/2 - rot_center)
    miscalib['delta_v']=0
    miscalib['phi']=0 

    z_start = input_params['z_start']
    z_numSlice = input_params['z_numSlice']
    filt_size=input_params['med_filt_win'] #window of median filter 
    print(os.path.join(input_params['brt_path'],'*.tiff'))
    #Read data
    print('Reading slices from %d to %d with %d cores' %(z_start,z_numSlice,max_core))
    brights=readMedianTifDir(os.path.join(input_params['brt_path'],'*.tiff'),z_start,z_numSlice,filt_size)
    darks=readMedianTifDir(os.path.join(input_params['drk_path'],'*.tiff'),z_start,z_numSlice,filt_size)
    count_data=readRadiographTifDir2(input_params['data_path'],z_start,z_numSlice)
    angles =get_angles(input_params['data_path']) 

    #Pre-process 
    print('Applying median filter to remove gammas')
    count_data= median_filter(count_data,size=filt_size,axis=0,ncore=max_core)

    print(count_data.shape)
    print(brights.shape)
    print(darks.shape)

    #Normalize and correct 
    norm_data = -np.log((count_data - darks) / (brights - darks))
    count_data[np.isnan(norm_data)]=0 #remove the bad values
    count_data[np.isinf(norm_data)]=0 #remove the bad values 
    norm_data[np.isnan(norm_data)]=0
    norm_data[np.isinf(norm_data)]=0

    #More pre-process 
    norm_data = remove_stripe_fw(norm_data,level=num_wav_level,ncore=max_core)

    if(input_params['use_det_tilt'] == 'True'):
        print('Tilt axis correction ..')
        count_data=apply_proj_tilt(count_data,input_params['det_tilt'],ncore=max_core)
        norm_data=apply_proj_tilt(norm_data,input_params['det_tilt'],ncore=max_core)

    ####Crop Data along the detector column axis #####
    count_data= count_data[:,:,tot_col//2-num_col//2:tot_col//2+num_col//2]
    norm_data = norm_data[:,:,tot_col//2-num_col//2:tot_col//2+num_col//2]
    ######End of data cropping #######
    
    norm_data=norm_data.swapaxes(0,1)
    count_data=count_data.swapaxes(0,1)
    
    #For data set 1
    print('Subsetting data by a factor of %d' %(input_params['view_subsamp']))
    ang_idx = range(0,len(angles),input_params['view_subsamp'])
    count_data=count_data[:,ang_idx,:]
    norm_data = norm_data[:,ang_idx,:] #Subset to run on GPU 
    angles = angles[ang_idx]
    
    print('Shape of data array')
    print(count_data.shape)
    
    proj_data = norm_data 
    
    det_row,num_angles,det_col=proj_data.shape
    proj_dims=np.array([det_row,num_angles,det_col])
    
    proj_params={}
    proj_params['type'] = 'par'
    proj_params['dims']= proj_dims
    proj_params['angles'] = angles*np.pi/180
    proj_params['forward_model_idx']=2
    proj_params['alpha']=[np.pi/2]
    proj_params['pix_x']=input_params['det_x']
    proj_params['pix_y']=input_params['det_y']
    
    vol_params={}
    vol_params['vox_xy']=input_params['vox_xy']
    vol_params['vox_z']=input_params['vox_z']
    vol_params['n_vox_z']=input_params['n_vox_z'] 
    vol_params['n_vox_y']=input_params['n_vox_y'] 
    vol_params['n_vox_x']=input_params['n_vox_x'] 

    print('Starting MBIR..')
    rec_mbir=np.float32(MBIR(proj_data,count_data,proj_params,miscalib,vol_params,rec_params))

    if input_params['write_op'] == 'True':
        temp_str = 'mbir' 
        temp_path=os.path.join(input_params['op_path'],temp_str)
        dxchange.write_tiff_stack(rec_mbir, fname=temp_path, start=z_start,overwrite=True)


'''
def full_recon_testdata(progress,finished,sent_recon_array):
    #Detector and experiment parameters
    num_angles = 256
    det_row = 128
    det_col = 256
    
    #Input flux and noise 
    I0 = 2e4
    noise_std = 1
    off_center_u = 20 #Number of pixels by which the center of rotation is off. To test artifacts due to this type of error.
    off_center_v=0
    det_tilt=0 
    lam_angle = 70 #Laminography angle
    det_x=1.0
    det_y=1.0
    vox_xy=1.0
    vox_z=1.0
    
    disc_height = 40
    center1=np.array([0,0])
    disc_rad1 = 100
    density1=0.01
    
    ring1_length = 50
    ring1_rad = 42
    ring2_length = 50
    ring2_rad = 25
    theta_list = np.array([0,72,144,216,288])*np.pi/180
    density2=0.02
    
    # Geometry for laminography 
    alpha=np.array([lam_angle])
    
    #Miscalibrations - detector offset, tilt
    miscalib={}
    miscalib['delta_u']=off_center_u
    miscalib['delta_v']=off_center_v
    miscalib['phi']=det_tilt*np.pi/180
    
    #MRF parameters
    MRF_P = 1.2 #1.2
    MRF_SIGMA = 0.5 

    NUM_ITER = 200
    gpu_index = 0
    
    ######End of inputs#######
    
    im_size = np.int(det_col*det_x/vox_xy) # n X n X n_slice volume             
    num_slice = np.int(det_row*det_y/vox_z)
    
    astra.astra.set_gpu_index(gpu_index)
    alpha=alpha*np.pi/180
    
    obj = np.zeros((num_slice,im_size,im_size)).astype(np.float32)
    
    y,x=np.ogrid[-im_size/2:im_size/2,-im_size/2:im_size/2]
    height_idx = slice(np.int(det_row/2-disc_height/2),np.int(det_row/2+disc_height/2))
    
    mask=create_circle_mask(y,x,center1,disc_rad1)
    obj[height_idx,mask]=density1
    
    for theta in theta_list:
        center_temp=np.array([ring1_length*np.cos(theta),ring1_length*np.sin(theta)])
        mask1 = create_circle_mask(y,x,center_temp,ring1_rad)
        mask2 = create_circle_mask(y,x,center_temp,ring2_rad)
    obj[height_idx,mask1^mask2] = density2

    
    # ----------------------------------
    # Parallel beam Laminography Vectors
    # ----------------------------------
    # Parameters: width of detector column, height of detector row, #rows, #columns
    angles = np.linspace(0, 2*np.pi, num_angles, False)
    
    proj_dims=np.array([det_row,num_angles,det_col])
    
    proj_params={}
    proj_params['type'] = 'par'
    proj_params['dims']= proj_dims
    proj_params['angles'] = angles
    proj_params['alpha'] = np.array([alpha])
    proj_params['forward_model_idx']=2
    
    proj_params['pix_x']= det_x
    proj_params['pix_y']= det_y
    
    vol_params={}
    vol_params['vox_xy'] = vox_xy
    vol_params['vox_z'] = vox_z
    vol_params['n_vox_x']=det_col
    vol_params['n_vox_y']=det_col
    vol_params['n_vox_z']=det_row

    A=generateAmatrix(proj_params,miscalib,vol_params,gpu_index)
    proj_data = A*obj
    proj_data=proj_data.astype(np.float32).reshape(det_row,num_angles,det_col)

    #Simulate Poisson like statistics using Gaussian approximation
    weight_data = createTransmission(proj_data,I0,noise_std)
    
    
    #Test projector
    print('Min/Max %f/%f of weight data' %(weight_data.min(),weight_data.max()))
    proj_data = np.log(I0/weight_data)
    
    #Display object
    print('Actual projection shape (%d,%d,%d)'% proj_data.shape)
    temp_proj_data=np.swapaxes(proj_data,0,1)
    temp_proj_data=np.swapaxes(temp_proj_data,1,2)
    print(temp_proj_data.shape)
    
    print(proj_data.shape)
    
    rec_params={}
    rec_params['num_iter'] = NUM_ITER
    rec_params['gpu_index']= gpu_index
    rec_params['MRF_P'] = MRF_P
    rec_params['MRF_SIGMA'] = MRF_SIGMA
    rec_params['debug']=False
    rec_params['huber_T']=5
    rec_params['huber_delta']=0.1
    rec_params['sigma']=1
    rec_params['reject_frac']=.1
    rec_params['verbose']=True
    rec_params['stop_thresh']=0.001


    rec_params['gui_emit']=True
    rec_params['emit_freq']=5
    rec_params['sent_recon_array']=sent_recon_array
    rec_params['progress']=progress
    rec_params['finished']=finished

    #params for fbp
    rec_params['filt_type']='Ram-Lak'
    rec_params['filt_cutoff']=0.8
    
    recon_mbir=MBIR(proj_data,weight_data,proj_params,miscalib,vol_params,rec_params)
'''
