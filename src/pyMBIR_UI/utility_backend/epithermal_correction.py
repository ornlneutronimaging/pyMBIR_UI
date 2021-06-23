# -*- coding: utf-8 -*-
"""
Created on Fri April 06 16:00:10 2018

@author: tneuwirt
"""
import numpy as np
#from scipy import signal
#from scipy import misc
#from scipy import ndimage
#import time
#import logging
#from numba import jit
#@jit
def epithermal_correction(image,threshold):
    image_temp=np.array(image, dtype=np.float32)
    thr=np.logical_xor(image_temp>(threshold*np.median(image_temp)),image_temp<(np.median(image_temp)/threshold))
    #print thr
    img_adp=np.copy(image_temp)
    index = np.nonzero(thr)
    thresh = np.shape(index)[1]
    sub=np.copy(np.median(image_temp))
    for i in range(thresh):
        img_adp[index[0][i],index[1][i]]=sub
    for i in range(thresh):
        img_adp[index[0][i],index[1][i]]=np.median(img_adp[index[0][i]-2:index[0][i]+3, index[1][i]-2:index[1][i]+3])
    return img_adp
"""
test=np.array([[12,13,42,16,43,2],[23,12,1,14,56,7],[14,16,17,15,18,15]])
test_2=epithermal_correction(test,3)
print np.median(test)
print test
print test_2
"""