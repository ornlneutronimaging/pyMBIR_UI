# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 13:29:20 2016

@author: tneuwirt
"""
import xlrd
import numpy as np
import datetime
import os
from matplotlib.backends.backend_pdf import PdfPages
import configparser
from astropy.io import fits
import ast
from PIL import Image

import matplotlib.pyplot as plt
from PyQt5 import QtCore, QtGui

import logging

def load_excel(excel):
    first_data_list=[]
    last_data_list=[]
    first_ob_list=[]
    last_ob_list=[]
    first_dc_list=[]
    last_dc_list=[]
    period_list=[]
    fit_list=[]
    roi_list=[]
    gamma_dat=[]
    gamma_dat_thr1=[]
    gamma_dat_thr2=[]
    gamma_dat_thr3=[]
    gamma_dat_sig=[]
    gamma_dc=[]
    gamma_dc_thr1=[]
    gamma_dc_thr2=[]
    gamma_dc_thr3=[]
    gamma_dc_sig=[]
    result_list=[]
    file_id_list=[]
    sample_list=[]
    used_env_list=[]
    osc_pixel_list=[]
    img_per_step_list=[]
    rot_list=[]
    epi_corr_list=[]
    epi_corr_val_list=[]


    startrow = 1
    wb = xlrd.open_workbook(excel)
    sh = wb.sheet_by_index(0)
    # read first excel row
    params = dict()
    for i in range(sh.ncols):
        params[sh.row_values(0)[i]] = i
    #print params

    for i in np.arange(startrow,sh.nrows,1):#Kommentar: die erste zahl gibt die Zeile im Excel file an

        for k in params:
            #exec('try:\n\t{KEY}=int({VALUE})\nexcept ValueError as e:\n\t{KEY}={VALUE}'.format(KEY = k, VALUE = repr(sh.row_values(i)[params[k]])))
            KEY=k
            #VALUE = repr(sh.row_values(i)[params[k]])
            VALUE = sh.row_values(i)[params[k]]
            #print sh.row_values(i)[params[k]]

            if str(k) == "first_data_file":
                #print VALUE
                first_data_list.append(str(VALUE))
            elif str(k) == "last_data_file":
                #print VALUE
                last_data_list.append(str(VALUE))
            elif str(k) == "first_ob_file":
                first_ob_list.append(str(VALUE))
                #print "blub"
            elif str(k) == "last_ob_file":
                last_ob_list.append(str(VALUE))
                #print "blub"
            elif str(k) == "first_dc_file":
                first_dc_list.append(str(VALUE))
            elif str(k) == "last_dc_file":
                last_dc_list.append(str(VALUE))

            elif str(k) == "period":
                period_list.append(str(VALUE))
            elif str(k) == "fit_procedure":
                fit_list.append(str(VALUE))
            elif str(k) == "roi":
                roi_list.append(str(VALUE))

            elif str(k) == "gamma_filter_data/ob":
                gamma_dat.append(str(VALUE))
            elif str(k) == "data_threshold_3x3":
                gamma_dat_thr1.append(str(VALUE))
            elif str(k) == "data_threshold_5x5":
                gamma_dat_thr2.append(str(VALUE))
            elif str(k) == "data_threshold_7x7":
                gamma_dat_thr3.append(str(VALUE))
            elif str(k) == "data_sigma_log":
                gamma_dat_sig.append(str(VALUE))

            elif str(k) == "gamma_filter_dc":
                gamma_dc.append(str(VALUE))
            elif str(k) == "dc_threshold_3x3":
                gamma_dc_thr1.append(str(VALUE))
            elif str(k) == "dc_threshold_5x5":
                gamma_dc_thr2.append(str(VALUE))
            elif str(k) == "dc_threshold_7x7":
                gamma_dc_thr3.append(str(VALUE))
            elif str(k) == "dc_sigma_log":
                gamma_dc_sig.append(str(VALUE))

            elif str(k) == "result_directory":
                result_list.append(str(VALUE))
            elif str(k) == "file_id":
                file_id_list.append(str(VALUE))
            elif str(k) == "sample_information":
                sample_list.append(str(VALUE))
            elif str(k) == "used_environment":
                used_env_list.append(str(VALUE))
            elif str(k) == "osc_pixel":
                osc_pixel_list.append(str(VALUE))
            elif str(k) == "images_per_step":
                img_per_step_list.append(str(VALUE))
            elif str(k) == "rotation":
                rot_list.append(str(VALUE))
            elif str(k) == "dc_outlier_removal":
                epi_corr_list.append(str(VALUE))
            elif str(k) == "dc_outlier_value":
                epi_corr_val_list.append(str(VALUE))
                #print bla


    return first_data_list,last_data_list,first_ob_list,last_ob_list,first_dc_list,last_dc_list,period_list,fit_list,roi_list,gamma_dat,gamma_dat_thr1,gamma_dat_thr2,gamma_dat_thr3,gamma_dat_sig,gamma_dc,gamma_dc_thr1,gamma_dc_thr2,gamma_dc_thr3,gamma_dc_sig,result_list,file_id_list,sample_list,used_env_list,osc_pixel_list,img_per_step_list,rot_list,epi_corr_list,epi_corr_val_list

def save_oscillation(result_dir,osc_plot,osc_data,osc_para_data,osc_para_ob,data_files,ob_files,dc_files,pixel,roi_list,file_id):
    #print osc_plot
    data_path=data_files[0][0:data_files[0].rfind(str(os.path.sep))]
    ob_path=ob_files[0][0:ob_files[0].rfind(str(os.path.sep))]
    dc_path=dc_files[0][0:dc_files[0].rfind(str(os.path.sep))]

    for i in range (0,len(data_files)):
        temp_ind_dat=data_files[i].rfind(str(os.path.sep))
        temp_ind_ob=ob_files[i].rfind(str(os.path.sep))
        data_files[i]=data_files[i][temp_ind_dat:]
        ob_files[i]=ob_files[i][temp_ind_ob:]
    for i in range (0,len(dc_files)):
        temp_ind_dc=dc_files[i].rfind(str(os.path.sep))
        dc_files[i]=dc_files[i][temp_ind_dc:]
    x_pixel=int(pixel[0]+roi_list[2])
    y_pixel=int(pixel[1]+roi_list[0])

    date = datetime.datetime.now()
    date = date.strftime("%Y-%m-%d %H:%M")
    osc_file = open(str(result_dir)+"Data_Oscillation ("+str(file_id)+") Pixel("+str(pixel[0])+", "+str(pixel[1])+").txt","w")

    osc_file.write("#### Header ####")
    osc_file.write("\n")
    osc_file.write("# "+date)
    osc_file.write("\n")
    osc_file.write("# Data Path:"+str(data_path))
    osc_file.write("\n")
    osc_file.write("# Data Files:"+str(data_files))
    osc_file.write("\n")
    osc_file.write("# OB Path:"+str(ob_path))
    osc_file.write("\n")
    osc_file.write("# OB Files:"+str(ob_files))
    osc_file.write("\n")
    osc_file.write("# DC Path:"+str(dc_path))
    osc_file.write("\n")
    osc_file.write("# DC Files:"+str(dc_files))
    osc_file.write("\n")
    osc_file.write("# Pixel in Raw Image: ("+str(x_pixel)+","+str(y_pixel)+")")
    osc_file.write("\n")
    osc_file.write("# Pixel in Processed Image: ("+str(pixel[0])+","+str(pixel[1])+")")
    osc_file.write("\n")
    osc_file.write("# Data Parameter: a0= "+str(np.around(osc_para_data[0][int(pixel[1])][int(pixel[0])],2))+" a1= "+str(np.around(osc_para_data[1][int(pixel[1])][int(pixel[0])],2))+" phi= "+str(np.around(osc_para_data[2][int(pixel[1])][int(pixel[0])],2)))
    osc_file.write("\n")
    osc_file.write("# OB Parameter: a0="+str(np.around(osc_para_ob[0][int(pixel[1])][int(pixel[0])],2))+", a1="+str(np.around(osc_para_ob[1][int(pixel[1])][int(pixel[0])],2))+", phi="+str(np.around(osc_para_ob[2][int(pixel[1])][int(pixel[0])],2)))
    osc_file.write("\n")
    osc_file.write("\n")
    osc_file.write("#### Data ####")
    osc_file.write("\n")
    osc_file.write("# X Position Data\t X Position OB\t Graylevel Data\t Graylevel Ob")
    osc_file.write("\n")
    for i in range(0,len(osc_data[0])):
        osc_file.write(str(osc_data[0][i])+"\t\t"+str(osc_data[1][i])+"\t\t"+str(osc_data[2][i])+"\t\t"+str(osc_data[3][i]))
        osc_file.write("\n")
    osc_file.close()
    pdf_file=PdfPages(str(result_dir)+"Plot_Oscillation ("+str(file_id)+") Pixel("+str(pixel[0])+", "+str(pixel[1])+").pdf")
    pdf_file.savefig(osc_plot,dpi=200)
    meta=pdf_file.infodict()
    meta['Title']=str(result_dir)+"Plot_Oscillation_Pixel("+str(pixel[0])+", "+str(pixel[1])+").pdf"
    meta['Author']="ANGEL"
    """
    meta['Date']=date
    meta['Data Path']=str(data_path)
    meta['OB Path']=str(ob_path)
    meta['DC Path']=str(dc_path)
    meta['Data Files']=str(data_files)
    meta['OB Files']=str(ob_files)
    meta['DC Files']=str(dc_files)
    meta['Pixel']="("+str(x_pixel)+","+str(y_pixel)+")"
    meta['Data Parameter']="a0= "+str(np.around(osc_para_data[0][pixel[1]][pixel[0]],2))+" a1= "+str(np.around(osc_para_data[1][pixel[1]][pixel[0]],2))+" phi= "+str(np.around(osc_para_data[2][pixel[1]][pixel[0]],2))
    meta['OB Parameter']="a0="+str(np.around(osc_para_ob[0][pixel[1]][pixel[0]],2))+", a1="+str(np.around(osc_para_ob[1][pixel[1]][pixel[0]],2))+", phi="+str(np.around(osc_para_ob[2][pixel[1]][pixel[0]],2))
    """

    pdf_file.close()
def save_line(result_dir,sender,line_plot,z_list,dist_list,pix_list,data_files,ob_files,dc_files,roi_list,file_id):
    #print line_plot
    data_path=data_files[0][0:data_files[0].rfind(str(os.path.sep))]
    ob_path=ob_files[0][0:ob_files[0].rfind(str(os.path.sep))]
    dc_path=dc_files[0][0:dc_files[0].rfind(str(os.path.sep))]

    for i in range (0,len(data_files)):
        temp_ind_dat=data_files[i].rfind(str(os.path.sep))
        temp_ind_ob=ob_files[i].rfind(str(os.path.sep))
        data_files[i]=data_files[i][temp_ind_dat:]
        ob_files[i]=ob_files[i][temp_ind_ob:]
    for i in range (0,len(dc_files)):
        temp_ind_dc=dc_files[i].rfind(str(os.path.sep))
        dc_files[i]=dc_files[i][temp_ind_dc:]
    x1_pixel=pix_list[0]+roi_list[2]
    y1_pixel=pix_list[1]+roi_list[0]
    x2_pixel=pix_list[2]+roi_list[2]
    y2_pixel=pix_list[3]+roi_list[0]

    date = datetime.datetime.now()
    date = date.strftime("%Y-%m-%d %H:%M")
    
    line_file = open(str(result_dir)+str(sender)+"_Line_Profile ("+str(file_id)+") Pixel("+str(int(np.around(x1_pixel)))+", "+str(int(np.around(y1_pixel)))+" to "+str(int(np.around(x2_pixel)))+", "+str(int(np.around(y2_pixel)))+").txt","w")

    line_file.write("#### Header ####")
    line_file.write("\n")
    line_file.write("# "+date)
    line_file.write("\n")
    line_file.write("# Data Path:"+str(data_path))
    line_file.write("\n")
    line_file.write("# Data Files:"+str(data_files))
    line_file.write("\n")
    line_file.write("# OB Path:"+str(ob_path))
    line_file.write("\n")
    line_file.write("# OB Files:"+str(ob_files))
    line_file.write("\n")
    line_file.write("# DC Path:"+str(dc_path))
    line_file.write("\n")
    line_file.write("# DC Files:"+str(dc_files))
    line_file.write("\n")
    line_file.write("# Pixel in Raw Image: ("+str(int(np.around(x1_pixel)))+", "+str(int(np.around(y1_pixel)))+" to "+str(int(np.around(x2_pixel)))+", "+str(int(np.around(y2_pixel)))+")")
    line_file.write("\n")
    line_file.write("# Pixel in Processed Image: ("+str(int(np.around(x1_pixel)))+", "+str(int(np.around(y1_pixel)))+" to "+str(int(np.around(x2_pixel)))+", "+str(int(np.around(y2_pixel)))+")")
    line_file.write("\n")
    line_file.write("#### Data ####")
    line_file.write("\n")
    line_file.write("# Distance\t Grayvalue")
    line_file.write("\n")
    for i in range(0,len(z_list)):
        line_file.write(str(dist_list[i])+"\t\t"+str(z_list[i]))
        line_file.write("\n")
    line_file.close()
    pdf_file=PdfPages(str(result_dir)+str(sender)+"_Line_Profile ("+str(file_id)+") Pixel("+str(int(np.around(x1_pixel)))+", "+str(int(np.around(y1_pixel)))+" to "+str(int(np.around(x2_pixel)))+", "+str(int(np.around(y2_pixel)))+").pdf")
    pdf_file.savefig(line_plot,dpi=200)
    meta=pdf_file.infodict()
    meta['Title']=str(result_dir)+str(sender)+"_Line_Profile_Pixel("+str(int(np.around(x1_pixel)))+", "+str(int(np.around(y1_pixel)))+" to "+str(int(np.around(x2_pixel)))+", "+str(int(np.around(y2_pixel)))+").pdf"
    meta['Author']="ANGEL"
    """
    meta['Date']=date
    meta['Data Path']=str(data_path)
    meta['OB Path']=str(ob_path)
    meta['DC Path']=str(dc_path)
    meta['Data Files']=str(data_files)
    meta['OB Files']=str(ob_files)
    meta['DC Files']=str(dc_files)
    meta['Pixel']="("+str(x_pixel)+","+str(y_pixel)+")"
    meta['Data Parameter']="a0= "+str(np.around(osc_para_data[0][pixel[1]][pixel[0]],2))+" a1= "+str(np.around(osc_para_data[1][pixel[1]][pixel[0]],2))+" phi= "+str(np.around(osc_para_data[2][pixel[1]][pixel[0]],2))
    meta['OB Parameter']="a0="+str(np.around(osc_para_ob[0][pixel[1]][pixel[0]],2))+", a1="+str(np.around(osc_para_ob[1][pixel[1]][pixel[0]],2))+", phi="+str(np.around(osc_para_ob[2][pixel[1]][pixel[0]],2))
    """

    pdf_file.close()
def save_ngi_files(result_dir,header,data,file_id):
    name=['TI','DPC','DFI','Phase_OB','Phase_Data','Visibility_Data','Visibility_OB','a0_Data','a0_OB']
    
    for i in range(9):
        hdu = fits.PrimaryHDU(data[i][::-1])
        hdulist = fits.HDUList([hdu])
        hdulist[0].header['path_dat']=(str(header[0]),'File of the data images')
        #hdulist[0].header['files_data']=(str(header[1]),'File names of the data images')
        hdulist[0].header['path_ob']=(str(header[2]),'Path of the open beam images')
        #hdulist[0].header['files_ob']=(str(header[3]),'File names of the open beam images')
        hdulist[0].header['path_dc']=(str(header[4]),'Path of the dark current images')
        #hdulist[0].header['files_dc']=(str(header[5]),'File names of the dark current images')
        hdulist[0].header['img_num']=(str(header[6]),'Number of data/OB images taken')
        hdulist[0].header['period']=(str(header[7]),'Number of periods scanned')
        hdulist[0].header['full_per']=(str(header[8]),'Full period')
        hdulist[0].header['roi_list']=(str(header[9]),'Region of Interest selected')
        hdulist[0].header['sample']=(str(header[10]),'Sample used in the experiment')
        hdulist[0].header['environ']=(str(header[11]),'Environment used in the experiment')
        hdulist[0].header['filter']=(str(header[12]),'Filter used in the processing')
        #hdulist[0].header['binning']=(header[13],'Binning of the image')
        hdulist[0].header['fit_alg']=(str(header[13]),'Fitting algorithm used')
        hdulist[0].header['rot_g0']=(str(header[14]),'Rotation of G0')
        #hdulist[0].header['fit_alg']=(header[16],'Fitting algorithm used')


        hdulist.writeto(str(result_dir) +name[i] + '_' + str(file_id) + '.fits',clobber=True)

def save_log_file(result_dir,data_files,ob_files,dc_files,instrument,sample,environment,comment,version,rot_G0,period_number,full_per,binning,bin_pix,median,median_pix,gamma_dat,gamma_dat_par,gamma_dc,gamma_dc_par,roi_list,fit,file_id):
    date = datetime.datetime.now()
    date = date.strftime("%Y-%m-%d %H:%M")
    data_path=data_files[0][0:data_files[0].rfind(str(os.path.sep))]
    ob_path=ob_files[0][0:ob_files[0].rfind(str(os.path.sep))]
    dc_path=dc_files[0][0:dc_files[0].rfind(str(os.path.sep))]
    for i in range (0,len(data_files)):
        temp_ind_dat=data_files[i].rfind(str(os.path.sep))
        temp_ind_ob=ob_files[i].rfind(str(os.path.sep))
        data_files[i]=data_files[i][temp_ind_dat:]
        ob_files[i]=ob_files[i][temp_ind_ob:]
    for i in range (0,len(dc_files)):
        temp_ind_dc=dc_files[i].rfind(str(os.path.sep))
        dc_files[i]=dc_files[i][temp_ind_dc:]

    config = configparser.SafeConfigParser()
    config.add_section("General Information")
    config.set("General Information","Instrument used",str(instrument))
    config.set("General Information","Date",str(date))
    config.set("General Information","File identifier",str(file_id))
    config.set("General Information","Sample",str(sample))
    config.set("General Information","Used Environment",str(environment))
    config.set("General Information","Comment",str(comment))
    config.set("General Information","Program Version",str(version))

    config.add_section("Raw Data Information")
    config.set("Raw Data Information","Data Path",str(data_path))
    config.set("Raw Data Information","Data Files",str(data_files))
    config.set("Raw Data Information","OB Path",str(ob_path))
    config.set("Raw Data Information","OB Files",str(ob_files))
    config.set("Raw Data Information","DC Path",str(dc_path))
    config.set("Raw Data Information","DC Files",str(dc_files))
    config.set("Raw Data Information","Number of Steps",str(len(data_files)))
    config.set("Raw Data Information","Number of Periods",str(period_number))
    config.set("Raw Data Information","Full Period",str(full_per))
    config.set("Raw Data Information","Rotation of G0",str(rot_G0))



    config.add_section("Image Processing Information")
    config.set("Image Processing Information","ROI",str(roi_list))

    config.set("Image Processing Information","Gamma Filter (Data/OB)",str(gamma_dat))
    config.set("Image Processing Information","Gamma Filter (Data/OB) Threshold 1",str(gamma_dat_par[0]))
    config.set("Image Processing Information","Gamma Filter (Data/OB) Threshold 2",str(gamma_dat_par[1]))
    config.set("Image Processing Information","Gamma Filter (Data/OB) Threshold 3",str(gamma_dat_par[2]))
    config.set("Image Processing Information","Gamma Filter (Data/OB) Sigma",str(gamma_dat_par[3]))

    config.set("Image Processing Information","Gamma Filter (DC)",str(gamma_dc))
    config.set("Image Processing Information","Gamma Filter (DC) Threshold 1",str(gamma_dc_par[0]))
    config.set("Image Processing Information","Gamma Filter (DC) Threshold 2",str(gamma_dc_par[1]))
    config.set("Image Processing Information","Gamma Filter (DC) Threshold 3",str(gamma_dc_par[2]))
    config.set("Image Processing Information","Gamma Filter (DC) Sigma",str(gamma_dc_par[3]))

    config.set("Image Processing Information","Median Filter",str(median))
    config.set("Image Processing Information","Median Filter Radius",str(median_pix))

    config.set("Image Processing Information","Binning",str(binning))
    config.set("Image Processing Information","Number of binned Pixels","("+str(bin_pix)+"x"+str(bin_pix)+")")

    config.set("Image Processing Information","Used Fit Procedure",str(fit))
    #print(file_id)
    with open(str(result_dir)+"Logbook_"+str(file_id)+".cfg", 'w') as configfile:
        config.write(configfile)
        #print "bla"


def load_log_file(path):
    #print path
    config = configparser.SafeConfigParser()
    config.read(str(path))
    #config.

    sections=config.sections()
    #print sections
    try   :
        instrument=config.get("General Information","instrument used")
        #print instrument, "bla"
        #config.get("General Information","Date")
        file_id=config.get("General Information","File identifier")
        sample=config.get("General Information","Sample")
        environment=config.get("General Information","Used Environment")
        comment=config.get("General Information","Comment")
        #config.get("General Information","Program Version")

        data_path=config.get("Raw Data Information","Data Path")
        data_files=config.get("Raw Data Information","Data Files")
        data_files=ast.literal_eval(str(data_files))
        ob_path=config.get("Raw Data Information","OB Path")
        ob_files=config.get("Raw Data Information","OB Files")
        ob_files=ast.literal_eval(str(ob_files))
        dc_path=config.get("Raw Data Information","DC Path")
        dc_files=config.get("Raw Data Information","DC Files")
        dc_files=ast.literal_eval(str(dc_files))
        number_img=config.get("Raw Data Information","Number of Steps")
        per_num=config.get("Raw Data Information","Number of Periods")
        full_per=config.getboolean("Raw Data Information","Full Period")
        rot=config.get("Raw Data Information","Rotation of G0")

        roi_list=config.get("Image Processing Information","ROI")
        roi_list=ast.literal_eval(str(roi_list))

        gamma_dat_bool=config.getboolean("Image Processing Information","Gamma Filter (Data/OB)")
        gamma_dat_thr1=config.getint("Image Processing Information","Gamma Filter (Data/OB) Threshold 1")
        gamma_dat_thr2=config.getint("Image Processing Information","Gamma Filter (Data/OB) Threshold 2")
        gamma_dat_thr3=config.getint("Image Processing Information","Gamma Filter (Data/OB) Threshold 3")
        gamma_dat_sigma=config.getfloat("Image Processing Information","Gamma Filter (Data/OB) Sigma")

        gamma_dc_bool=config.getboolean("Image Processing Information","Gamma Filter (DC)")
        gamma_dc_thr1=config.getint("Image Processing Information","Gamma Filter (DC) Threshold 1")
        gamma_dc_thr2=config.getint("Image Processing Information","Gamma Filter (DC) Threshold 2")
        gamma_dc_thr3=config.getint("Image Processing Information","Gamma Filter (DC) Threshold 3")
        gamma_dc_sigma=config.getfloat("Image Processing Information","Gamma Filter (DC) Sigma")

        median_bool=config.getboolean("Image Processing Information","Median Filter")
        median_radius=config.getint("Image Processing Information","Median Filter Radius")

        binning_bool=config.getboolean("Image Processing Information","Binning")
        binning_radius=config.get("Image Processing Information","Number of binned Pixels")
        #binning_radius=ast.literal_eval(str(binning_radius))
        binning_radius=binning_radius[1]

        fit=config.get("Image Processing Information","Used Fit Procedure")

    except configparser.NoSectionError:
        #print"blub"
        pass
    return instrument,file_id,sample,environment,comment,data_path,data_files,ob_path,ob_files,dc_path,dc_files,per_num,full_per,rot,roi_list,gamma_dat_bool,gamma_dat_thr1,gamma_dat_thr2,gamma_dat_thr3,gamma_dat_sigma,gamma_dc_bool,gamma_dc_thr1,gamma_dc_thr2,gamma_dc_thr3,gamma_dc_sigma,median_bool,median_radius,binning_bool,binning_radius,fit


def load_img_list(instrument='ANTARES', file_path=None, progressbar=None, program=None, header_para=None):

    pos_list = []
    img_list = []
    len_files = len(file_path)
    counter = 0

    if instrument == 'CG-1D':

        for file_index, file in enumerate(file_path):
            with Image.open(file) as f:
                metadata = dict(f.tag_v2)
                data = np.asarray(f)
                # data = data[::-1]    ## this is one in fits to follow imageJ convention
                img_list.append(data)
            program.progressSignal.emit([progressbar, 100*(file_index+1)/len_files])
            QtGui.QGuiApplication.processEvents()

        program.progressSignal.emit([progressbar, 0])

    else:

        for i in file_path:
            fitsobject = fits.open(i)
            try:
                fits_data = fitsobject[0].data
            except:
                fits_data = fitsobject[0].data[0]
            if header_para != None:
                try:
                    pos_list.append(getheader(i, header_para))
                except:
                    logging.error("Seems like you tried to load files which do not contain the header parameter \ "+str(header_para)+". Try using another instrument selection or check your header selection.\n")
                    #program.emit(QtCore.SIGNAL('status'),[program.error,"Error! Further information in the info tab."])
                    program.statusSignal.emit([program.error,"Loading parameter error! Further information in the info tab."])
                    return
            fitsobject.close()
            fitsobject = None
            arr = np.array(fits_data, dtype=np.uint16)
            fits_data = None
            rev_arr = arr[::-1]
            arr = None
            img_list.append(rev_arr)
            rev_arr = None
            #program.emit(QtCore.SIGNAL('progress'),[program.progressbar,100*i/len_files])
            counter += 1
            program.progressSignal.emit([progressbar, 100*counter/len_files])
            QtGui.QGuiApplication.processEvents()

    return img_list, pos_list
        
            
def getheader(datafile,parameter):
    try:
        hv=float(str(fits.getval(datafile,parameter)))#[:-3])
    except ValueError:
        hv=float(str(fits.getval(datafile,parameter))[:-3])
    return hv        
#first_data_list,last_data_list,first_ob_list,last_ob_list,first_dc_list,last_dc_list,period_list,fit_list,roi_list,gamma_dat,gamma_dat_thr1,gamma_dat_thr2,gamma_dat_thr3,gamma_dat_sig,gamma_dc,gamma_dc_thr1,gamma_dc_thr2,gamma_dc_thr3,gamma_dc_sig,result_list,file_id_list,sample_list,used_env_list=load_excel(path)
#print int(float(gamma_dat_thr1[0]))