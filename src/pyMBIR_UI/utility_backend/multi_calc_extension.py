#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 16:11:22 2018

@author: tneuwirt
"""

import numpy as np
import os
import glob
from itertools import cycle
#import re


#path="/media/antaressrv/FRM-II/2018/p13977/002_Corr_Scan_30_U_0_0_27/data/p13977_00009007.dat"
#path_2="/media/antaressrv/FRM-II/2018/p13977/007_Corr_Scan_65_U_0_0_27/data"
def open_scan_file(path):
    fname=open(path,"r")
    lines=fname.readlines()
    data_lines=[]
    for i in lines:
        if i[0]!="#":
            temp=i.rstrip().split("\t")
       
            data_lines.append([temp[0],temp[-1]])
    return np.array(data_lines)


def guess_ips(data_lines):
    pos_list=np.array(data_lines.T[0],dtype=np.float)
    for i in range(len(pos_list)):
        temp=np.mean(pos_list[0:i+1])
        if temp !=pos_list[0]:
            img_per_step= i
            break
    return img_per_step
def create_file_path(path):
    temp_ind=path.rfind(str(os.path.sep)+"data")
    data_path=path[:temp_ind]
    return data_path
def generate_load_data(path):
    data_lines=open_scan_file(path)
    data_path=create_file_path(path)
   
    ips=guess_ips(data_lines)
    img_list=np.array(data_lines.T[1])
    
    first_img_path=str(data_path)+str(os.path.sep)+str(img_list[0])
    last_img_path=str(data_path)+str(os.path.sep)+str(img_list[-1])
    img_num,y=img_list.shape()
    return first_img_path, last_img_path,ips,img_num
def alpha_num_split(s):
    return (''.join(c for c in s if c.isdigit()) or None, 
            ''.join(c for c in s if c.isalpha()) or None)
def check_scan(folder,scan_order,exp_img,start_scan=None):
    scan_list=glob.glob(folder+str(os.path.sep)+"*.dat")
    if len(scan_list)==0:
        print("No scan files found in this folder.")
    scan_list.sort()
    try:
        start_ind=scan_list.index(folder+str(os.path.sep)+str(start_scan))
    except ValueError:
        print("Specified staring scan file has not been found. Setting first scan file as starting scan file.")
        start_ind=0
    scan_list_cropped=scan_list[start_ind:]
    first_scan=scan_list[start_ind]
    split_scan=scan_order.split("-")
    split_scan_2=np.array(map(alpha_num_split,split_scan))
    scans_per_cycle=np.sum(np.array(split_scan_2.T[0],dtype=np.int))  
    if len(scan_list_cropped) >=scans_per_cycle:
        data_lines=open_scan_file(scan_list_cropped[scans_per_cycle-1])
        if data_lines.shape[0] == exp_img:
            return scan_list_cropped[:scans_per_cycle]
        else:
            return "Not enough Images in the Last Scan"
    else:
        return "Waiting on Scan" 
            
def prep_scan_data(scan_list,scan_order,start_scan=None,file_identifier=[None]):
    split_scan=scan_order.split("-")
    split_scan_2=np.array(map(alpha_num_split,split_scan))
    scan_type_list=[]
    for i in split_scan_2:
        for j in range(int(i[0])):
            scan_type_list.append(str(i[1]))
 
    pool=cycle(scan_type_list)
    points_per_scan=np.sum(np.array(split_scan_2.T[0],dtype=np.int))  
    num_scans=len(scan_list)/float(points_per_scan)
  
    if len(scan_list) < points_per_scan:
        return "First scan not finished. Waiting until it is finished."
    

    scan_dict=dict()
    #for j in range 
    for i in range(len(scan_list)):
            scan_dict[scan_list[i]] = next(pool)
    
    open_beam_indices=[]
    sample_indices=[]
    #jump_list=["blub"]
    jump_list_2=[]
    file_id_pool=cycle(file_identifier)
    file_id_list=[]
    counter=0
    for item in scan_list:
        
        if scan_dict[item] == "D"or scan_dict[item] == "d":
            print("Dummy")
        elif scan_dict[item] == "O" or scan_dict[item] == "o" :
            if item not in jump_list_2:
                open_beam_indices.append(scan_list.index(item))
            print("Open Beam")
        elif scan_dict[item] == "S"or scan_dict[item] == "s":
            file_id=next(file_id_pool)
            sample_indices.append(scan_list.index(item))
            file_id_list.append(str(counter).zfill(3)+"_"+str(file_id))
                
            counter+=1
        
    
    first_data_list=[]
    last_data_list=[]
    first_ob_list=[]
    last_ob_list=[]
    data_inf_list=[]
    ob_inf_list=[]
    for scan in sample_indices:
        ob_index=min(open_beam_indices, key=lambda x:abs(x-scan))
        first_data_path,last_data_path,data_ips,data_nimg=generate_load_data(scan_list[scan])
        first_ob_path,last_ob_path,ob_ips,ob_nimg=generate_load_data(scan_list[ob_index])
        first_data_list.append(first_data_path)
        last_data_list.append(last_data_path)
        first_ob_list.append(first_ob_path)
        last_ob_list.append(last_ob_path)
        data_inf_list.append([data_ips,data_nimg])
        ob_inf_list.append([ob_ips,ob_nimg])
    return first_data_list,last_data_list,first_ob_list,last_ob_list,data_inf_list,ob_inf_list,file_id_list
    
    
    


        

