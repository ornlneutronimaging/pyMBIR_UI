# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 10:01:06 2016

@author: tneuwirt
"""

from . import multi_logger as ml
from .gam_rem_adp_log.gam_rem_adp_log import gam_rem_adp_log as holy_grail
import multiprocessing

#from utility_backend.pool_ext import Pool_win,Process
def _call_filterfunc(param_list):
    img = param_list[0]
    thr3 = param_list[1]
    thr5 = param_list[2]
    thr7 = param_list[3]
    sig_log = param_list[4]
    return holy_grail(img, thr3, thr5, thr7, sig_log)

def filter_image(img_list, filter_params,queue):
    #multiprocessing_logging.install_mp_handler()
    """Takes a list of datasets and filters them using gam_rem_adp_log()"""
    merged_data = []
    filtered_images=[]
    for img in img_list:
        merged_data.append([img] + filter_params)

    pool = multiprocessing.Pool(initializer=ml.worker_configurer,initargs=(queue,))
    for filter_image,filter_para in pool.map(_call_filterfunc, merged_data):
        filtered_images.append(filter_image)
    pool.close()

    pool.join()
    return filtered_images
