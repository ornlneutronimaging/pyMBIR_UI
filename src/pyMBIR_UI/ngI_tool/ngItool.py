# -*- coding: utf-8 -*-
"""
Created on Thu Sep 04 13:01:57 2014
nGI-processing tool for python
@author: Tommy Reimann, FRM II
changed to fit into the NGI-GUI by Tobias Neuwirth, FRM II
"""
#import pyfits as pf
import numpy as np
#import matplotlib.pyplot as plt
import time
#from matplotlib.patches import Rectangle
#import sys
from scipy.optimize import leastsq
#from numpy import sin, mean
#import timeit
#from scipy import signal
#from scipy import misc
#from scipy import ndimage
import logging
from ngievaluation import evaluate_imagestack as simon

#import easyProc as ep
#import easyProc.helper
#import ddfSetupProcessing.HarmonicAnalysis.lsqprocessing as dpcprocess
#from numba import jit
#tic1=0
antares_stepping=12.2
stepping_offset=12500
def binning (image,n):

    """Bins a picture n x n"""

    height, width = np.shape(image)
    bin_image = np.zeros([height/n,width/n])
    for i in range(height/n):
        for j in range(width/n):
            pixel = 0
            for ni in range(n):
                for nj in range(n):
                    pixel +=image[n*i+ni][n*j+nj]
            bin_image[i][j]=pixel

    return bin_image

def rebin(a, n):
    height, width = np.shape(a)
    shape=[height//n,width//n]
    a_crop=a[0:n*shape[0],0:n*shape[1]]
    sh = shape[0],a_crop.shape[0]//shape[0],shape[1],a_crop.shape[1]//shape[1]
    return a_crop.reshape(sh).mean(axis=(-1,1))

def bin_ndarray(ndarray, n, operation='sum'):
    """
    Bins an ndarray in all axes based on the target shape, by summing or
        averaging.

    Number of output dimensions must match number of input dimensions.

    Example
    -------
    >>> m = np.arange(0,100,1).reshape((10,10))
    >>> n = bin_ndarray(m, new_shape=(5,5), operation='sum')
    >>> print(n)

    [[ 22  30  38  46  54]
     [102 110 118 126 134]
     [182 190 198 206 214]
     [262 270 278 286 294]
     [342 350 358 366 374]]

    """
    height, width = np.shape(ndarray)
    new_shape=(int(height/n),int(width/n))
    
    if not operation.lower() in ['sum', 'mean', 'average', 'avg']:
        raise ValueError("Operation not supported.")
    if ndarray.ndim != len(new_shape):
        raise ValueError("Shape mismatch: {} -> {}".format(ndarray.shape,
                                                           new_shape))
    compression_pairs = [(d, c//d) for d,c in zip(new_shape,
                                                  ndarray.shape)]
    flattened = [l for p in compression_pairs for l in p]
    
    ndarray = ndarray.reshape(flattened)
    for i in range(len(new_shape)):
        if operation.lower() == "sum":
            ndarray = ndarray.sum(-1*(i+1))
        elif operation.lower() in ["mean", "average", "avg"]:
            ndarray = ndarray.mean(-1*(i+1))
    return ndarray

def nGI(data_img_list,
        ob_img_list,
        dc_median,
        Fit,
        full_period,
        period_global,
        data_pos_list=None,
        ob_pos_list=None,
        data_norm_list=None,
        ob_norm_list=None,
        G0_rot=None):

    global antares_stepping
    """Program calculates TI, DPC, DFI """
    # define dc
    #global tic1
    #dc_stack = dc_img_listp
    dc = np.array(dc_median,dtype=np.uint16)

    # define data and substract dc
    #global data_stack
    data_stack_temp = np.asarray(data_img_list)
    #data_stack = data_img_list
    data_stack=[]
    for i in range(np.shape(data_stack_temp)[0]):

        data_stack_temp[i]-= dc

        if data_norm_list != None:
            data_temp=data_stack_temp[i]
            data_temp=data_temp.astype(np.float64)
           
            data_temp/=data_norm_list[i]
            

            data_stack.append(data_temp)
        else:
            data_stack.append(data_stack_temp[i])
         
    ob_stack_temp = np.asarray(ob_img_list)
    
    ob_stack=[]
   

    for i in range(np.shape(ob_stack_temp)[0]):
        ob_stack_temp[i]-= dc

        if ob_norm_list != None:
            ob_temp=ob_stack_temp[i]
            ob_temp=ob_temp.astype(np.float64)
           
            ob_temp/=ob_norm_list[i]
          

            ob_stack.append(ob_temp)
          
        else:
            ob_stack.append(ob_stack_temp[i])
  
    ob_stack=np.asanyarray(ob_stack)
    data_stack=np.asanyarray(data_stack)
    #print(np.shape(data_stack))
    count=len(data_img_list)
    height, width = np.shape(ob_stack[0])
  
    a0_ob = np.zeros([height,width],dtype=np.float32)
    a1_ob = np.zeros([height,width],dtype=np.float32)
    phi_ob = np.zeros([height,width],dtype=np.float32)
    a0_data = np.zeros([height,width],dtype=np.float32)
    a1_data = np.zeros([height,width],dtype=np.float32)
    phi_data= np.zeros([height,width],dtype=np.float32)
    TI = np.zeros([height,width],dtype=np.float32)
    DPC = np.zeros([height,width],dtype=np.float32)
    DFI = np.zeros([height,width],dtype=np.float32)
    # loop calculating parameter for every pixel. And add it to TI, DPC, DFI
    logging.info('<<< start evaluation >>>\n')
  
    progress = 0
    t_start = time.time()   #evaluation time determination
    if Fit == 'Sinus Fit':
        logging.info('Sinus Fit \n')


        for i in range(height):
          
            
            if progress != int(i*1.0/height*100):
            
                progress = int(i*1.0/height*100) 
                logging.info(str(progress)+" % of Sinus Fit finished")
            for j in range(width):
             
                pixel_values_ob=(np.arange(0,len(ob_stack)),ob_stack.T[j][i])
                a0_ob[i][j],a1_ob[i][j],phi_ob[i][j] = sinfit(pixel_values_ob,count,0,period_global,full_period)

                pixel_values_data=(np.arange(0,len(data_stack)),data_stack.T[j][i])
                a0_data[i][j],a1_data[i][j],phi_data[i][j] = sinfit(pixel_values_data,count,phi_ob[i][j],period_global,full_period)
            

                if a1_ob[i][j]<0:
                    a1_ob[i][j] *= -1
                    phi_ob[i][j] += np.pi
                else:
                    pass
                if a1_data[i][j]<0:
                    a1_data[i][j] *= -1
                    phi_data[i][j] += np.pi

                else:
                    pass

                TI[i][j] = a0_data[i][j]/a0_ob[i][j]
                DPC[i][j] = -phi_data[i][j]+phi_ob[i][j]
                if not -np.pi<=DPC[i][j]<=np.pi:
                    DPC[i][j] %= 2*np.pi
                DFI[i][j] = a1_data[i][j]*a0_ob[i][j]/a1_ob[i][j]/a0_data[i][j]
            

    elif Fit == 'FFT Fit':
        logging.info('FFT Fit \n')

        for i in range(height):
        
            if progress != int(i*1.0/height*100):
            
                progress = int(i*1.0/height*100)
                logging.info(str(progress)+" % of FFT Fit finished")
            for j in range(width):
                pixel_values_ob=(np.arange(0,len(ob_stack)),ob_stack.T[j][i])
                pixel_values_data=(np.arange(0,len(data_stack)),data_stack.T[j][i])
                a0_ob[i][j],a1_ob[i][j],phi_ob[i][j] = fft_fit(pixel_values_ob,count,full_period)
                a0_data[i][j],a1_data[i][j],phi_data[i][j] = fft_fit(pixel_values_data,count,full_period)

                TI[i][j] = a0_data[i][j]/a0_ob[i][j]
                DPC[i][j] = -phi_data[i][j]+phi_ob[i][j]
                if not -np.pi<=DPC[i][j]<=np.pi:
                    DPC[i][j] %= 2*np.pi
                DFI[i][j] = a1_data[i][j]*a0_ob[i][j]/a1_ob[i][j]/a0_data[i][j]

    elif (Fit == 'Matrix Fit') or (Fit == 'MATRIX'):
        logging.info('Matrix Fit \n')
        if data_pos_list == None:
            logging.info('Guessing equidistant positions \n')
            em_data_pos_list = np.linspace(0, 2*np.pi, data_stack.shape[0], False, dtype=np.float64)
            em_ob_pos_list = np.linspace(0, 2*np.pi, ob_stack.shape[0], False, dtype=np.float64)
        else:
            logging.info('Using provided positions \n')
            em_data_pos_list =(np.asanyarray(data_pos_list)-stepping_offset)/antares_stepping*2*np.pi
            em_ob_pos_list =(np.asanyarray(ob_pos_list)-stepping_offset)/antares_stepping*2*np.pi
           
        a0_data,a1_data,phi_data,phi_data_err=simon(data_stack.T,em_data_pos_list,algorithm='marathe')
        a0_ob,a1_ob,phi_ob,phi_ob_err=simon(ob_stack.T,em_ob_pos_list,algorithm='marathe')
        a0_data[a0_data<=1e-6]=1e-6
        a0_ob[a0_ob<=1e-6]=1e-6
        #a1_data=vis_data*a0_data
        #a1_ob=vis_ob*a0_ob
        a0_data=a0_data.T
        a1_data=a1_data.T
        phi_data=phi_data.T
        #phi_data_err=phi_data_err.T
        a0_ob=a0_ob.T
        a1_ob=a1_ob.T
        phi_ob=phi_ob.T
        #phi_ob_err=phi_ob_err.T
        if np.amin(a1_ob)<0 or np.amin(a1_data)<0:
            for i in range(height):
                for j in range(width):
                



                    if a1_ob[i][j]<0:
                      
                        a1_ob[i][j] *= -1.0
                        phi_ob[i][j] += np.pi
                       
                    else:
                        pass
                    if a1_data[i][j]<0:
                        
                        a1_data[i][j] *= -1.0
                        phi_data[i][j] += np.pi
                        

                    else:
                        pass
        a0_data[a0_data<=1e-6]=1e-6
        a0_ob[a0_ob<=1e-6]=1e-6
        TI = np.divide(a0_data,a0_ob)
        DPC = np.add(-phi_data,phi_ob)
       
        DPC_array=np.asarray(DPC)
        low_value_indice= DPC_array < -np.pi
        high_value_indice= DPC_array > np.pi
        DPC_array[low_value_indice]=(DPC_array[low_value_indice]+np.pi)%(2*np.pi)-np.pi
        DPC_array[high_value_indice]=(DPC_array[high_value_indice]+np.pi)%(2*np.pi)-np.pi
        DPC=DPC_array
        
        try:
            DFI = np.divide((np.multiply(a1_data,a0_ob)),(np.multiply(a1_ob,a0_data)))
        except RuntimeWarning:
            logging.warning("Division by zero while calculating the DFI")
         
    elif Fit == 'EM Fit':
        if data_pos_list == None:
            logging.info('Guessing equidistant positions \n')
            em_data_pos_list = np.linspace(0, 2*np.pi, data_stack.shape[0], False, dtype=np.float64)
            em_ob_pos_list = np.linspace(0, 2*np.pi, ob_stack.shape[0], False, dtype=np.float64)
        else:
            logging.info('Using provided positions \n')
            em_data_pos_list =(np.asanyarray(data_pos_list)-stepping_offset)/antares_stepping*2*np.pi
            em_ob_pos_list =(np.asanyarray(ob_pos_list)-stepping_offset)/antares_stepping*2*np.pi
        logging.info('Expectation Maximization \n')

        a0_data,a1_data,phi_data,phi_data_err=simon(data_stack.T,em_data_pos_list,algorithm='dittmann1+marathe')
        a0_ob,a1_ob,phi_ob,phi_ob_err=simon(ob_stack.T,em_ob_pos_list,algorithm='dittmann1+marathe')
        #a0_data,vis_data,phi_data, _, _, _, _, = ep.processing.gratings.em_processing_simple(data_stack,grating_positions=em_data_pos_list, processing_options={'stop_criterion': 0.001})
        #a0_ob,vis_ob,phi_ob, _, _, _, _, = ep.processing.gratings.em_processing_simple(ob_stack,grating_positions=em_ob_pos_list, processing_options={'stop_criterion': 0.001})
        a0_data[a0_data<=1e-6]=1e-6
        a0_ob[a0_ob<=1e-6]=1e-6
        #a1_data=vis_data*a0_data
        #a1_ob=vis_ob*a0_ob
        a0_data=a0_data.T
        a1_data=a1_data.T
        phi_data=phi_data.T
        phi_data_err=phi_data_err.T
        a0_ob=a0_ob.T
        a1_ob=a1_ob.T
        phi_ob=phi_ob.T
        phi_ob_err=phi_ob_err.T
        
        if np.amin(a1_ob)<0 or np.amin(a1_data)<0:
            for i in range(height):
                for j in range(width):
                    



                    if a1_ob[i][j]<0:
                       
                        a1_ob[i][j] *= -1.0
                        phi_ob[i][j] += np.pi
                       
                    else:
                        pass
                    if a1_data[i][j]<0:
                       
                        a1_data[i][j] *= -1.0
                        phi_data[i][j] += np.pi
                        

                    else:
                        pass
        
        TI = np.divide(a0_data,a0_ob)
        DPC = np.add(-phi_data,phi_ob)
        #print(TI.shape)
        DPC_array=np.asarray(DPC)
        low_value_indice= DPC_array < -np.pi
        high_value_indice= DPC_array > np.pi
        DPC_array[low_value_indice]=(DPC_array[low_value_indice]+np.pi)%(2*np.pi)-np.pi
        DPC_array[high_value_indice]=(DPC_array[high_value_indice]+np.pi)%(2*np.pi)-np.pi
        DPC=DPC_array
        
        try:
            DFI = np.divide((np.multiply(a1_data,a0_ob)),(np.multiply(a1_ob,a0_data)))
        except RuntimeWarning:
            logging.warning("Division by zero while calculating the DFI")
        
    elif Fit == 'Matrix Fit Advanced':
        logging.info('Matrix Fit Advanced \n')
        logging.info('Searching actual stepping period \n')
        steppingperiod, reconflats = findsteppingrange(ob_stack, 0.95, 1.4, 0.01)
        logging.info('Actual stepping period:' +str(steppingperiod)+' \n')
        if data_pos_list == None:
           
            a0_data,a1_data,phi_data = matrix_algorithm_fit(data_stack,period=steppingperiod)
            a0_ob,a1_ob,phi_ob = matrix_algorithm_fit(ob_stack,period=steppingperiod)
        else:
            
            a0_data,a1_data,phi_data = antares_matrix_algorithm_fit(data_pos_list,data_stack,G0_rot,period=steppingperiod)
            a0_ob,a1_ob,phi_ob = antares_matrix_algorithm_fit(ob_pos_list,ob_stack,G0_rot,period=steppingperiod)
     
        if np.amin(a1_ob)<0 or np.amin(a1_data)<0:
            for i in range(height):
                for j in range(width):
                    



                    if a1_ob[i][j]<0:
                        
                        a1_ob[i][j] *= -1.0
                        phi_ob[i][j] += np.pi
                        
                    else:
                        pass
                    if a1_data[i][j]<0:
                        
                        a1_data[i][j] *= -1.0
                        phi_data[i][j] += np.pi
                       

                    else:
                        pass
        a0_data[a0_data<=1e-6]=1e-6
        a0_ob[a0_ob<=1e-6]=1e-6
        TI = np.divide(a0_data,a0_ob)
        DPC = np.add(-phi_data,phi_ob)
     
        DPC_array=np.asarray(DPC)
        low_value_indice= DPC_array < -np.pi
        high_value_indice= DPC_array > np.pi
        DPC_array[low_value_indice]=(DPC_array[low_value_indice]+np.pi)%(2*np.pi)-np.pi
        DPC_array[high_value_indice]=(DPC_array[high_value_indice]+np.pi)%(2*np.pi)-np.pi
        DPC=DPC_array
       
        try:
            DFI = np.divide((np.multiply(a1_data,a0_ob)),(np.multiply(a1_ob,a0_data)))
        except RuntimeWarning:
            logging.warning("Division by zero while calculating the DFI")
           
    else:
        raise Exception('no fit procedure defined')
    logging.info('>>  evaluation time = %2i h %2i min %2.1f sec \n' % ((time.time()-t_start)/3600, ((time.time()-t_start)%3600)/60, (time.time()-t_start) % 60))
   
    TI_clipped=np.clip(TI,0,2)
    DPC_clipped=np.clip(DPC,-np.pi,np.pi)
    DFI_clipped=np.clip(DFI,0,2)
    return TI_clipped,DPC_clipped,DFI_clipped,a0_ob,a1_ob,phi_ob,a0_data,a1_data,phi_data
def normalization(stack,normreg):

    """Normalize an image. Uses the average pixel value in a rectangle (x1,y1,x2,y2)"""

    d=normreg

    Area = (d[3]-d[1])*(d[2]-d[0])

    for l in range(np.shape(stack)[0]):
        Norm = 0
        for i in range(d[3]-d[1]):
            for j in range(d[2]-d[0]):
                Norm += stack[l][i+d[1]][j+d[0]]/Area

        stack[l] /= Norm


    return stack
def sin_filter(fitpara,xandy,threshold,count,guess_phi,period_global,full_period):
    '''compares fit to data, if the distance lies above a threathold, the point is skipped'''
    xin,yin = xandy
    xi_temp,yi_temp=[],[]
    for i in range(len(xin)):
        if np.abs(yin[i]-fitfunc(fitpara,xin[i],count,period_global,full_period)) > threshold:
            pass
        else:
            xi_temp.append(xin[i])
            yi_temp.append(yin[i])
    if len(xin)==len(xi_temp):
        return fitpara
    else:
        
        xandy=np.array(xi_temp),np.array(yi_temp)
        return sinfit(xandy,count,guess_phi,'sin')
def sinfit(xandy,count,guess_phi,period_global,full_period,Filter = None):
    """Sin fit function for known frequency"""
    #tic1=timeit.default_timer()
    global tic1

    xin,yin = xandy
   

    errfunc = lambda p, x, y: (y - fitfunc(p, x,count,period_global,full_period))

    guess_offset    = np.mean(yin)
    guess_amplitude = np.max(yin)-guess_offset
    guess_phase     = guess_phi
    #x_temp,y_temp=[],[]


    p_init  = [guess_offset, guess_amplitude, guess_phase]
    out_fit = leastsq(errfunc, p_init, args=(xin, yin), full_output=0, maxfev=600)


    if Filter == 'sin':
        return sin_filter(out_fit[0],xandy,0.04,count,0,period_global,full_period)
    else:
        return out_fit[0]


def fft_fit(xandy,count,full_period):

    xin,yin = xandy
    step_period = count
    if full_period:
        step_period -=1
        fftb = np.fft.rfft(yin[:-1])/(step_period)
    else:
        fftb = np.fft.rfft(yin)/(step_period)
    outfft = (fftb[0],2*np.sqrt(np.real(fftb[1])**2+np.imag(fftb[1])**2),-np.angle(fftb[1]))
    return outfft

def matrix_algorithm_fit(stack,period=1):
    
    steps,height,width = np.shape(stack)
    x = range(steps)
    c = []
    for i in range(steps):
        c.append(np.ravel(stack[i]))
    c = np.matrix(c)
    B = np.zeros((np.shape(stack)[0],3))
    for j in range(np.shape(stack)[0]):
        B[j][0] = 1.0
        B[j][1] = np.cos(2*np.pi*x[j]*period/(steps-1.0))
        B[j][2] = np.sin(2*np.pi*x[j]*period/(steps-1.0))
    B = np.matrix(B)
    G  = (B.T*B).I*B.T
    a = np.asarray(((G*c).T).tolist())

    a0 = np.zeros((height,width),dtype=np.float32)
    a1 = np.zeros((height,width),dtype=np.float32)
    phi = np.zeros((height,width),dtype=np.float32)
  

    a0.flat = a.T[0]
    a1.flat = np.sqrt(a.T[1]**2 + a.T[2]**2)



    try:
        phi.flat = np.arctan2(a.T[2],a.T[1])
    except ZeroDivisionError as e:
        for i in range(height*width):
            try:
                phi.flat[i] = np.arctan2(a[i][2],a[i][1])
            except ZeroDivisionError as e:
                print (a[i][1])
    """
    for i in range(height*width):
        a0.flat[i] = a[i][0]
        a1.flat[i] = np.sqrt(a[i][1]**2 + a[i][2]**2)
        try:
            phi.flat[i] = np.arctan2(a[i][2],a[i][1])
        except ZeroDivisionError as e:
          
    """
    return a0,a1,phi
def antares_matrix_algorithm_fit(pos_list,stack,G0_rot,period=1):
    global antares_stepping
    steps,height,width = np.shape(stack)
    #x = range(steps)
    c = []
    for i in range(steps):
        c.append(np.ravel(stack[i]))
    c = np.matrix(c)
    B = np.zeros((np.shape(stack)[0],3))
    for j in range(np.shape(stack)[0]):
        B[j][0] = 1.0
        B[j][1] = np.cos(2*np.pi*pos_list[j]*period/(antares_stepping/np.cos(np.deg2rad(G0_rot))))
        B[j][2] = np.sin(2*np.pi*pos_list[j]*period/(antares_stepping/np.cos(np.deg2rad(G0_rot))))
    B = np.matrix(B)
    G  = (B.T*B).I*B.T

    a = np.asarray(((G*c).T).tolist())


    a0 = np.zeros((height,width),dtype=np.float32)
    a1 = np.zeros((height,width),dtype=np.float32)
    phi = np.zeros((height,width),dtype=np.float32)
    
    a0.flat = a.T[0]
    a1.flat = np.sqrt(a.T[1]**2 + a.T[2]**2)



    try:
        phi.flat = np.arctan2(a.T[2],a.T[1])
    except:
        #pass
        
        for i in range(height*width):
            try:
                phi.flat[i] = np.arctan2(a[i][2],a[i][1])
            except ZeroDivisionError as e:
                phi.flat[i] = 0
                
                logging.warning("Division by zero while calculating the Phase. Replacing the value by zero.")
        

    return a0,a1,phi


def pixel_values(stack,i,j):
    #tic1=timeit.default_timer()
    """Returns the values of one Image-Pixel in the Stack as a np.array"""

    index = []
    data = []
    for l in range(np.shape(stack)[0]):
        index.append(l)
        data=stack[:][i][j]
    index,data = np.array(index),np.array(data)

    return index,data
def fitfunc(p,x,count,period_global,full_period):
    '''the function used to fit and plot the data'''
    step_period = count
    period_global=1
    full_period=True
    if full_period:
        step_period -= 1
    return p[0] + p[1]*np.cos(x*2*np.pi*period_global/(step_period)-p[2])
def findsteppingrange(steppdata, start, end, step, plot=False):
   """ finds most propable steppingperiod, apply better only on flatfields
   input: stepped data (ndarray)
          start: where to start e.g. 0.9 for 0.9 of period
          end: where to end eg. 1.1 of period
          step: in which steps to search e.g. 0.01 of period
          
   """
   processedperiods = []
   stdVisibility = []
   meanVisibility = []
   ptp = np.arange(start, end, step)
   for i in range(ptp.shape[0]):
       p = ptp[i]
       
       logging.info('Checking'+ str(p) + ' periods \n')
       coeff = dpcprocess.lsq_fit(steppdata, nb_periods = p, order = 3)
       a0=coeff[0,0]
       a1=coeff[0,1]
       phi=coeff[1,1]
       a0[a0<=1e-6]=1e-6
       V=a1/a0
       #pg.image(V)
       processedperiods.append(V)
       stdVisibility.append(np.std(V))
       meanVisibility.append(np.mean(V))
       
   return ptp[np.argmin(stdVisibility)], np.array(processedperiods)
