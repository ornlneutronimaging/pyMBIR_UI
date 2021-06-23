# -*- coding: iso-8859-1 -*-

import os
import datetime
import glob
import sys
import random
import ast
import time
import logging
import multiprocessing

import configparser
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from matplotlib import rcParams
#import FileDialog
from astropy.io import fits
from scipy.ndimage import filters,map_coordinates

from roiselector import RoiSelectorDialog as rsd

from .guiresources.matplotlibwidget import MatplotlibWidget, Preview, ROI, Filter_Preview, LINE
from .guiresources import gui_setup
#import ngI_tool.easyProc.helper
from .ngI_tool import ngItool as ngI
#import ngI_tool.ddfSetupProcessing.HarmonicAnalysis.lsqprocessing as dpcprocess

from .utility_backend import multi_logger as ml
from .guiresources import newcolormaps as nmap
from .utility_backend.gam_rem_adp_log.gam_rem_adp_log import gam_rem_adp_log as holy_grail
from .utility_backend.multicore_filtering import filter_image as fast_grail
from .utility_backend import save_load_backend as salo
#from utility_backend.pool_ext import Pool_win,Process
from .utility_backend.epithermal_correction import epithermal_correction
from .utility_backend import multi_calc_extension as mc

# Get the program version from versioneer
from .__init__ import __version__

rcParams['font.size'] = 9

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)
        
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# __version__= "0.98_indev"

def main(args):
    app = QtWidgets.QApplication(args)
    app.setStyle('Fusion')
    app.aboutToQuit.connect(cleanUp)
    app.setOrganizationName("ANTARES")
    window = ANGELMain()
    window.show()
    sys.exit(app.exec_())








def cleanUp():
  
    app = QtWidgets.QApplication.instance()
    app.closeAllWindows()
    




class ANGELMain(QtWidgets.QMainWindow):
    """
    ANGELMain: Main class of the GUI.
    """
    statusSignal = QtCore.pyqtSignal(list)
    progressSignal = QtCore.pyqtSignal(list)
    setvalueSignal = QtCore.pyqtSignal(list)
    settextSignal = QtCore.pyqtSignal(list)
    setcomboSignal = QtCore.pyqtSignal(list)
    setboolSignal = QtCore.pyqtSignal(list)
    setindexSignal = QtCore.pyqtSignal(list)
    callfuncSignal = QtCore.pyqtSignal(list)
    
    def __init__(self, parent=None):
        super(ANGELMain, self).__init__(parent)

        #sys.stdout = self.logging = Logger()
        #sys.stderr = Logger_err()
        #sys.stdout = Logger()

        gui_setup._setupUI(self, __version__)
        self._setup_signals()
        self._setup_general_variable()
    def _setup_signals(self):
        
        self.statusSignal.connect(self.status_change)
        self.progressSignal.connect(self.progress_change)
        self.setvalueSignal.connect(self.set_value)
        self.settextSignal.connect(self.set_text)
        self.setcomboSignal.connect(self.set_combo)
        self.setboolSignal.connect(self.set_bool)
        self.setindexSignal.connect(self.set_index)
        self.callfuncSignal.connect(self.call_func)
        
        #ANGELMain.connect(ANGELMain,QtCore.SIGNAL('status'),ANGELMain.status_change)
        #ANGELMain.connect(ANGELMain,QtCore.SIGNAL('progress'),ANGELMain.progress_change)
        #ANGELMain.connect(ANGELMain,QtCore.SIGNAL('filtered'),ANGELMain.multi_progress) Keine Ahnung wofür ich das Signal gedacht hab
    
        #ANGELMain.connect(ANGELMain,QtCore.SIGNAL('set_value'),ANGELMain.set_value)
        #ANGELMain.connect(ANGELMain,QtCore.SIGNAL('set_text'),ANGELMain.set_text)
        #ANGELMain.connect(ANGELMain,QtCore.SIGNAL('set_combo'),ANGELMain.set_combo)
        #ANGELMain.connect(ANGELMain,QtCore.SIGNAL('set_bool'),ANGELMain.set_bool)
        #ANGELMain.connect(ANGELMain,QtCore.SIGNAL('set_index'),ANGELMain.set_index)
        #ANGELMain.connect(ANGELMain,QtCore.SIGNAL('call_func'),ANGELMain.call_func)

   
    """
    def log_info(self,message):
        self.log_plainText.append(message)
    def log_err(self,message):
        self.err_plainText.append(message)
    """
    def _setup_general_variable(self):
#==============================================================================
#       _setup_general_variable: Initialization of some general variables. 
#                   Currently mainly used for the processing test part. self.test_filter()
#==============================================================================        
        self.test_name_list = []
        self.test_img_list = []
        self.test_img_filtered_list = []
        self.test_para_list = []
        self.filter_img=Filter_Preview("Processing Preview",self)
    def update_roi(self,roi_list):
#==============================================================================
#       update_roi: Called by self.preview_img when a roi is choosen in the Preview Widget,
#                   also called when the data set is loaded.
#                   This function is responsible for updating self.roi_list and self.roi_LineEdit in the parameter tab.
#==============================================================================
        self.roi_LineEdit.setText(str(roi_list))
        self.roi_list=roi_list
        self.roi_LineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[0-9_\\[\\]\\,]{0,255}")))
    def update_norm_roi(self,roi_list):
#==============================================================================
#       update_norm_roi:    Called by self.preview_img when a norm_roi is choosen in the Preview Widget.
#
#                           This function is responsible for updating self.norm_roi_list.
#==============================================================================
        self.norm_roi_LineEdit.setText(str(roi_list))
        self.norm_roi_list=roi_list
        self.norm_roi_LineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[0-9_\\[\\]\\,]{0,255}")))

    def update_para(self):
#==============================================================================
#       update_para:        Called when a parameter in the img_pro_tab or the start tab is changed.
#
#                           Updates the corresponding parameters in the parameter_tab.
#                           To do: Add epithermal correction        
#==============================================================================
        self.fit_Combo.setText(self.choose_fit_Combo.currentText())
        if self.grail_filt_dat_CheckBox.isChecked()==True:
            self.par_grail_filt_dat_Combo.setCurrentIndex(1)
        else:
            self.par_grail_filt_dat_Combo.setCurrentIndex(0)

        if self.grail_filt_dc_CheckBox.isChecked()==True:
            self.par_grail_filt_dc_Combo.setCurrentIndex(1)
        else:
            self.par_grail_filt_dc_Combo.setCurrentIndex(0)


        self.par_grail_filt_dat_thr1_SpinBox.setValue(self.grail_filt_dat_thr1_SpinBox.value())
        self.par_grail_filt_dat_thr2_SpinBox.setValue(self.grail_filt_dat_thr2_SpinBox.value())
        self.par_grail_filt_dat_thr3_SpinBox.setValue(self.grail_filt_dat_thr3_SpinBox.value())
        self.par_grail_filt_dat_sigma_DSpinBox.setValue(self.grail_filt_dat_sigma_DSpinBox.value())

        self.par_grail_filt_dc_thr1_SpinBox.setValue(self.grail_filt_dc_thr1_SpinBox.value())
        self.par_grail_filt_dc_thr2_SpinBox.setValue(self.grail_filt_dc_thr2_SpinBox.value())
        self.par_grail_filt_dc_thr3_SpinBox.setValue(self.grail_filt_dc_thr3_SpinBox.value())
        self.par_grail_filt_dc_sigma_DSpinBox.setValue(self.grail_filt_dc_sigma_DSpinBox.value())

        if self.bin_CheckBox.isChecked()==True:
            self.par_bin_Combo.setCurrentIndex(1)
        else:
            self.par_bin_Combo.setCurrentIndex(0)

        self.par_bin_SpinBox.setValue(self.bin_SpinBox.value())
        if self.median2_CheckBox.isChecked()==True:
            self.par_median_Combo.setCurrentIndex(1)
        else:
            self.par_median_Combo.setCurrentIndex(0)

        self.par_median_SpinBox.setValue(self.median2_SpinBox.value())
        self.par_full_per_Combo.setCurrentIndex(self.full_per_Combo.currentIndex())
        self.par_per_SpinBox.setValue(self.scanned_periods_Spinbox.value())
        self.par_rot_G0rz_DSpinBox.setValue(self.rot_G0rz_DSpinbox.value())
        self.par_img_per_step_SpinBox.setValue(self.img_per_step_Spinbox.value())
    def para_lock(self):
#==============================================================================
#       para_lock:  Called by self.para_Button.
#
#                   Locks or unlocks the parameters in the parameter_tab.
#==============================================================================
        if self.para_Button.text()=="Unlock Parameters":
            para_bool=True
            self.para_Button.setText("Lock Parameters")
        elif self.para_Button.text()=="Lock Parameters":
            para_bool=False
            self.para_Button.setText("Unlock Parameters")
        self.im_num_SpinBox.setEnabled(para_bool)
        self.ob_num_SpinBox.setEnabled(para_bool)
        self.dc_num_SpinBox.setEnabled(para_bool)
        self.im_pat_LineEdit.setEnabled(para_bool)
        self.ob_pat_LineEdit.setEnabled(para_bool)
        self.dc_pat_LineEdit.setEnabled(para_bool)
        self.im_first_LineEdit.setEnabled(para_bool)
        self.ob_first_LineEdit.setEnabled(para_bool)
        self.dc_first_LineEdit.setEnabled(para_bool)
        self.im_last_LineEdit.setEnabled(para_bool)
        self.ob_last_LineEdit.setEnabled(para_bool)
        self.dc_last_LineEdit.setEnabled(para_bool)
        self.par_per_SpinBox.setEnabled(para_bool)
        self.par_full_per_Combo.setEnabled(para_bool)
        self.par_rot_G0rz_DSpinBox.setEnabled(para_bool)
        self.fit_Combo.setEnabled(para_bool)
        self.par_bin_Combo.setEnabled(para_bool)
        self.par_bin_SpinBox.setEnabled(para_bool)
        self.par_median_Combo.setEnabled(para_bool)
        self.par_median_SpinBox.setEnabled(para_bool)
        self.par_grail_filt_dat_Combo.setEnabled(para_bool)
        self.par_grail_filt_dat_thr1_SpinBox.setEnabled(para_bool)
        self.par_grail_filt_dat_thr2_SpinBox.setEnabled(para_bool)
        self.par_grail_filt_dat_thr3_SpinBox.setEnabled(para_bool)
        self.par_grail_filt_dat_sigma_DSpinBox.setEnabled(para_bool)
        self.par_grail_filt_dc_Combo.setEnabled(para_bool)
        self.par_grail_filt_dc_thr1_SpinBox.setEnabled(para_bool)
        self.par_grail_filt_dc_thr2_SpinBox.setEnabled(para_bool)
        self.par_grail_filt_dc_thr3_SpinBox.setEnabled(para_bool)
        self.par_grail_filt_dc_sigma_DSpinBox.setEnabled(para_bool)
        self.roi_LineEdit.setEnabled(para_bool)
        self.norm_roi_LineEdit.setEnabled(para_bool)
        self.par_img_per_step_SpinBox.setEnabled(para_bool)

    def chose_directory(self):
#==============================================================================
#       chose_directory:    Called by self.data_dir_Button, self.ob_dir_Button, self.dc_dir_Button or  self.result_dir_Button.
#
#                           Opens a file dialog to choose the directory in which the data, ob or dc files are,
#                           shows the directoy in self.data_dir_lineEdit, self.ob_dir_lineEdit or self.dc_dir_lineEdit.
#                           Then grabs all the fits files in this directory and shows the path of the first and last fits file in a combo box.
#                           Also Enables the respective load buttons.
#                           If the caller is self.result_dir_Button it will only write the directory in self.result_dir_lineEdit.
#==============================================================================

        fname = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory', self.homepath)
        fname = fname.replace('/', str(os.path.sep))
        if len(fname) is not 0:
            self.homepath = os.path.dirname(fname)
      
        sender = self.sender()

        instrument_selected = str(self.instrument_Combo.currentText())
        self.instrument_selected = instrument_selected
        extension = "*.fits"
        if instrument_selected == "CG-1D":
            extension = '*.tif*'

        if len(fname) is not 0:
            if sender == self.data_dir_Button:
                self.first_data_file_Combo.clear()
                self.last_data_file_Combo.clear()
                self.img_pro_Combo.clear()
                self.data_dir_lineEdit.setText(str(fname)+str(os.path.sep))
                self.data_list = glob.glob(str(self.data_dir_lineEdit.text()) + extension)
                self.data_list.sort()

                self.first_data_file_Combo.addItems(self.data_list)
                self.last_data_file_Combo.addItems(self.data_list)
                self.img_pro_Combo.addItems(self.data_list)
                self.last_data_file_Combo.setCurrentIndex(self.last_data_file_Combo.count()-1)
                self.load_data_Button.setEnabled(True)
                self.data_progressBar.setValue(0)

            elif sender == self.dc_dir_Button:
                self.first_dc_file_Combo.clear()
                self.last_dc_file_Combo.clear()
                self.dc_dir_lineEdit.setText(str(fname)+str(os.path.sep))

                self.dc_list=glob.glob(str(self.dc_dir_lineEdit.text()) + extension)
                self.dc_list.sort()
                self.first_dc_file_Combo.addItems(self.dc_list)
                self.last_dc_file_Combo.addItems(self.dc_list)
                self.last_dc_file_Combo.setCurrentIndex(self.last_dc_file_Combo.count()-1)
                self.load_dc_Button.setEnabled(True)
                self.dc_progressBar.setValue(0)

            elif sender == self.ob_dir_Button:
                self.first_ob_file_Combo.clear()
                self.last_ob_file_Combo.clear()
                self.ob_dir_lineEdit.setText(str(fname)+str(os.path.sep))
                self.ob_list=glob.glob(str(self.ob_dir_lineEdit.text()) + extension)
                self.ob_list.sort()
                self.first_ob_file_Combo.addItems(self.ob_list)
                self.last_ob_file_Combo.addItems(self.ob_list)
                self.last_ob_file_Combo.setCurrentIndex(self.last_ob_file_Combo.count()-1)
                self.load_ob_Button.setEnabled(True)
                self.ob_progressBar.setValue(0)

            elif sender == self.result_dir_Button:
                self.result_dir_lineEdit.setText(str(fname)+str(os.path.sep))

    def load_img_files(self,multi_load=None):
#==============================================================================
#       load_img_files:     Called by self.load_data_Button, self.load_ob_Button or self.load_dc_Button.
#
#                           Loads the files which are choosen by the user. Depending on which Instrument has been used in the measurement
#                           it will use different load routines. When ANTARES data is loaded it will also load the absolute grating position.
#                           Also sets the roi to the whole image, and updates the path parameters in the parameter_tab.
#                           Loading is performed by the save_load_backend.
#                           When dark image files are loaded it will also do different things depending on how many di files are loaded.
#==============================================================================
        #Setting of the header parameter to analyze for the stepped grating position

        instrument = str(self.instrument_Combo.currentText())
        header_para = None
        if instrument == "ANTARES":
            header_para = "G1tx/value"

        #Helper value for loading of multiple data sets using excel files.
        self.multi_load_fin=[False, False, False]
        if multi_load != False:
            sender = multi_load
        else:  
            sender = self.sender()

        #Data loading
        if sender == self.load_data_Button:

            self.statusSignal.emit([self.working, "Loading Data Files"])
            logging.info("Loading Data Files\n") 
            self.preview_data_Button.setEnabled(False)
            try:
                from_file = str(self.first_data_file_Combo.currentText())
                to_file = str(self.last_data_file_Combo.currentText())

                from_file_index = self.data_list.index(from_file)
                to_file_index = self.data_list.index(to_file) + 1

                self.load_data_list = self.data_list[from_file_index: to_file_index]

            except ValueError:

                logging.error("List of data images was empty. Try to select a folder which contains fits images.")
                self.statusSignal.emit([self.error, "Files not found! Further information in the info tab."])
                return

            # loading files
            self.data_img_list , self.data_pos_list = salo.load_img_list(instrument=self.instrument_selected,
                                                                         file_path=self.load_data_list,
                                                                         progressbar=self.data_progressBar,
                                                                         program=self,
                                                                         header_para=header_para)

            #Resets evaluated roi to maximum image size in case the new image is smaller than the previous loaded ones.
            roi_y1, roi_x1 = self.data_img_list[0].shape
            if self.roi_list[1] > roi_y1 or self.roi_list[3] > roi_x1 or self.roi_list[1] ==0:
                self.roi_list=[0,int(roi_y1),0,int(roi_x1)]
            
            #Updates the GUI
            self.preview_data_Button.setEnabled(True)
            self.preview_filter_Button.setEnabled(True)
            self.roi_LineEdit.setText(str(self.roi_list))
            self.im_num_SpinBox.setValue(len(self.load_data_list))
            self.im_first_LineEdit.setText(str(self.first_data_file_Combo.currentText()))
            self.im_last_LineEdit.setText(str(self.last_data_file_Combo.currentText()))
            self.im_pat_LineEdit.setText(str(self.data_dir_lineEdit.text()))
            #Sends the loaded data images names to the preview widget for display. Widget grabs the data from the main window.
            #self.preview_img.add_data(self.load_data_list,self.data_img_list,self.roi_list)
            self.preview_img.add_data(self.load_data_list, 1, self.roi_list)
            logging.info("Finished loading " + str(len(self.load_data_list)) + " Data Files \n")
            self.choose_test_image()
            self.multi_load_fin = [True, False, False]

        elif sender == self.load_ob_Button:
            #OB loading
            self.statusSignal.emit([self.working, "Loading OB Files"])
            logging.info("Loading OB Files\n")
            self.preview_ob_Button.setEnabled(False)
            try:
                from_file = str(self.first_ob_file_Combo.currentText())
                to_file = str(self.last_ob_file_Combo.currentText())

                from_file_index = self.ob_list.index(from_file)
                to_file_index = self.ob_list.index(to_file) + 1

                self.load_ob_list = self.ob_list[from_file_index: to_file_index]

            except ValueError:

                logging.error("List of OB images was empty. Try to select a folder which contains fits images.")
                self.statusSignal.emit([self.error, "Error! Further information in the info tab."])
                return

            self.ob_img_list , self.ob_pos_list = salo.load_img_list(instrument=self.instrument_selected,
                                                                     file_path=self.load_ob_list,
                                                                     progressbar=self.ob_progressBar,
                                                                     program=self,
                                                                     header_para=header_para)
            
            #Updates the GUI
            self.preview_ob_Button.setEnabled(True)
            self.ob_num_SpinBox.setValue(len(self.load_ob_list))
            self.ob_first_LineEdit.setText(str(self.first_ob_file_Combo.currentText()))
            self.ob_last_LineEdit.setText(str(self.last_ob_file_Combo.currentText()))
            self.ob_pat_LineEdit.setText(str(self.ob_dir_lineEdit.text()))
            
            #Sends the loaded ob images names to the preview widget for display. Widget grabs the data from the main window.
            self.preview_img.add_ob(self.load_ob_list, 1)
            logging.info("Finished loading " + str(len(self.load_ob_list))+" OB Files \n")
            
            self.multi_load_fin = [True, True, False]

        elif sender == self.load_dc_Button:

            #DC loading
            self.statusSignal.emit([self.working, "Loading DI Files"])
            logging.info("Loading DI Files\n")
            self.preview_dc_Button.setEnabled(False)
            try:

                from_file = str(self.first_dc_file_Combo.currentText())
                to_file = str(self.last_dc_file_Combo.currentText())

                from_file_index = self.dc_list.index(from_file)
                to_file_index = self.dc_list.index(to_file) + 1

                self.load_dc_list = self.dc_list[from_file_index: to_file_index]

            except ValueError:

                logging.error("List of DI images was empty. Try to select a folder which contains fits images.")
                self.statusSignal.emit([self.error,"Error! Further information in the info tab."])
                return
            
            self.dc_img_list , self.dc_pos_list = salo.load_img_list(instrument=self.instrument_selected,
                                                                     file_path=self.load_dc_list,
                                                                     progressbar=self.dc_progressBar,
                                                                     program=self,
                                                                     header_para=header_para)
            
            #Updates the GUI
            self.dc_median=np.median(self.dc_img_list,axis=0)
            self.preview_dc_Button.setEnabled(True)
            self.dc_num_SpinBox.setValue(len(self.dc_img_list))
            self.dc_first_LineEdit.setText(str(self.first_dc_file_Combo.currentText()))
            self.dc_last_LineEdit.setText(str(self.last_dc_file_Combo.currentText()))
            self.dc_pat_LineEdit.setText(str(self.dc_dir_lineEdit.text()))

            #Sends the loaded dc images names to the preview widget for display. Widget grabs the data from the main window.
            self.preview_img.add_dc(self.load_dc_list, 1, self.dc_median)
            logging.info("Finished loading and handling " + str(len(self.load_dc_list))+" DC Files. \n")
            self.multi_load_fin=[True, True, True]

        self.statusBar().setStyleSheet(self.ready)
        self.statusBar().showMessage("Ready")

    def choose_test_image(self):
        if self.img_type_pro_Combo.currentText() == "Data Images":
            self.img_pro_Combo.clear()
            try:
                self.img_pro_Combo.addItems(self.load_data_list)
            except AttributeError:
                logging.error("List of data images was empty. Try to select a folder which contains fits images, or load the data images.")
                self.statusSignal.emit([self.error,"Error! Couldn't find data images."])
        elif self.img_type_pro_Combo.currentText() == "OB Images":
            self.img_pro_Combo.clear()
            try:
                self.img_pro_Combo.addItems(self.load_ob_list)
            except AttributeError:
                logging.error("List of OB images was empty. Try to select a folder which contains fits images, or load the OB images.")
                self.statusSignal.emit([self.error,"Error! Couldn't find OB images."])
        elif self.img_type_pro_Combo.currentText() == "DI Images":
            self.img_pro_Combo.clear()
            try:
                self.img_pro_Combo.addItems(self.load_dc_list)
            except AttributeError:
                logging.error("List of DI images was empty. Try to select a folder which contains fits images, or load the DI images.")
                self.statusSignal.emit([self.error,"Error! Couldn't find DI images."])

    def set_roi(self):
#==============================================================================
#       set_roi:    Called by roi_Button.
#
#                   Calls the RoiselectorDialog from the roiselector package. 
#                   Returns both the ROI (always) as well as the Norm ROI (only if selected by the nroi_CheckBox).
#                   ROIs are currently always given as the bounds of the ROI chosen in the selector.
#                   The image is choosen by self.img_pro_Combo.   
#==============================================================================
        if self.img_type_pro_Combo.currentText() == "Data Images":
            # try:
            img = self.data_img_list[self.load_data_list.index(str(self.img_pro_Combo.currentText()))]
            # except:
            #     logging.error("No data images found. Please load data images or choose other images.")
            #     self.statusSignal.emit([self.error,"No data images found."])
            #     return

        elif self.img_type_pro_Combo.currentText() == "OB Images":   
            img = self.ob_img_list[self.load_ob_list.index(str(self.img_pro_Combo.currentText()))]

        elif self.img_type_pro_Combo.currentText() == "DI Images":
            img = self.dc_img_list[self.load_dc_list.index(str(self.img_pro_Combo.currentText()))]

        roidialog = rsd(image=img,tags=['ROI','Norm ROI'],standalone=False)
        roidialog.show()
        if roidialog.exec_():
            roi = roidialog.get_roi()
            roi_w = roi.get_windows(tags='ROI')
            nroi_w = roi.get_windows(tags='Norm ROI')

            if len(roi_w) == 0:
                logging.error("No ROI window with the ROI tag defined.Please use the 'ROI' tag during the creation of the ROI")
                self.statusSignal.emit([self.error,"No ROI window with the 'ROI' tag defined"]) 
            elif len(roi_w) == 1:
                roi_bounds = roi_w[0].get_bounds()
                temp_roi = [int(roi_bounds[2]), int(roi_bounds[3]), int(roi_bounds[0]), int(roi_bounds[1])]
                logging.info("ROI has been set to: "+str(temp_roi))
                self.statusSignal.emit([self.ready,"ROI has been set to: "+str(temp_roi)])
                self.callfuncSignal.emit([self.update_roi,temp_roi])
            elif len(roi_w) > 1:
                temp_roi=[0, 0, 0, 0]
                for i in roi_w:
                    roi_bounds = i.get_bounds()
                    temp_roi[0]=int(min([temp_roi[0], roi_bounds[2]]))
                    temp_roi[1]=int(max([temp_roi[1], roi_bounds[3]]))
                    temp_roi[2]=int(min([temp_roi[2], roi_bounds[0]]))
                    temp_roi[3]=int(max([temp_roi[3], roi_bounds[1]]))
                logging.info("Multiple ROI windows detected. Setting ROI to maximum bounds of all windows. ROI has been set to: "+str(temp_roi))
                self.statusSignal.emit([self.warning,"Multiple ROI windows detected. ROI has been set to: "+str(temp_roi)])
                self.callfuncSignal.emit([self.update_roi,temp_roi])



            if self.nroi_CheckBox.isChecked():
                if len(nroi_w) == 0:
                    logging.error("No Norm ROI window with the Norm ROI tag defined.Please use the 'Norm ROI' tag during the creation of the ROI")
                    self.statusSignal.emit([self.error,"No Norm ROI window with the 'Norm ROI' tag defined"]) 
                elif len(nroi_w) == 1:
                    nroi_bounds = nroi_w[0].get_bounds()
                    temp_nroi = [int(nroi_bounds[2]), int(nroi_bounds[3]), int(nroi_bounds[0]), int(nroi_bounds[1])]
                    logging.info("Norm ROI has been set to: "+str(temp_nroi))
                    self.statusSignal.emit([self.ready,"ROI has been set to: "+str(temp_nroi)])
                    self.callfuncSignal.emit([self.update_norm_roi,temp_nroi])
                elif len(nroi_w) > 1:
                    temp_nroi=[0, 0, 0, 0]
                    for i in roi_w:
                        roi_bounds = i.get_bounds()
                        temp_nroi[0]=int(min([temp_nroi[0], nroi_bounds[2]]))
                        temp_nroi[1]=int(max([temp_nroi[1], nroi_bounds[3]]))
                        temp_nroi[2]=int(min([temp_nroi[2], nroi_bounds[0]]))
                        temp_nroi[3]=int(max([temp_nroi[3], nroi_bounds[1]]))
                    logging.info("Multiple Norm ROI windows detected. Setting Norm ROI to maximum bounds of all windows. Norm ROI has been set to: "+str(temp_roi))
                    self.statusSignal.emit([self.warning,"Multiple Norm ROI windows detected. Norm ROI has been set to: "+str(temp_roi)])
                    self.callfuncSignal.emit([self.update_norm_roi,temp_nroi])
        else:
            self.statusSignal.emit([self.ready,"No ROI has been set."])
        
        #self.settextSignal.emit([self.update_roi,temp_roi])
    def test_filter(self):
#==============================================================================
#       test_filter:    Called by self.preview_filter_Button.
#
#                       Calls the Filter_Preview defined in guiresources.matplotlibwidget.
#                       Shows a preview of the image when filtered by the parameters set in the img_pro_tab.
#                       The image is choosen by self.img_pro_Combo, additionally the dark image is also filtered.
#==============================================================================
        
        #data_img_list=self.preview_img.data_list[1]
        start = time.time()
        self.statusBar().setStyleSheet(self.working)
        self.statusBar().showMessage("Testing Processing")
        
        if self.img_type_pro_Combo.currentText() == "Data Images":
            img=self.data_img_list[self.load_data_list.index(str(self.img_pro_Combo.currentText()))]
        elif self.img_type_pro_Combo.currentText() == "OB Images":   
            img=self.ob_img_list[self.load_ob_list.index(str(self.img_pro_Combo.currentText()))]
        elif self.img_type_pro_Combo.currentText() == "DI Images":   
            img=self.dc_img_list[self.load_dc_list.index(str(self.img_pro_Combo.currentText()))]
        img=img[int(self.roi_list[0]):int(self.roi_list[1]),int(self.roi_list[2]):int(self.roi_list[3])]
        test_name=str(self.img_pro_Combo.currentText())

        #filtered_img_list=[]
        #filtered_dc_list=[]
        

        #img_dc=self.test_img_dc
        
        #img_dc_raw=img_dc
        #filtered_img_list.append(img)
        #filtered_dc_list.append(img_dc)
        
        self.test_img_list.append(img)
        #self.test_name_dc=self.dc_first_LineEdit.text()

        if self.img_type_pro_Combo.currentText() == "Data Images" or self.img_type_pro_Combo.currentText() == "OB Images":
            if self.grail_filt_dat_CheckBox.isChecked():
                self.statusBar().setStyleSheet(self.working)
                self.statusBar().showMessage("Applying Gamma Filter to Data and OB images")
                img,img_para=holy_grail(img,
                                        self.grail_filt_dat_thr1_SpinBox.value(),
                                        self.grail_filt_dat_thr2_SpinBox.value(),
                                        self.grail_filt_dat_thr3_SpinBox.value(),
                                        self.grail_filt_dat_sigma_DSpinBox.value())
                test_name = test_name + " gamma (3x3 Filter: " + str(self.grail_filt_dat_thr1_SpinBox.value()) + ", " \
                            "5x5 Filter: " + str(self.grail_filt_dat_thr2_SpinBox.value()) + ", 7x7 Filter: " + \
                            str(self.grail_filt_dat_thr3_SpinBox.value()) + ", Sigma LoG: " + str(
                        self.grail_filt_dat_sigma_DSpinBox.value()) + ")"
            else:
                img_para=[0, 0, 0, 0, 0, 0]

        if self.img_type_pro_Combo.currentText() == "DI Images" :
            if self.grail_filt_dc_CheckBox.isChecked():
                self.statusBar().setStyleSheet(self.working)
                self.statusBar().showMessage("Applying Gamma Filter to Dark images")
                img,img_para=holy_grail(img,self.grail_filt_dc_thr1_SpinBox.value(),self.grail_filt_dc_thr2_SpinBox.value(),self.grail_filt_dc_thr3_SpinBox.value(),self.grail_filt_dc_sigma_DSpinBox.value())
                test_name=test_name+" gamma (3x3 Filter: "+str(self.grail_filt_dc_thr1_SpinBox.value())+", 5x5 Filter: "+str(self.grail_filt_dc_thr2_SpinBox.value())+", 7x7 Filter: "+str(self.grail_filt_dc_thr3_SpinBox.value())+", Sigma LoG: "+str(self.grail_filt_dc_sigma_DSpinBox.value())+")"
            else:
                img_para=[0, 0, 0, 0, 0, 0]

        if self.bin_CheckBox.isChecked():
            self.statusBar().setStyleSheet(self.working)
            self.statusBar().showMessage("Binning Image")
            

            img=ngI.rebin(img,self.par_bin_SpinBox.value())
            test_name=test_name+" binning ("+str(self.par_bin_SpinBox.value())+"x"+str(self.par_bin_SpinBox.value())+")"

        if self.median2_CheckBox.isChecked():
            self.statusBar().setStyleSheet(self.working)
            self.statusBar().showMessage("Applying Median Filter")
            
            img = ngI.median_filter(img,self.median2_SpinBox.value())
            test_name=test_name+" median ("+str(self.median2_SpinBox.value())+"x"+str(self.median2_SpinBox.value())+")"

        self.test_name_list.append(test_name)
        try:
            img_number=len(self.load_data_list)+len(self.load_ob_list)+len(self.load_dc_list)
        except:
            img_number=0
            logging.info("Missing image data. Full image processing time for cannot be calculated. Please load data, OB and DI for correct evaluation")
            self.statusSignal.emit([self.warning,"Missing image data. Full image processing time for cannot be calculated."])
        test_time = time.time()-start
        self.test_img_filtered_list.append(img)
        h,w = np.shape(img)

        temp=[img_para[0],
              img_para[1],
              img_para[2],
              img_para[3],
              self.grail_filt_dat_thr1_SpinBox.value(),
              self.grail_filt_dat_thr2_SpinBox.value(),
              self.grail_filt_dat_thr3_SpinBox.value(),
              self.grail_filt_dat_sigma_DSpinBox.value(),
              test_time,
              img_number,
              self.par_bin_SpinBox.value(),
              h,
              w,
              self.roi_list]
        self.test_para_list.append(temp)
           
        self.filter_img.add_filtered(self.test_name_list,self.test_img_list,self.test_img_filtered_list,self.test_para_list)

        self.statusBar().setStyleSheet(self.ready)
        self.statusBar().showMessage("Ready")
        self.filter_img.show()
        
        
        
    def status_change(self,msg):
        self.statusBar().setStyleSheet(msg[0])
        self.statusBar().showMessage(msg[1])
    def progress_change(self,progress):
        
        progress[0].setValue(progress[1])
    def multi_progress(self,filtered):
        self.progress_counter+=filtered
        #self.emit(QtCore.SIGNAL('progress'),[self.calc_progressBar,50*self.progress_counter/(2*float(self.im_num_SpinBox.value()))])
        self.progressSignal.emit([self.calc_progressBar,50*self.progress_counter/(2*float(self.im_num_SpinBox.value()))])
    def image_filtering(self,data_list,ob_list,dc_list):
#==============================================================================
#       image_filtering:    Called by self.calc_ngi.
#
#                           Filters the images depending on the parameters choosen in the parameter_tab.
#                           Returns a filtered data_list, ob_list and dc_list.
#==============================================================================
        
        
        m=self.median2_SpinBox.value()
        n=self.par_bin_SpinBox.value()
        self.progress_counter=0
        if self.grail_filt_dat_CheckBox.isChecked():
            #self.emit(QtCore.SIGNAL('status'),[self.working,"Applying Gamma Filter to Data Images"])
            self.statusSignal.emit([self.working,"Applying Gamma Filter to Data Images"])
            #self.statusBar().showMessage("Applying Gamma Filter to Data and OB Images")
            
            data_filter_params=[self.grail_filt_dat_thr1_SpinBox.value(),
                                self.grail_filt_dat_thr2_SpinBox.value(),
                                self.grail_filt_dat_thr3_SpinBox.value(),
                                self.grail_filt_dat_sigma_DSpinBox.value()]
            data_list=fast_grail(data_list,data_filter_params,self.queue)
            #self.emit(QtCore.SIGNAL('progress'),[self.calc_progressBar,25])
            self.progressSignal.emit([self.calc_progressBar,25])
            logging.info("Finished Gamma Filtering Data Images\n" )
            #for i in range
            #self.emit(QtCore.SIGNAL('status'),[self.working,"Applying Gamma Filter to OB Images"])
            self.statusSignal.emit([self.working,"Applying Gamma Filter to OB Images"])
            ob_list=fast_grail(ob_list,data_filter_params,self.queue)
            
            #self.emit(QtCore.SIGNAL('progress'),[self.calc_progressBar,50])
            self.progressSignal.emit([self.calc_progressBar,50])
            logging.info("Finished Gamma Filtering OB Images\n" )
            
            
            """
            logging.info('Gamma rem: '+ str(data_res_list[i][1])+ '  pixels substituted. '+str(data_res_list[i][1]*100.0/(data_res_list[i][2]*data_res_list[i][3]))+ '% of total pixels.\n'
                        'M3: '+str(data_res_list[i][4])+'='+str(data_res_list[i][4]*100.0/(data_res_list[i][2]*data_res_list[i][3]))+'%;  M5: '+str(data_res_list[i][5])+'='+ str(data_res_list[i][5]*100.0/(data_res_list[i][2]*data_res_list[i][3]))+'%; M7: '+str(data_res_list[i][6])+'= '+str(data_res_list[i][6]*100.0/(data_res_list[i][2]*data_res_list[i][3]))+ '% of total pixels.\n'
                        'Filtered image in '+str(data_res_list[i][7])+ 's')
            """
        
            """
            logging.info('Gamma rem: '+ str(ob_res_list[i][1])+ '  pixels substituted. '+str(ob_res_list[i][1]*100.0/(ob_res_list[i][2]*ob_res_list[i][3]))+ '% of total pixels.\n'
                        'M3: '+str(ob_res_list[i][4])+'='+str(ob_res_list[i][4]*100.0/(ob_res_list[i][2]*ob_res_list[i][3]))+'%;  M5: '+str(ob_res_list[i][5])+'='+ str(ob_res_list[i][5]*100.0/(ob_res_list[i][2]*ob_res_list[i][3]))+'%; M7: '+str(ob_res_list[i][6])+'= '+str(ob_res_list[i][6]*100.0/(ob_res_list[i][2]*ob_res_list[i][3]))+ '% of total pixels.\n'
                        'Filtered image in '+str(ob_res_list[i][7])+ 's')
            """
        for i in range(0,len(data_list)):
            
            """
            if self.grail_filt_dat_CheckBox.isChecked():
                self.statusBar().showMessage("Applying Gamma Filter to Data and OB Images")
                data_list[i]=holy_grail(data_list[i],self.grail_filt_dat_thr1_SpinBox.value(),self.grail_filt_dat_thr2_SpinBox.value(),self.grail_filt_dat_thr3_SpinBox.value(),self.grail_filt_dat_sigma_DSpinBox.value())
                ob_list[i]=holy_grail(ob_list[i],self.grail_filt_dat_thr1_SpinBox.value(),self.grail_filt_dat_thr2_SpinBox.value(),self.grail_filt_dat_thr3_SpinBox.value(),self.grail_filt_dat_sigma_DSpinBox.value())
            """
            if self.median2_CheckBox.isChecked():
                
                #self.emit(QtCore.SIGNAL('status'),[self.working,"Applying Median Filter"])
                self.statusSignal.emit([self.working,"Applying Median Filter"])
                data_list[i] = median_filter(data_list[i],m)
                ob_list[i] = median_filter(ob_list[i],m)
            if self.bin_CheckBox.isChecked():
                #self.emit(QtCore.SIGNAL('status'),[self.working,"Binning Image"])
                self.statusSignal.emit([self.working,"Binning Image"])
                data_list[i] = ngI.rebin(data_list[i],n)
                ob_list[i] = ngI.rebin(ob_list[i],n)
            #self.emit(QtCore.SIGNAL('progress'),[self.calc_progressBar,50+0.16*(100*i/(len(data_list)+1))])
            self.progressSignal.emit([self.calc_progressBar,50+0.16*(100*i/(len(data_list)+1))])
            

        if self.grail_filt_dc_CheckBox.isChecked():
            #self.emit(QtCore.SIGNAL('status'),[self.working,"Applying Gamma Filter to DI Images"])
            self.statusSignal.emit([self.working,"Applying Gamma Filter to DI Images"])
            #dc_res_list=holy_grail(dc_median,self.grail_filt_dc_thr1_SpinBox.value(),self.grail_filt_dc_thr2_SpinBox.value(),self.grail_filt_dc_thr3_SpinBox.value(),self.grail_filt_dc_sigma_DSpinBox.value())
            dc_filter_params=[self.grail_filt_dc_thr1_SpinBox.value(),self.grail_filt_dc_thr2_SpinBox.value(),self.grail_filt_dc_thr3_SpinBox.value(),self.grail_filt_dc_sigma_DSpinBox.value()]
            dc_res_list=fast_grail(dc_list,dc_filter_params,self.queue)
            """
            logging.info('Gamma rem: '+ str(dc_res_list[1])+ '  pixels substituted. '+str(dc_res_list[1]*100.0/(dc_res_list[2]*dc_res_list[3]))+ '% of total pixels.\n'
                            'M3: '+str(dc_res_list[4])+'='+str(dc_res_list[4]*100.0/(dc_res_list[2]*dc_res_list[3]))+'%;  M5: '+str(dc_res_list[5])+'='+ str(dc_res_list[5]*100.0/(dc_res_list[2]*dc_res_list[3]))+'%; M7: '+str(dc_res_list[6])+'= '+str(dc_res_list[6]*100.0/(dc_res_list[2]*dc_res_list[3]))+ '% of total pixels.\n'
                            'Filtered image in '+str(dc_res_list[7])+ 's')
            """
            #dc_median=dc_res_list[0]
            #ob_list[i]=holy_grail(ob_list[i],self.grail_filt_dat_thr1_SpinBox.value(),self.grail_filt_dat_thr2_SpinBox.value(),self.grail_filt_dat_thr3_SpinBox.value(),self.grail_filt_dat_sigma_DSpinBox.value())
        else:
            dc_res_list=dc_list
        for i in range(0,len(dc_res_list)):
            if self.median2_CheckBox.isChecked():
                #self.emit(QtCore.SIGNAL('status'),[self.working,"Applying Median Filter"])
                self.statusSignal.emit([self.working,"Applying Median Filter"])
                dc_res_list[i] = median_filter(dc_res_list[i],m)
                #ob_list[i] = median_filter(ob_list[i],m)
            if self.bin_CheckBox.isChecked():
                #self.emit(QtCore.SIGNAL('status'),[self.working,"Binning Image"])
                self.statusSignal.emit([self.working,"Binning Image"])
                dc_res_list[i] = ngI.rebin(dc_res_list[i],n)
                #ob_list[i] = ngI.binning(ob_list[i],n)
            
        #self.emit(QtCore.SIGNAL('status'),[self.working,"Fitting the Data"])
        self.statusSignal.emit([self.working,"Fitting the Data"])
        #self.emit(QtCore.SIGNAL('progress'),[self.calc_progressBar,66])
        self.progressSignal.emit([self.calc_progressBar,66])
        #time.sleep(0.5)





        #self.statusBar().showMessage("Ready")
        return data_list, ob_list, dc_res_list

        
    def epithermal_filtering(self,dc_median_list):
        dc_median_corrected=[]
        
        for i in dc_median_list:
            dc_median_corrected.append(epithermal_correction(i,self.epithermal_corr_DSpinBox.value()))
        return dc_median_corrected
    def preview_images(self):
#==============================================================================
#       preview_images:    Called by self.preview_data_Button, self.preview_ob_Button and self.preview_dc_Button.
#
#                          Shows the Preview_Widget.
#==============================================================================
        self.preview_img.show()
        self.preview_img.raise_()

    def calc_ngi_thread(self):
        if self.calc_Button.text() == "Calculate":
            """
            self.tabWidget.setCurrentIndex(8)
            self.tabWidget.setTabEnabled(0,False)
            self.tabWidget.setTabEnabled(1,False)
            self.tabWidget.setTabEnabled(2,False)
            self.tabWidget.setTabEnabled(3,False)
            self.tabWidget.setTabEnabled(4,False)
            self.tabWidget.setTabEnabled(5,False)
            self.tabWidget.setTabEnabled(6,False)
            """
            if self.multi_Checkbox.isChecked()==False:
                self.ngiThread = GenericThread(self.calc_ngi)
                #self.connect(self.ngiThread,QtCore.SIGNAL('finished'),self.ngi_calc_gui)
                self.ngiThread.finishedSignal.connect(self.ngi_calc_gui)
                self.ngiThread.start()
                self.calc_Button.setText("Abort Calculation")
            else:
                self.calc_ngi()
        elif self.calc_Button.text()=="Abort Calculation":
            if self.ngiThread.isRunning():
                self.ngiThread.terminate()
                
            self.calc_Button.setText("Calculate")
            logging.info("Calculation has been aborted by user \n")
            #self.emit(QtCore.SIGNAL('progress'),[self.calc_progressBar,0])
            self.progressSignal.emit([self.calc_progressBar,0])
        
        
        #self.genericThread


    def pre_calc_check(self):
        try:
            roi_list=ast.literal_eval(str(self.roi_LineEdit.text()))
            list_eval=True
        except:
            list_eval=False
        #try:
    def calc_ngi(self):

#==============================================================================
#       calc_ngi:   Called by self.calc_Button.
#
#                   Contains the calculation of the TI,DPCI and DFI.
#                   First crops the images down to the size of the roi.
#                   Then applies the filter choosen in the img_pro_tab.
#                   Afterwards, depending on the used instrument it will calculate the TI,DPCI and DFI according to the algorithm
#                   choosen in the img_pro_tab and draws the preview images in the calc_tab. Also enables the other tabs of the lower tab widget.
#                   Calls self.vis_analysis, self.phase_analysis, self.ti_analysis, self.dpci_analysis and self.dfi_analysis, which set up the other
#                   tabs of the lower tab widget.
#==============================================================================
        #ml.MultiProcessingHandler.stop(ml.MultiProcessingHandler("blub"))
        self.calc_state=0
        data_img_list=self.data_img_list
        ob_img_list=self.ob_img_list
        dc_img_list=self.dc_img_list
        self.before = time.time()
        logging.info("Start Calculation \n")
        #self.emit(QtCore.SIGNAL('status'),[self.working,"Calculating"])
        self.statusSignal.emit([self.working,"Calculating"])
        try:
            roi_list=ast.literal_eval(str(self.roi_LineEdit.text()))
        except SyntaxError:
            logging.error("Couldn't parse the ROI. Either no data has been loaded or while changing the ROI manually there was an mistake.")
            #self.emit(QtCore.SIGNAL('status'),[self.error,"Error! Further information in the info tab"])
            self.statusSignal.emit([self.error,"Error! Further information in the info tab"])
            
            return
        if self.instrument_Combo.currentText() == "ICON":
            norm_roi_list=ast.literal_eval(str(self.norm_roi_LineEdit.text()))
        
            
        self.roi_list=roi_list

        self.data_img_list_crop=[]
        self.ob_img_list_crop=[]
        self.dc_img_list_crop=[]

        self.data_img_list_norm=[]
        self.ob_img_list_norm=[]
        
        if self.instrument_Combo.currentText() == "ICON":

            for i in range(0,len(data_img_list)):
                self.data_img_list_norm.append( np.mean(data_img_list[i][norm_roi_list[0]:norm_roi_list[1],norm_roi_list[2]:norm_roi_list[3]]))
                self.ob_img_list_norm.append( np.mean(ob_img_list[i][norm_roi_list[0]:norm_roi_list[1],norm_roi_list[2]:norm_roi_list[3]]))
        
        for i in range(0,len(data_img_list)):
            try:
                self.data_img_list_crop.append( data_img_list[i][roi_list[0]:roi_list[1],roi_list[2]:roi_list[3]])
                self.ob_img_list_crop.append( ob_img_list[i][roi_list[0]:roi_list[1],roi_list[2]:roi_list[3]])
            except IndexError:
                logging.error("Not enough values in the list.It seems like you forgot a comma when changing the ROI by hand")
                #self.emit(QtCore.SIGNAL('status'),[self.error,"Error! Further information in the info tab"])
                self.statusSignal.emit([self.error,"Error! Further information in the info tab"])
                return
        
        for i in range(0,len(dc_img_list)):
            self.dc_img_list_crop.append(dc_img_list[i][roi_list[0]:roi_list[1],roi_list[2]:roi_list[3]])

        data_img_list=None
        ob_img_list=None
        dc_img_list=None
        self.data_img_list_filtered,self.ob_img_list_filtered,self.dc_img_list_filtered=self.image_filtering(self.data_img_list_crop,self.ob_img_list_crop,self.dc_img_list_crop)
        
        logging.info('Complete Filter time '+str(time.time()-self.before)+ ' sec \n')

        if self.epithermal_corr_CheckBox.isChecked():
            dc_median_filtered = self.epithermal_filtering(self.dc_img_list_filtered)

        else:
            dc_median_filtered = self.dc_img_list_filtered

        if len(dc_median_filtered) == 1:
            self.dc_median_filtered = dc_median_filtered[0]
            logging.info("Single DC image loaded. No further handling done.\n")

        elif len(dc_median_filtered) == 2:
            self.dc_median_filtered = np.minimum(dc_median_filtered[0], dc_median_filtered[1])
            logging.info("Two DC images loaded. Elementwise minimum of the images has been calculated.\n")
        elif len(dc_median_filtered) > 2:
            self.dc_median_filtered = np.median(dc_median_filtered, axis=0)
            logging.info("Three or more DC images loaded. Elementwise median of the images has been calculated.\n")





        self.data_img_list_crop=None
        self.ob_img_list_crop=None
        self.dc_median_crop=None
        temp_data_list=[]
        temp_ob_list=[]
        temp_data_pos_list=[]
        temp_ob_pos_list=[]
        self.data_img_list_median=[]
        self.ob_img_list_median=[]
        
        self.data_pos_list_median=[]
        self.ob_pos_list_median=[]
        temp_ind=self.par_bin_SpinBox.value()
        for i in range(0,len(self.data_img_list)):
            temp_data_list.append(self.data_img_list_filtered[i])
            temp_ob_list.append(self.ob_img_list_filtered[i])

            if self.instrument_Combo.currentText() == "ANTARES":
                temp_data_pos_list.append(self.data_pos_list[i])
                temp_ob_pos_list.append(self.ob_pos_list[i])
            if len(temp_data_list)==self.par_img_per_step_SpinBox.value():
                self.data_img_list_median.append(np.median(temp_data_list[0:temp_ind],axis=0))
                self.ob_img_list_median.append(np.median(temp_ob_list[0:temp_ind],axis=0))
                if self.instrument_Combo.currentText() == "ANTARES":
                    self.data_pos_list_median.append(np.median(temp_data_pos_list[0:temp_ind],axis=0))
                    self.ob_pos_list_median.append(np.median(temp_ob_pos_list[0:temp_ind],axis=0))
                temp_data_list=[]
                temp_ob_list=[]
                temp_data_pos_list=[]
                temp_ob_pos_list=[]

        self.data_img_list_filtered=None
        self.ob_img_list_filtered=None
        self.dc_img_list_filtered=None
        
        if self.instrument_Combo.currentText() == "ANTARES":
            self.TI, self.DPC, self.DFI, \
            self.a0_ob, self.a1_ob, self.phi_ob, \
            self.a0_data, self.a1_data, self.phi_data = \
                ngI.nGI(self.data_img_list_median,
                        self.ob_img_list_median,
                        self.dc_median_filtered,
                        self.fit_Combo.text(),
                        bool(self.par_full_per_Combo.currentText()),
                        int(self.par_per_SpinBox.value()),
                        self.data_pos_list_median,
                        self.ob_pos_list_median,
                        data_norm_list=None,
                        ob_norm_list=None,
                        G0_rot=self.par_rot_G0rz_DSpinBox.value())

        elif self.instrument_Combo.currentText() == "ICON":
            self.TI,self.DPC,self.DFI,self.a0_ob,self.a1_ob,self.phi_ob,self.a0_data,self.a1_data,self.phi_data= ngI.nGI(self.data_img_list_median,self.ob_img_list_median,self.dc_median_filtered,self.fit_Combo.text(),bool(self.par_full_per_Combo.currentText()),int(self.par_per_SpinBox.value()),data_pos_list=None,ob_pos_list=None,data_norm_list=self.data_img_list_norm,ob_norm_list=self.ob_img_list_norm,G0_rot=None)
        else:
            self.TI,self.DPC,self.DFI,self.a0_ob,self.a1_ob,self.phi_ob,self.a0_data,self.a1_data,self.phi_data= ngI.nGI(self.data_img_list_median,self.ob_img_list_median,self.dc_median_filtered,self.fit_Combo.text(),bool(self.par_full_per_Combo.currentText()),int(self.par_per_SpinBox.value()),data_pos_list=None,ob_pos_list=None,data_norm_list=None,ob_norm_list=None,G0_rot=None)
        #self.ngiThread.quit()
        #self.calc_progressBar.setValue(83)
        #time.sleep(0.5)
        
        self.calc_state=1
        #self.ngi_calc_gui(1)

    def ngi_calc_gui(self,temp):
        self.calc_Button.setText("Calculate")
        self.calc_Button.setEnabled(False)
        
        
        self.tabWidget2.setTabEnabled(1,True)
        self.tabWidget2.setTabEnabled(2,True)
        self.tabWidget2.setTabEnabled(3,True)
        self.tabWidget2.setTabEnabled(4,True)
        self.tabWidget2.setTabEnabled(5,True)

        self.mpl_ti_pre_widget.axes.set_title("TI")
        self.mpl_ti_pre_widget.axes.imshow(self.TI,vmin=np.amin(self.a0_data)/np.amax(self.a0_ob),vmax=1,cmap=plt.cm.gray)
        #self.mpl_ti_pre_widget.figure.savefig("TI.jpg")
        self.mpl_ti_pre_widget.draw()
        self.mpl_dpci_pre_widget.axes.imshow(self.DPC,vmin=-(np.amax(self.phi_data)-np.amin(self.phi_ob)),vmax=(np.amax(self.phi_data)-np.amin(self.phi_ob)),cmap=plt.cm.gray)
        self.mpl_dpci_pre_widget.axes.set_title("DPCI")
        self.mpl_dpci_pre_widget.draw()
        self.mpl_dfi_pre_widget.axes.imshow(self.DFI,vmin=0,vmax=1,cmap=plt.cm.gray)
        self.mpl_dfi_pre_widget.axes.set_title("DFI")
        #self.mpl_dfi_pre_widget.figure.savefig("DFI.jpg")
        self.mpl_dfi_pre_widget.draw()

        self.vis_analysis(self.a0_ob,self.a1_ob,self.a0_data,self.a1_data)
        self.phase_analysis(self.phi_ob,self.phi_data)
        self.ti_analysis(self.data_img_list_median,self.ob_img_list_median)
        self.dpci_analysis(self.data_img_list_median,self.ob_img_list_median)
        self.dfi_analysis(self.data_img_list_median,self.ob_img_list_median)
        self.calc_progressBar.setValue(100)
        #self.emit(QtCore.SIGNAL('status'),[self.ready,"Ready"])
        self.statusSignal.emit([self.ready,"Ready"])
        logging.info('Complete Calculation time '+str(time.time()-self.before)+ ' sec \n')
        
        self.tabWidget.setTabEnabled(0,True)
        self.tabWidget.setTabEnabled(1,True)
        self.tabWidget.setTabEnabled(2,True)
        self.tabWidget.setTabEnabled(3,True)
        self.tabWidget.setTabEnabled(4,True)
        self.tabWidget.setTabEnabled(5,True)
        self.tabWidget.setTabEnabled(6,True)
        self.calc_Button.setEnabled(True)
        self.calc_state=2

    def multi_handle(self):
        if self.multi_Checkbox.isChecked():
            self.tabWidget.setTabEnabled(7,True)
            self.calc_Button.setEnabled(False)
            self.multi_igno_Checkbox.setChecked(True)
        else:
            self.tabWidget.setTabEnabled(7,False)
            self.calc_Button.setEnabled(True)
            self.multi_igno_Checkbox.setChecked(False)





    def vis_analysis(self,a0_ob,a1_ob,a0_data,a1_data):
#==============================================================================
#       vis_analysisi:  Called by self.ngi_calc.
#
#                       Creates the visibility map for the OB and Data images. and draws them in the Visibility tab.
#==============================================================================
        try:
            self.vis_ob_img=np.divide(a1_ob,a0_ob)
        except RuntimeWarning:
            loggin.warning("Division by zero while calculating the OB visibility")
        try:
            self.vis_dat_img=np.divide(a1_data,a0_data)
        except RuntimeWarning:
            loggin.warning("Division by zero while calculating the Data visibility")
        self.vis_mean_dat_Box.setText(str(np.around(np.mean(self.vis_dat_img),2)))
        self.vis_mean_ob_Box.setText(str(np.around(np.mean(self.vis_ob_img),2)))
        self.vis_ax_dat=self.mpl_vis_dat_widget.axes.imshow(self.vis_dat_img,vmin=0,vmax=0.5,cmap=plt.cm.gray)
        self.mpl_vis_dat_widget.axes.set_title("Visibility Data")
        self.mpl_vis_dat_widget.axes.set_xlabel("Pixel (x)")
        self.mpl_vis_dat_widget.axes.set_ylabel("Pixel (y)")
        self.mpl_vis_dat_widget.draw()

        self.vis_ax_ob=self.mpl_vis_ob_widget.axes.imshow(self.vis_ob_img,vmin=0,vmax=0.5,cmap=plt.cm.gray)
        self.mpl_vis_ob_widget.axes.set_title("Visibility OB")
        self.mpl_vis_ob_widget.axes.set_xlabel("Pixel (x)")
        self.mpl_vis_ob_widget.axes.set_ylabel("Pixel (y)")
        self.mpl_vis_ob_widget.draw()

    def phase_analysis(self,phi_ob,phi_data):
#==============================================================================
#       phase_analysis:     Called by self.ngi_calc.
#
#                           Creates the phase map for the OB and Data images. and draws them in the Phase tab.
#==============================================================================
        self.phase_ob_img=phi_ob
        self.phase_dat_img=phi_data
        self.phase_mean_dat_Box.setText(str(np.around(np.mean(self.phase_dat_img),2)))
        self.phase_mean_ob_Box.setText(str(np.around(np.mean(self.phase_ob_img),2)))
        self.phase_ax_dat=self.mpl_phase_dat_widget.axes.imshow(self.phase_dat_img,vmin=-np.pi,vmax=np.pi,cmap=plt.cm.gray)
        self.mpl_phase_dat_widget.axes.set_title("Phase Data")
        self.mpl_phase_dat_widget.axes.set_xlabel("Pixel (x)")
        self.mpl_phase_dat_widget.axes.set_ylabel("Pixel (y)")
        self.mpl_phase_dat_widget.draw()

        self.phase_ax_ob=self.mpl_phase_ob_widget.axes.imshow(self.phase_ob_img,vmin=-np.pi,vmax=np.pi,cmap=plt.cm.gray)
        self.mpl_phase_ob_widget.axes.set_title("Phase OB")
        self.mpl_phase_ob_widget.axes.set_xlabel("Pixel (x)")
        self.mpl_phase_ob_widget.axes.set_ylabel("Pixel (y)")
        self.mpl_phase_ob_widget.draw()

    def ti_analysis(self,data_img_list,ob_img_list):
#==============================================================================
#       ti_analysis:    Called by self.ngi_calc.
#
#                       Creates the TI Tab and sets the default values. For the Oscilation this is the central pixel,
#                       while the data image will show the first data image.
#                       Also sets minimum and maximum grayvalues of the TI and the used colormap.
#                       Also creates the histogramm for the TI, which is by default hidden.
#==============================================================================
        #if self.ti == None:
        cm_ti=self.cmap_list[self.ti_color_Combo.currentIndex()]
        #self.mpl_ti_widget.axes.clear()
        self.ti=self.mpl_ti_widget.axes.imshow(self.TI,vmin=self.ti_vminSpinBox.value(),vmax=self.ti_vmaxSpinBox.value(),cmap=cm_ti,interpolation="none")
        #self.ti_toolbar.home()

        self.mpl_ti_widget.axes.set_title("TI")
        self.mpl_ti_widget.axes.set_xlabel("Pixel (x)")
        self.mpl_ti_widget.axes.set_ylabel("Pixel (y)")
        #if self.ti.colorbar == None:
        if self.ti_cbar == None:
            #cax = make_axes_locatable(self.mpl_ti_widget.axes).append_axes("right", size="10%", pad=0.5)
            self.ti_cbar=self.mpl_ti_widget.figure.colorbar(self.ti)
        self.mpl_ti_widget.draw()
        
        
        self.ti_im_step=0

        if self.default_pixel == None:
            h,w=self.TI.shape
        else:
            w=2*self.default_pixel[0]
            h=2*self.default_pixel[1]
        if self.instrument_Combo.currentText() == "ANTARES":
            x_list_raw_dat,x_list_raw_ob,y_raw_list_dat,y_raw_list_ob,x_list_fit_dat,x_list_fit_ob,y_fit_list_dat,y_fit_list_ob=osc_calc(int(w/2),int(h/2),self.data_img_list_median,self.ob_img_list_median,self.dc_median_filtered,self.im_num_SpinBox.value(),self.a0_data,self.a1_data,self.phi_data,self.a0_ob,self.a1_ob,self.phi_ob,self.par_img_per_step_SpinBox.value(),self.par_rot_G0rz_DSpinBox.value(),self.data_pos_list_median,self.ob_pos_list_median)
        else:
            x_list_raw_dat,x_list_raw_ob,y_raw_list_dat,y_raw_list_ob,x_list_fit_dat,x_list_fit_ob,y_fit_list_dat,y_fit_list_ob=osc_calc(int(w/2),int(h/2),self.data_img_list_median,self.ob_img_list_median,self.dc_median_filtered,self.im_num_SpinBox.value(),self.a0_data,self.a1_data,self.phi_data,self.a0_ob,self.a1_ob,self.phi_ob,self.par_img_per_step_SpinBox.value(),self.par_rot_G0rz_DSpinBox.value())
        self.mpl_ti_osc_dat_widget.axes.clear()
        self.mpl_ti_osc_dat_widget.axes.errorbar(x_list_raw_dat,y_raw_list_dat,fmt="ro",yerr=5*np.sqrt(np.array(y_raw_list_dat)),elinewidth=2,capthick=2,label="Data")
        self.mpl_ti_osc_dat_widget.axes.errorbar(x_list_raw_ob,y_raw_list_ob,fmt="bo",yerr=5*np.sqrt(np.array(y_raw_list_ob)),elinewidth=2,capthick=2,label="OB")
        self.mpl_ti_osc_dat_widget.axes.plot(x_list_fit_dat,y_fit_list_dat,'r-',label="Fitted Data a0="+str(np.around(self.a0_data[int(h/2)][int(w/2)],2))+" a1="+str(np.around(self.a1_data[int(h/2)][int(w/2)],2))+" phi="+str(np.around(self.phi_data[int(h/2)][int(w/2)],2)))
        self.mpl_ti_osc_dat_widget.axes.plot(x_list_fit_ob,y_fit_list_ob,'b-',label="Fitted OB a0="+str(np.around(self.a0_ob[int(h/2)][int(w/2)],2))+" a1="+str(np.around(self.a1_ob[int(h/2)][int(w/2)],2))+" phi="+str(np.around(self.phi_ob[int(h/2)][int(w/2)],2)))
        if self.instrument_Combo.currentText() == "ANATRES":
            self.mpl_ti_osc_dat_widget.axes.set_xlabel("Position of G0tx in mm")
        else:
            self.mpl_ti_osc_dat_widget.axes.set_xlabel("Number of Image")
        #self.mpl_ti
        self.mpl_ti_osc_dat_widget.axes.set_ylabel("Intensity Graylevel")
        self.mpl_ti_osc_dat_widget.axes.set_title("Oscillation of Pixel ("+str(int(np.around(w/2)))+","+str(int(np.around(h/2)))+")")
        self.mpl_ti_osc_dat_widget.axes.legend(fontsize=8,loc=0,frameon=False,ncol=2)

        self.mpl_ti_osc_dat_widget.axes.set_xlim([min(x_list_raw_dat),np.around(max(x_list_raw_dat),1)])
        self.mpl_ti_osc_dat_widget.draw()


        self.ti_dat=self.mpl_ti_img_dat_widget.axes.imshow(data_img_list[self.ti_im_step],cmap=plt.cm.gray)
        self.mpl_ti_img_dat_widget.axes.set_title("Data (Showing Image 0)")
        self.mpl_ti_img_dat_widget.draw()

        histogram = np.histogram(self.TI, bins=500)
        bins = histogram[1]
        central_bins = (bins[1:] + bins[:-1]) / 2.
        self.mpl_ti_hist_widget.axes.clear()
        self.mpl_ti_hist_widget.axes.fill_between(central_bins,0, histogram[0],color="black")
        self.mpl_ti_hist_widget.axes.set_xlabel("Grayvalue")
        self.mpl_ti_hist_widget.axes.set_ylabel("Number of Pixels")
        self.mpl_ti_hist_widget.axes.set_ylim([0,max(histogram[0])])
        self.mpl_ti_hist_widget.draw()
        self.ti_osc_raw=[x_list_raw_dat,x_list_raw_ob,y_raw_list_dat,y_raw_list_ob]
        self.ti_osc_fit=[x_list_fit_dat,x_list_fit_ob,y_fit_list_dat,y_fit_list_ob]
        self.ti_osc_pix=[w/2,h/2]
        self.ti_osc_par_dat=[self.a0_data,self.a1_data,self.phi_data]
        self.ti_osc_par_ob=[self.a0_ob,self.a1_ob,self.phi_ob]
        if self.ti_pixel_Button.isChecked()==False:
            self.ti_pixel_Button.click()

    def dpci_analysis(self,data_img_list,ob_img_list):
#==============================================================================
#       dpci_analysis:      Called by self.ngi_calc.
#
#                           Creates the DPCI Tab and sets the default values. For the Oscilation this is the central pixel,
#                           while the data image will show the first data image.
#                           Also sets minimum and maximum grayvalues of the DPCI and the used colormap.
#                           Also creates the histogramm for the DPCI, which is by default hidden.
#==============================================================================
        #if self.ti == None:

        #self.dpci_toolbar.home()
           #self.mpl_ti_widget.axes.clear()
        cm_dpci=self.cmap_list[self.dpci_color_Combo.currentIndex()]
        self.dpci=self.mpl_dpci_widget.axes.imshow(self.DPC,vmin=self.dpci_vminSpinBox.value(),vmax=self.dpci_vmaxSpinBox.value(),cmap=cm_dpci,interpolation="none")

        self.mpl_dpci_widget.axes.set_title("DPCI")
        self.mpl_dpci_widget.axes.set_xlabel("Pixel (x)")
        self.mpl_dpci_widget.axes.set_ylabel("Pixel (y)")
        #if self.ti.colorbar == None:
        if self.dpci_cbar == None:
            #cax = make_axes_locatable(self.mpl_ti_widget.axes).append_axes("right", size="10%", pad=0.5)
            self.dpci_cbar=self.mpl_dpci_widget.figure.colorbar(self.dpci)
        self.mpl_dpci_widget.draw()
        self.dpci_im_step=0


        if self.default_pixel == None:
            h,w=self.DPC.shape
        else:
            w=2*self.default_pixel[0]
            h=2*self.default_pixel[1]

        if self.instrument_Combo.currentText() == "ANTARES":
            x_list_raw_dat,x_list_raw_ob,y_raw_list_dat,y_raw_list_ob,x_list_fit_dat,x_list_fit_ob,y_fit_list_dat,y_fit_list_ob=osc_calc(int(w/2),int(h/2),self.data_img_list_median,self.ob_img_list_median,self.dc_median_filtered,self.im_num_SpinBox.value(),self.a0_data,self.a1_data,self.phi_data,self.a0_ob,self.a1_ob,self.phi_ob,self.par_img_per_step_SpinBox.value(),self.par_rot_G0rz_DSpinBox.value(),self.data_pos_list_median,self.ob_pos_list_median)
        else:
            x_list_raw_dat,x_list_raw_ob,y_raw_list_dat,y_raw_list_ob,x_list_fit_dat,x_list_fit_ob,y_fit_list_dat,y_fit_list_ob=osc_calc(int(w/2),int(h/2),self.data_img_list_median,self.ob_img_list_median,self.dc_median_filtered,self.im_num_SpinBox.value(),self.a0_data,self.a1_data,self.phi_data,self.a0_ob,self.a1_ob,self.phi_ob,self.par_img_per_step_SpinBox.value(),self.par_rot_G0rz_DSpinBox.value())
        self.mpl_dpci_osc_dat_widget.axes.clear()
        self.mpl_dpci_osc_dat_widget.axes.errorbar(x_list_raw_dat,y_raw_list_dat,fmt="ro",yerr=5*np.sqrt(np.array(y_raw_list_dat)),elinewidth=2,capthick=2,label="Data")
        self.mpl_dpci_osc_dat_widget.axes.errorbar(x_list_raw_ob,y_raw_list_ob,fmt="bo",yerr=5*np.sqrt(np.array(y_raw_list_ob)),elinewidth=2,capthick=2,label="OB")
        self.mpl_dpci_osc_dat_widget.axes.plot(x_list_fit_dat,y_fit_list_dat,'r-',label="Fitted Data a0="+str(np.around(self.a0_data[int(h/2)][int(w/2)],2))+" a1="+str(np.around(self.a1_data[int(h/2)][int(w/2)],2))+" phi="+str(np.around(self.phi_data[int(h/2)][int(w/2)],2)))
        self.mpl_dpci_osc_dat_widget.axes.plot(x_list_fit_ob,y_fit_list_ob,'b-',label="Fitted OB a0="+str(np.around(self.a0_ob[int(h/2)][int(w/2)],2))+" a1="+str(np.around(self.a1_ob[int(h/2)][int(w/2)],2))+" phi="+str(np.around(self.phi_ob[int(h/2)][int(w/2)],2)))
        if self.instrument_Combo.currentText() == "ANATRES":
            self.mpl_dpci_osc_dat_widget.axes.set_xlabel("Position of G0tx in mm")
        else:
            self.mpl_dpci_osc_dat_widget.axes.set_xlabel("Number of Image")
        #self.mpl_ti
        self.mpl_dpci_osc_dat_widget.axes.set_ylabel("Intensity Graylevel")
        self.mpl_dpci_osc_dat_widget.axes.set_title("Oscillation of Pixel ("+str(int(np.around(w/2)))+","+str(int(np.around(h/2)))+")")
        self.mpl_dpci_osc_dat_widget.axes.legend(fontsize=8,loc=0,frameon=False,ncol=2)
        self.mpl_dpci_osc_dat_widget.axes.set_xlim([min(x_list_raw_dat),np.around(max(x_list_raw_dat),1)])
        self.mpl_dpci_osc_dat_widget.draw()


        self.dpci_dat=self.mpl_dpci_img_dat_widget.axes.imshow(data_img_list[self.dpci_im_step],cmap=plt.cm.gray)
        self.mpl_dpci_img_dat_widget.axes.set_title("Data (Showing Image 0)")
        self.mpl_dpci_img_dat_widget.draw()
        
        
        histogram = np.histogram(self.DPC, bins=500)
        bins = histogram[1]
        central_bins = (bins[1:] + bins[:-1]) / 2.
        self.mpl_dpci_hist_widget.axes.clear()
        self.mpl_dpci_hist_widget.axes.fill_between(central_bins,0, histogram[0],color="black")
        self.mpl_dpci_hist_widget.axes.set_xlabel("Grayvalue")
        self.mpl_dpci_hist_widget.axes.set_ylabel("Number of Pixels")
        self.mpl_dpci_hist_widget.axes.set_ylim([0,max(histogram[0])])
        self.mpl_dpci_hist_widget.draw()
        
        
        self.dpci_osc_raw=[x_list_raw_dat,x_list_raw_ob,y_raw_list_dat,y_raw_list_ob]
        self.dpci_osc_fit=[x_list_fit_dat,x_list_fit_ob,y_fit_list_dat,y_fit_list_ob]
        self.dpci_osc_pix=[w/2,h/2]
        self.dpci_osc_par_dat=[self.a0_data,self.a1_data,self.phi_data]
        self.dpci_osc_par_ob=[self.a0_ob,self.a1_ob,self.phi_ob]
        if self.dpci_pixel_Button.isChecked()==False:
            self.dpci_pixel_Button.click()


    def dfi_analysis(self,data_img_list,ob_img_list):
#==============================================================================
#       dfi_analysis:       Called by self.ngi_calc.
#
#                           Creates the DFI Tab and sets the default values. For the Oscilation this is the central pixel,
#                           while the data image will show the first data image.
#                           Also sets minimum and maximum grayvalues of the DFI and the used colormap.
#                           Also creates the histogramm for the DFI, which is by default hidden.
#==============================================================================
        #if self.ti == None:

            #self.mpl_ti_widget.axes.clear()
        cm_dfi=self.cmap_list[self.dfi_color_Combo.currentIndex()]
        self.dfi=self.mpl_dfi_widget.axes.imshow(self.DFI,vmin=self.dfi_vminSpinBox.value(),vmax=self.dfi_vmaxSpinBox.value(),cmap=cm_dfi,interpolation="none")
        #self.dfi_toolbar.home()
        self.mpl_dfi_widget.axes.set_title("DFI")
        self.mpl_dfi_widget.axes.set_xlabel("Pixel (x)")
        self.mpl_dfi_widget.axes.set_ylabel("Pixel (y)")
        #if self.ti.colorbar == None:
        if self.dfi_cbar == None:
            #cax = make_axes_locatable(self.mpl_ti_widget.axes).append_axes("right", size="10%", pad=0.5)
            self.dfi_cbar=self.mpl_dfi_widget.figure.colorbar(self.dfi)
        self.mpl_dfi_widget.draw()
        self.dfi_im_step=0


        if self.default_pixel == None:
            h,w=self.DFI.shape
        else:
            w=2*self.default_pixel[0]
            h=2*self.default_pixel[1]

        if self.instrument_Combo.currentText() == "ANTARES":
            x_list_raw_dat,x_list_raw_ob,y_raw_list_dat,y_raw_list_ob,x_list_fit_dat,x_list_fit_ob,y_fit_list_dat,y_fit_list_ob=osc_calc(int(w/2),int(h/2),self.data_img_list_median,self.ob_img_list_median,self.dc_median_filtered,self.im_num_SpinBox.value(),self.a0_data,self.a1_data,self.phi_data,self.a0_ob,self.a1_ob,self.phi_ob,self.par_img_per_step_SpinBox.value(),self.par_rot_G0rz_DSpinBox.value(),self.data_pos_list_median,self.ob_pos_list_median)
        else:
            x_list_raw_dat,x_list_raw_ob,y_raw_list_dat,y_raw_list_ob,x_list_fit_dat,x_list_fit_ob,y_fit_list_dat,y_fit_list_ob=osc_calc(int(w/2),int(h/2),self.data_img_list_median,self.ob_img_list_median,self.dc_median_filtered,self.im_num_SpinBox.value(),self.a0_data,self.a1_data,self.phi_data,self.a0_ob,self.a1_ob,self.phi_ob,self.par_img_per_step_SpinBox.value(),self.par_rot_G0rz_DSpinBox.value())

        self.mpl_dfi_osc_dat_widget.axes.clear()
        self.mpl_dfi_osc_dat_widget.axes.errorbar(x_list_raw_dat,y_raw_list_dat,fmt="ro",yerr=5*np.sqrt(np.array(y_raw_list_dat)),elinewidth=2,capthick=2,label="Data")
        self.mpl_dfi_osc_dat_widget.axes.errorbar(x_list_raw_ob,y_raw_list_ob,fmt="bo",yerr=5*np.sqrt(np.array(y_raw_list_ob)),elinewidth=2,capthick=2,label="OB")
        self.mpl_dfi_osc_dat_widget.axes.plot(x_list_fit_dat,y_fit_list_dat,'r-',label="Fitted Data a0="+str(np.around(self.a0_data[int(h/2)][int(w/2)],2))+" a1="+str(np.around(self.a1_data[int(h/2)][int(w/2)],2))+" phi="+str(np.around(self.phi_data[int(h/2)][int(w/2)],2)))
        self.mpl_dfi_osc_dat_widget.axes.plot(x_list_fit_ob,y_fit_list_ob,'b-',label="Fitted OB a0="+str(np.around(self.a0_ob[int(h/2)][int(w/2)],2))+" a1="+str(np.around(self.a1_ob[int(h/2)][int(w/2)],2))+" phi="+str(np.around(self.phi_ob[int(h/2)][int(w/2)],2)))
        if self.instrument_Combo.currentText() == "ANATRES":
            self.mpl_dfi_osc_dat_widget.axes.set_xlabel("Position of G0tx in mm")
        else:
            self.mpl_dfi_osc_dat_widget.axes.set_xlabel("Number of Image")
        #self.mpl_ti
        self.mpl_dfi_osc_dat_widget.axes.set_ylabel("Intensity Graylevel")
        self.mpl_dfi_osc_dat_widget.axes.set_title("Oscillation of Pixel ("+str(int(np.around(w/2)))+","+str(int(np.around(h/2)))+")")
        self.mpl_dfi_osc_dat_widget.axes.legend(fontsize=8,loc=0,frameon=False,ncol=2)
        self.mpl_dfi_osc_dat_widget.axes.set_xlim([min(x_list_raw_dat),np.around(max(x_list_raw_dat),1)])
        self.mpl_dfi_osc_dat_widget.draw()


        self.dfi_dat=self.mpl_dfi_img_dat_widget.axes.imshow(data_img_list[self.dfi_im_step],cmap=plt.cm.gray)
        self.mpl_dfi_img_dat_widget.axes.set_title("Data (Showing Image 0)")
        self.mpl_dfi_img_dat_widget.draw()

        histogram = np.histogram(self.DFI, bins=500)
        bins = histogram[1]
        central_bins = (bins[1:] + bins[:-1]) / 2.
        self.mpl_dfi_hist_widget.axes.clear()
        self.mpl_dfi_hist_widget.axes.fill_between(central_bins,0, histogram[0],color="black")
        self.mpl_dfi_hist_widget.axes.set_xlabel("Grayvalue")
        self.mpl_dfi_hist_widget.axes.set_ylabel("Number of Pixels")
        self.mpl_dfi_hist_widget.axes.set_ylim([0,max(histogram[0])])
        self.mpl_dfi_hist_widget.draw()
        self.dfi_osc_raw=[x_list_raw_dat,x_list_raw_ob,y_raw_list_dat,y_raw_list_ob]
        self.dfi_osc_fit=[x_list_fit_dat,x_list_fit_ob,y_fit_list_dat,y_fit_list_ob]
        self.dfi_osc_pix=[w/2,h/2]
        self.dfi_osc_par_dat=[self.a0_data,self.a1_data,self.phi_data]
        self.dfi_osc_par_ob=[self.a0_ob,self.a1_ob,self.phi_ob]
        if self.dfi_pixel_Button.isChecked()==False:
            self.dfi_pixel_Button.click()
        #data_img_list=None
    def on_click(self,event):
#==============================================================================
#       on_click:   Called by clicking on either the TI, DPCI, DFI or the corresponding oscillation.
#
#                   Only works when self.ti_pixel_Button, self.dpci_pixel_Button or self.dfii_pixel_Button are checked.
#                   When clicking on either TI,DPCI or DFI the oscillation plot will change to show the oscillation at the
#                   clicked pixel.
#                   If clicked on the oscillation plot the Data Image will show the image corresponding to the point nearest to the click.
#==============================================================================
        self.x0 = event.xdata
        self.y0 = event.ydata

        
        if event.inaxes == self.mpl_ti_osc_dat_widget.axes or event.inaxes == self.mpl_dpci_osc_dat_widget.axes or event.inaxes == self.mpl_dfi_osc_dat_widget.axes:
            im_step=self.x0
            
            if self.instrument_Combo.currentText()== "ANTARES":
                    im_step=self.data_pos_list_median.index(min(self.data_pos_list_median, key=lambda x:abs(x-im_step)))
                    
            else:
                im_step=int(np.around(self.x0))
                if im_step<0:
                    im_step=0
                elif im_step>self.im_num_SpinBox.value():
                    im_step=self.im_num_SpinBox.value()-1


        
            #temp_figure_dat=self.mpl_ti_img_dat_widget
            self.ti_im_step=im_step
            cm_temp=self.cmap_list[self.ti_color_Combo.currentIndex()]
            self.ti_dat=self.mpl_ti_img_dat_widget.axes.imshow(self.data_img_list_median[im_step],cmap=cm_temp)
            self.mpl_ti_img_dat_widget.axes.set_title("Data (Showing Image "+str(im_step)+")")
            self.mpl_ti_img_dat_widget.draw()
        
            #temp_figure_dat=self.mpl_dpci_img_dat_widget
            self.dpci_im_step=im_step
            cm_temp=self.cmap_list[self.dpci_color_Combo.currentIndex()]
            self.dpci_dat=self.mpl_dpci_img_dat_widget.axes.imshow(self.data_img_list_median[im_step],cmap=cm_temp)
            self.mpl_dpci_img_dat_widget.axes.set_title("Data (Showing Image "+str(im_step)+")")
            self.mpl_dpci_img_dat_widget.draw()
        
            #temp_figure_dat=self.mpl_dfi_img_dat_widget
            self.dfi_im_step=im_step
            cm_temp=self.cmap_list[self.dfi_color_Combo.currentIndex()]
            self.dfi_dat=self.mpl_dfi_img_dat_widget.axes.imshow(self.data_img_list_median[im_step],cmap=cm_temp)
            self.mpl_dfi_img_dat_widget.axes.set_title("Data (Showing Image "+str(im_step)+")")
            self.mpl_dfi_img_dat_widget.draw()


        elif event.inaxes == self.mpl_ti_widget.axes  or event.inaxes == self.mpl_dpci_widget.axes or event.inaxes == self.mpl_dfi_widget.axes:
            self.x0=int(self.x0)
            self.y0=int(self.y0)
            if self.instrument_Combo.currentText() == "ANTARES":
                x_list_raw_dat,x_list_raw_ob,y_raw_list_dat,y_raw_list_ob,x_list_fit_dat,x_list_fit_ob,y_fit_list_dat,y_fit_list_ob=osc_calc(int(self.x0),int(self.y0),self.data_img_list_median,self.ob_img_list_median,self.dc_median_filtered,self.im_num_SpinBox.value(),self.a0_data,self.a1_data,self.phi_data,self.a0_ob,self.a1_ob,self.phi_ob,self.par_img_per_step_SpinBox.value(),self.par_rot_G0rz_DSpinBox.value(),self.data_pos_list_median,self.ob_pos_list_median)
            else:
                x_list_raw_dat,x_list_raw_ob,y_raw_list_dat,y_raw_list_ob,x_list_fit_dat,x_list_fit_ob,y_fit_list_dat,y_fit_list_ob=osc_calc(int(self.x0),int(self.y0),self.data_img_list_median,self.ob_img_list_median,self.dc_median_filtered,self.im_num_SpinBox.value(),self.a0_data,self.a1_data,self.phi_data,self.a0_ob,self.a1_ob,self.phi_ob,self.par_img_per_step_SpinBox.value(),self.par_rot_G0rz_DSpinBox.value())
        
            temp_figure_osc=self.mpl_ti_osc_dat_widget
            self.ti_osc_raw=[x_list_raw_dat,x_list_raw_ob,y_raw_list_dat,y_raw_list_ob]
            self.ti_osc_fit=[x_list_fit_dat,x_list_fit_ob,y_fit_list_dat,y_fit_list_ob]
            self.ti_osc_pix=[self.x0,self.y0]
            self.ti_osc_par_dat=[self.a0_data,self.a1_data,self.phi_data]
            self.ti_osc_par_ob=[self.a0_ob,self.a1_ob,self.phi_ob]
            temp_figure_osc.axes.clear()
            temp_figure_osc.axes.errorbar(x_list_raw_dat,y_raw_list_dat,fmt="ro",yerr=5*np.sqrt(np.array(y_raw_list_dat)),elinewidth=2,capthick=2,label="Data" )
            temp_figure_osc.axes.errorbar(x_list_raw_ob,y_raw_list_ob,fmt="bo",yerr=5*np.sqrt(np.array(y_raw_list_ob)),elinewidth=2,capthick=2,label="OB")
            temp_figure_osc.axes.plot(x_list_fit_dat,y_fit_list_dat,'r-',label="Fitted Data a0="+str(np.around(self.a0_data[self.y0][self.x0],2))+" a1="+str(np.around(self.a1_data[self.y0][self.x0],2))+" phi="+str(np.around(self.phi_data[self.y0][self.x0],2)))
            temp_figure_osc.axes.plot(x_list_fit_ob,y_fit_list_ob,'b-',label="Fitted OB a0="+str(np.around(self.a0_ob[self.y0][self.x0],2))+" a1="+str(np.around(self.a1_ob[self.y0][self.x0],2))+" phi="+str(np.around(self.phi_ob[self.y0][self.x0],2)))
            if self.instrument_Combo.currentText() == "ANATRES":
                temp_figure_osc.axes.set_xlabel("Position of G0tx in mm")
            else:
                temp_figure_osc.axes.set_xlabel("Number of Image")
            #self.mpl_ti
            temp_figure_osc.axes.set_ylabel("Intensity Graylevel")
            temp_figure_osc.axes.set_title("Oscillation of Pixel ("+str(self.x0)+","+str(self.y0)+")")
            temp_figure_osc.axes.set_xlim([min(x_list_raw_dat),np.around(max(x_list_raw_dat),1)])
            temp_figure_osc.axes.legend(fontsize=8,loc=0,frameon=False,ncol=2)
            temp_figure_osc.draw()
            temp_figure_osc=self.mpl_dpci_osc_dat_widget
            self.dpci_osc_raw=[x_list_raw_dat,x_list_raw_ob,y_raw_list_dat,y_raw_list_ob]
            self.dpci_osc_fit=[x_list_fit_dat,x_list_fit_ob,y_fit_list_dat,y_fit_list_ob]
            self.dpci_osc_pix=[self.x0,self.y0]
            self.dpci_osc_par_dat=[self.a0_data,self.a1_data,self.phi_data]
            self.dpci_osc_par_ob=[self.a0_ob,self.a1_ob,self.phi_ob]
            temp_figure_osc.axes.clear()
            temp_figure_osc.axes.errorbar(x_list_raw_dat,y_raw_list_dat,fmt="ro",yerr=5*np.sqrt(np.array(y_raw_list_dat)),elinewidth=2,capthick=2,label="Data" )
            temp_figure_osc.axes.errorbar(x_list_raw_ob,y_raw_list_ob,fmt="bo",yerr=5*np.sqrt(np.array(y_raw_list_ob)),elinewidth=2,capthick=2,label="OB")
            temp_figure_osc.axes.plot(x_list_fit_dat,y_fit_list_dat,'r-',label="Fitted Data a0="+str(np.around(self.a0_data[self.y0][self.x0],2))+" a1="+str(np.around(self.a1_data[self.y0][self.x0],2))+" phi="+str(np.around(self.phi_data[self.y0][self.x0],2)))
            temp_figure_osc.axes.plot(x_list_fit_ob,y_fit_list_ob,'b-',label="Fitted OB a0="+str(np.around(self.a0_ob[self.y0][self.x0],2))+" a1="+str(np.around(self.a1_ob[self.y0][self.x0],2))+" phi="+str(np.around(self.phi_ob[self.y0][self.x0],2)))
            if self.instrument_Combo.currentText() == "ANATRES":
                temp_figure_osc.axes.set_xlabel("Position of G0tx in mm")
            else:
                temp_figure_osc.axes.set_xlabel("Number of Image")
            #self.mpl_ti
            temp_figure_osc.axes.set_ylabel("Intensity Graylevel")
            temp_figure_osc.axes.set_title("Oscillation of Pixel ("+str(self.x0)+","+str(self.y0)+")")
            temp_figure_osc.axes.set_xlim([min(x_list_raw_dat),np.around(max(x_list_raw_dat),1)])
            temp_figure_osc.axes.legend(fontsize=8,loc=0,frameon=False,ncol=2)
            temp_figure_osc.draw()
            temp_figure_osc=self.mpl_dfi_osc_dat_widget
            self.dfi_osc_raw=[x_list_raw_dat,x_list_raw_ob,y_raw_list_dat,y_raw_list_ob]
            self.dfi_osc_fit=[x_list_fit_dat,x_list_fit_ob,y_fit_list_dat,y_fit_list_ob]
            self.dfi_osc_pix=[self.x0,self.y0]
            self.dfi_osc_par_dat=[self.a0_data,self.a1_data,self.phi_data]
            self.dfi_osc_par_ob=[self.a0_ob,self.a1_ob,self.phi_ob]
           
            temp_figure_osc.axes.clear()
            temp_figure_osc.axes.errorbar(x_list_raw_dat,y_raw_list_dat,fmt="ro",yerr=5*np.sqrt(np.array(y_raw_list_dat)),elinewidth=2,capthick=2,label="Data" )
            temp_figure_osc.axes.errorbar(x_list_raw_ob,y_raw_list_ob,fmt="bo",yerr=5*np.sqrt(np.array(y_raw_list_ob)),elinewidth=2,capthick=2,label="OB")
            temp_figure_osc.axes.plot(x_list_fit_dat,y_fit_list_dat,'r-',label="Fitted Data a0="+str(np.around(self.a0_data[self.y0][self.x0],2))+" a1="+str(np.around(self.a1_data[self.y0][self.x0],2))+" phi="+str(np.around(self.phi_data[self.y0][self.x0],2)))
            temp_figure_osc.axes.plot(x_list_fit_ob,y_fit_list_ob,'b-',label="Fitted OB a0="+str(np.around(self.a0_ob[self.y0][self.x0],2))+" a1="+str(np.around(self.a1_ob[self.y0][self.x0],2))+" phi="+str(np.around(self.phi_ob[self.y0][self.x0],2)))
            if self.instrument_Combo.currentText() == "ANATRES":
                temp_figure_osc.axes.set_xlabel("Position of G0tx in mm")
            else:
                temp_figure_osc.axes.set_xlabel("Number of Image")
            
            temp_figure_osc.axes.set_ylabel("Intensity Graylevel")
            temp_figure_osc.axes.set_title("Oscillation of Pixel ("+str(self.x0)+","+str(self.y0)+")")
            temp_figure_osc.axes.set_xlim([min(x_list_raw_dat),np.around(max(x_list_raw_dat),1)])
            temp_figure_osc.axes.legend(fontsize=8,loc=0,frameon=False,ncol=2)
            temp_figure_osc.draw()




    def replot_img(self):
#==============================================================================
#       replot_img:     Called by changing the colorbar, maximum grayvalue or minimum grayvalue in the TI_tab, DPCI_tab or DFI_tab.
#
#                       Replots the associated image with the new values.
#==============================================================================
        sender=self.sender()


        if sender == self.ti_vminSpinBox or sender == self.ti_vmaxSpinBox:
            self.ti.set_clim(vmin=self.ti_vminSpinBox.value(),vmax=self.ti_vmaxSpinBox.value())

            self.mpl_ti_widget.draw()

        if sender == self.dpci_vminSpinBox or sender == self.dpci_vmaxSpinBox:
            self.dpci.set_clim(vmin=self.dpci_vminSpinBox.value(),vmax=self.dpci_vmaxSpinBox.value())

            self.mpl_dpci_widget.draw()

        if sender == self.dfi_vminSpinBox or sender == self.dfi_vmaxSpinBox:
            self.dfi.set_clim(vmin=self.dfi_vminSpinBox.value(),vmax=self.dfi_vmaxSpinBox.value())

            self.mpl_dfi_widget.draw()

        if sender == self.dfi_color_Combo or sender == self.dpci_color_Combo or sender == self.ti_color_Combo:
            if sender == self.ti_color_Combo:
                #self.ti_dat.set_cmap(cm_ti)
                self.dpci_color_Combo.setCurrentIndex(self.ti_color_Combo.currentIndex())
                self.dfi_color_Combo.setCurrentIndex(self.ti_color_Combo.currentIndex())

            if sender == self.dpci_color_Combo:
                #self.dpci_dat.set_cmap(cm_dpci)
                self.ti_color_Combo.setCurrentIndex(self.dpci_color_Combo.currentIndex())
                self.dfi_color_Combo.setCurrentIndex(self.dpci_color_Combo.currentIndex())

            if sender == self.dfi_color_Combo:
                #self.dfi_dat.set_cmap(cm_dfi)
                self.ti_color_Combo.setCurrentIndex(self.dfi_color_Combo.currentIndex())
                self.dpci_color_Combo.setCurrentIndex(self.dfi_color_Combo.currentIndex())
            cm_ti=self.cmap_list[self.ti_color_Combo.currentIndex()]
            cm_dpci=self.cmap_list[self.dpci_color_Combo.currentIndex()]
            cm_dfi=self.cmap_list[self.dfi_color_Combo.currentIndex()]
            self.ti.set_cmap(cm_ti)
            self.ti_dat.set_cmap(cm_ti)
            self.ti_cbar.update_bruteforce(self.ti)
            self.mpl_ti_widget.draw()
            self.mpl_ti_img_dat_widget.draw()
            self.dpci.set_cmap(cm_dpci)
            self.dpci_dat.set_cmap(cm_dpci)
            self.dpci_cbar.update_bruteforce(self.dpci)
            self.mpl_dpci_img_dat_widget.draw()
            self.mpl_dpci_widget.draw()
            self.dfi.set_cmap(cm_dfi)
            self.dfi_dat.set_cmap(cm_dfi)
            self.dfi_cbar.update_bruteforce(self.dfi)
            self.mpl_dfi_img_dat_widget.draw()
            self.mpl_dfi_widget.draw()
            
            
            
    def line_handling(self):
        self.ti_line_Button.setChecked(True)
        self.dpci_line_Button.setChecked(True)
        self.dfi_line_Button.setChecked(True)
        if self.ti_osc_line_Button.text()!="Show Oscillation":
            self.ti_osc_line_Button.click()
        if self.dpci_osc_line_Button.text()!="Show Oscillation":
            self.dpci_osc_line_Button.click()
        if self.dfi_osc_line_Button.text()!="Show Oscillation":
            self.dfi_osc_line_Button.click()
        try:
            self.multi_line._exit()
            #self.dpci_line._exit()
            #self.dfi_line._exit()
        except:
            pass
            
    
        if self.ti_pixel_Button.isChecked() == True:
            self.ti_pixel_Button.setChecked(False)
        if self.ti_zoom_Button.isChecked() == True:
            a,b,c,d=self.ti_zoom._exit()
            self.ti_zoom_Button.setChecked(False)
        if self.dpci_pixel_Button.isChecked() == True:
            self.dpci_pixel_Button.setChecked(False)
        if self.dpci_zoom_Button.isChecked() == True:
            a,b,c,d=self.dpci_zoom._exit()
            self.dpci_zoom_Button.setChecked(False)
            #if self.ti_toolbar._active != "ZOOM":
                #self.ti_toolbar.zoom()
        if self.dfi_pixel_Button.isChecked() == True:
            self.dfi_pixel_Button.setChecked(False)
        if self.dfi_zoom_Button.isChecked() == True:
            a,b,c,d=self.dfi_zoom._exit()
            self.dfi_zoom_Button.setChecked(False)
            
        ax =self.mpl_ti_widget.axes
        self.multi_line=LINE(self.mpl_ti_widget.axes,ax2=self.mpl_dpci_widget.axes,ax3=self.mpl_dfi_widget.axes)
        #self.dpci_line=None
        #self.dfi_line=None
        #self.connect(self.multi_line,QtCore.SIGNAL('line'),self.line_show)
        self.multi_line.lineSignal.connect(self.line_show)
        self.mpl_ti_osc_dat_widget.axes.figure.canvas.mpl_disconnect(self.ti_con1)
        self.mpl_ti_widget.axes.figure.canvas.mpl_disconnect(self.ti_con2)
        self.mpl_dpci_osc_dat_widget.axes.figure.canvas.mpl_disconnect(self.dpci_con1)
        self.mpl_dpci_widget.axes.figure.canvas.mpl_disconnect(self.dpci_con2)
        self.mpl_dfi_osc_dat_widget.axes.figure.canvas.mpl_disconnect(self.dfi_con1)
        self.mpl_dfi_widget.axes.figure.canvas.mpl_disconnect(self.dfi_con2)

   
        
        """        
            #if self.ti_toolbar._active != "ZOOM":
                #self.ti_toolbar.zoom()
        ax =self.mpl_dpci_widget.axes
        self.dpci_line=LINE(ax,ax2=self.mpl_ti_widget.axes,ax3=self.mpl_dfi_widget.axes)
        #self.ti_line=None
        #self.dfi_line=None
        self.connect(self.dpci_line,QtCore.SIGNAL('line'),self.line_show)
        
    
        if self.dfi_pixel_Button.isChecked() == True:
            self.dfi_pixel_Button.setChecked(False)
        if self.dfi_zoom_Button.isChecked() == True:
            a,b,c,d=self.dfi_zoom._exit()
            self.dfi_zoom_Button.setChecked(False)
                
            #if self.ti_toolbar._active != "ZOOM":
                #self.ti_toolbar.zoom()
        ax =self.mpl_dfi_widget.axes
        self.dfi_line=LINE(ax,ax2=self.mpl_ti_widget.axes,ax3=self.mpl_dpci_widget.axes)
        #self.dpci_line=None
        #self.ti_line=None
        self.connect(self.dfi_line,QtCore.SIGNAL('line'),self.line_show)
        
        """
        

    def line_show(self,pix_list):
        
        
        dist=np.sqrt((pix_list[2]-pix_list[3])**2+(pix_list[4]-pix_list[5])**2)
        self.pix_list=[pix_list[2],pix_list[4],pix_list[3],pix_list[5]]
        self.dist_list=np.linspace(0,dist,1000)
        self.z_ti = map_coordinates(self.TI,np.vstack((pix_list[1],pix_list[0])))
       
        self.z_dpci = map_coordinates(self.DPC,np.vstack((pix_list[1],pix_list[0])))
        
        self.z_dfi = map_coordinates(self.DFI,np.vstack((pix_list[1],pix_list[0])))
        
        self.mpl_ti_line_widget.axes.clear()       
        self.mpl_ti_line_widget.axes.plot(self.dist_list,self.z_ti,'k-',label="Line Profile")
        self.mpl_ti_line_widget.axes.set_ylabel("TI Signal")
        self.mpl_ti_line_widget.axes.set_xlabel("Distance in Pixel")
        self.mpl_ti_line_widget.axes.set_title("Line Profile from Pixel("+str(int(pix_list[2]))+", "+str(int(pix_list[4]))+") to ("+str(int(pix_list[3]))+", "+str(int(pix_list[5]))+") ")
        self.mpl_ti_line_widget.axes.legend(fontsize=8,loc=0,frameon=False,ncol=2)
        self.mpl_ti_line_widget.draw()
        
        self.mpl_dpci_line_widget.axes.clear()       
        self.mpl_dpci_line_widget.axes.plot(self.dist_list,self.z_dpci,'k-',label="Line Profile")
        self.mpl_dpci_line_widget.axes.set_ylabel("DPCI Signal")
        self.mpl_dpci_line_widget.axes.set_xlabel("Distance in Pixel")
        self.mpl_dpci_line_widget.axes.set_title("Line Profile from Pixel("+str(int(pix_list[2]))+", "+str(int(pix_list[4]))+") to ("+str(int(pix_list[3]))+", "+str(int(pix_list[5]))+") ")
        self.mpl_dpci_line_widget.axes.legend(fontsize=8,loc=0,frameon=False,ncol=2)
        self.mpl_dpci_line_widget.draw()
        
        self.mpl_dfi_line_widget.axes.clear()       
        self.mpl_dfi_line_widget.axes.plot(self.dist_list,self.z_dfi,'k-',label="Line Profile")
        self.mpl_dfi_line_widget.axes.set_ylabel("DFI Signal")
        self.mpl_dfi_line_widget.axes.set_xlabel("Distance in Pixel")
        self.mpl_dfi_line_widget.axes.set_title("Line Profile from Pixel("+str(int(pix_list[2]))+", "+str(int(pix_list[4]))+") to ("+str(int(pix_list[3]))+", "+str(int(pix_list[5]))+") ")
        self.mpl_dfi_line_widget.axes.legend(fontsize=8,loc=0,frameon=False,ncol=2)
        self.mpl_dfi_line_widget.draw()

    
    def pixel_handling(self):
#==============================================================================
#       pixel_handling:     Called by self.ti_pixel_Button, self.dpci_pixel_Button or self.dfi_pixel_Button
#
#                           Controls the connections necessary for changing the oscillation plots
#==============================================================================
        self.ti_pixel_Button.setChecked(True)
        self.dpci_pixel_Button.setChecked(True)
        self.dfi_pixel_Button.setChecked(True)
        if self.ti_osc_line_Button.text()=="Show Oscillation":
            self.ti_osc_line_Button.click()
        if self.dpci_osc_line_Button.text()=="Show Oscillation":
            self.dpci_osc_line_Button.click()
        if self.dfi_osc_line_Button.text()=="Show Oscillation":
            self.dfi_osc_line_Button.click()
   
        if self.ti_zoom_Button.isChecked() == True:
            a,b,c,d=self.ti_zoom._exit()
        if self.ti_line_Button.isChecked() == True:
            self.multi_line._exit()
        self.ti_zoom_Button.setChecked(False)
        self.ti_line_Button.setChecked(False)
        self.ti_con1=self.mpl_ti_osc_dat_widget.axes.figure.canvas.mpl_connect('button_press_event', self.on_click)
        self.ti_con2=self.mpl_ti_widget.axes.figure.canvas.mpl_connect('button_press_event', self.on_click)
        
        #if self.ti_toolbar._active == "ZOOM":
        #    self.ti_toolbar.zoom()
    
        

   
        if self.dpci_zoom_Button.isChecked() == True:
            a,b,c,d=self.dpci_zoom._exit()
        #if self.dpci_line_Button.isChecked() == True:
            #self.dpci_line._exit()
        self.dpci_zoom_Button.setChecked(False)
        self.dpci_line_Button.setChecked(False)
        self.dpci_con1=self.mpl_dpci_osc_dat_widget.axes.figure.canvas.mpl_connect('button_press_event', self.on_click)
        self.dpci_con2=self.mpl_dpci_widget.axes.figure.canvas.mpl_connect('button_press_event', self.on_click)
        
        #if self.dpci_toolbar._active == "ZOOM":
            #self.dpci_toolbar.zoom()
    


    
        if self.dfi_zoom_Button.isChecked() == True:
            a,b,c,d=self.dfi_zoom._exit()
        #if self.dfi_line_Button.isChecked() == True:
            #self.dfi_line._exit()
        self.dfi_zoom_Button.setChecked(False)
        self.dfi_line_Button.setChecked(False)
        self.dfi_con1=self.mpl_dfi_osc_dat_widget.axes.figure.canvas.mpl_connect('button_press_event', self.on_click)
        self.dfi_con2=self.mpl_dfi_widget.axes.figure.canvas.mpl_connect('button_press_event', self.on_click)
        #if self.dfi_toolbar._active == "ZOOM":
            #self.dfi_toolbar.zoom()
        
            

    def zoom_handling(self):
#==============================================================================
#       zoom_handling:      Called by self.ti_zoom_Button, self.dpci_zoom_Button or self.dfi_zoom_Button
#
#                           Controls the connections necessary for zooming in the TI, DPCI and DFI
#==============================================================================
        self.ti_zoom_Button.setChecked(True)
        self.dpci_zoom_Button.setChecked(True)
        self.dfi_zoom_Button.setChecked(True)
        if self.ti_pixel_Button.isChecked() == True:
            self.ti_pixel_Button.setChecked(False)
        if self.ti_line_Button.isChecked() == True:
            self.multi_line._exit()
            self.ti_line_Button.setChecked(False)
        ax =self.mpl_ti_widget.axes
        self.ti_zoom=ROI(ax,fin_col=False)
        #self.connect(self.ti_zoom,QtCore.SIGNAL('zoom'),self.zoom_show)
        self.ti_zoom.zoomSignal.connect(self.zoom_show)
        self.mpl_ti_osc_dat_widget.axes.figure.canvas.mpl_disconnect(self.ti_con1)
        self.mpl_ti_widget.axes.figure.canvas.mpl_disconnect(self.ti_con2)
        #else :
            #self.ti_pixel_Button.click()
    
        if self.dpci_pixel_Button.isChecked() == True:
            self.dpci_pixel_Button.setChecked(False)
            #if self.dpci_toolbar._active != "ZOOM":
                #self.dpci_toolbar.zoom()
        if self.dpci_line_Button.isChecked() == True:
            #self.multi_line._exit()
            self.dpci_line_Button.setChecked(False)
        ax =self.mpl_dpci_widget.axes
        self.dpci_zoom=ROI(ax,fin_col=False)
        #self.connect(self.dpci_zoom,QtCore.SIGNAL('zoom'),self.zoom_show)
        self.dpci_zoom.zoomSignal.connect(self.zoom_show)
        self.mpl_dpci_osc_dat_widget.axes.figure.canvas.mpl_disconnect(self.dpci_con1)
        self.mpl_dpci_widget.axes.figure.canvas.mpl_disconnect(self.dpci_con2)
        #else :
            #self.dpci_pixel_Button.click()
    
        if self.dfi_pixel_Button.isChecked() == True:
            self.dfi_pixel_Button.setChecked(False)
            #if self.dfi_toolbar._active != "ZOOM":
                #self.dfi_toolbar.zoom()
        if self.dfi_line_Button.isChecked() == True:
            #self.multi_line._exit()
            self.dfi_line_Button.setChecked(False)
        ax =self.mpl_dfi_widget.axes
        self.dfi_zoom=ROI(ax,fin_col=False)
        #self.connect(self.dfi_zoom,QtCore.SIGNAL('zoom'),self.zoom_show)
        self.dfi_zoom.zoomSignal.connect(self.zoom_show)
        self.mpl_dfi_osc_dat_widget.axes.figure.canvas.mpl_disconnect(self.dfi_con1)
        self.mpl_dfi_widget.axes.figure.canvas.mpl_disconnect(self.dfi_con2)
        #else :
            #self.dfi_pixel_Button.click()
    def zoom_show(self,zoom_list):
#==============================================================================
#       zoom_show:      Called by self.zoom_handling
#
#                       Zooms the TI, DPCI and DFI to the area selected.
#==============================================================================
        self.mpl_ti_widget.axes.set_xlim([zoom_list[2],zoom_list[3]])
        self.mpl_ti_widget.axes.set_ylim([zoom_list[1],zoom_list[0]])
        self.mpl_ti_widget.draw()
        histogram = np.histogram(self.TI[zoom_list[0]:zoom_list[1],zoom_list[2]:zoom_list[3]], bins=500, range=(0,2))
        bins = histogram[1]
        central_bins = (bins[1:] + bins[:-1]) / 2.
        self.mpl_ti_hist_widget.axes.clear()
        self.mpl_ti_hist_widget.axes.fill_between(central_bins,0, histogram[0],color="black")
        self.mpl_ti_hist_widget.axes.set_xlabel("Grayvalue")
        self.mpl_ti_hist_widget.axes.set_ylabel("Number of Pixels")
        self.mpl_ti_hist_widget.axes.set_ylim([0,max(histogram[0])])
        self.mpl_ti_hist_widget.draw()
    #def dpci_zoom_show(self,zoom_list):

        self.mpl_dpci_widget.axes.set_xlim([zoom_list[2],zoom_list[3]])
        self.mpl_dpci_widget.axes.set_ylim([zoom_list[1],zoom_list[0]])
        self.mpl_dpci_widget.draw()
        histogram = np.histogram(self.DPC[zoom_list[0]:zoom_list[1],zoom_list[2]:zoom_list[3]], bins=500, range=(-np.pi,np.pi))
        bins = histogram[1]
        central_bins = (bins[1:] + bins[:-1]) / 2.
        self.mpl_dpci_hist_widget.axes.clear()
        self.mpl_dpci_hist_widget.axes.fill_between(central_bins,0, histogram[0],color="black")
        self.mpl_dpci_hist_widget.axes.set_xlabel("Grayvalue")
        self.mpl_dpci_hist_widget.axes.set_ylabel("Number of Pixels")
        self.mpl_dpci_hist_widget.axes.set_ylim([0,max(histogram[0])])
        self.mpl_dpci_hist_widget.draw()
    #def dfi_zoom_show(self,zoom_list):

        self.mpl_dfi_widget.axes.set_xlim([zoom_list[2],zoom_list[3]])
        self.mpl_dfi_widget.axes.set_ylim([zoom_list[1],zoom_list[0]])
        self.mpl_dfi_widget.draw()
        histogram = np.histogram(self.DFI[zoom_list[0]:zoom_list[1],zoom_list[2]:zoom_list[3]], bins=500, range=(0,2))
        bins = histogram[1]
        central_bins = (bins[1:] + bins[:-1]) / 2.
        self.mpl_dfi_hist_widget.axes.clear()
        self.mpl_dfi_hist_widget.axes.fill_between(central_bins,0, histogram[0],color="black")
        self.mpl_dfi_hist_widget.axes.set_xlabel("Grayvalue")
        self.mpl_dfi_hist_widget.axes.set_ylabel("Number of Pixels")
        self.mpl_dfi_hist_widget.axes.set_ylim([0,max(histogram[0])])
        self.mpl_dfi_hist_widget.draw()


    def unzoom_handling(self):
#==============================================================================
#       zoom_show:      Called by self.ti_unzoom_Button, self.dpci_unzoom_Button or self.dfi_unzoom_Button
#
#                       Unzooms the TI, DPCI and DFI.
#==============================================================================
        #a,b,c,d=self.zoom._exit()
        sender=self.sender()
        self.ti_zoom_Button.setChecked(False)
        self.dpci_zoom_Button.setChecked(False)
        self.dfi_zoom_Button.setChecked(False)
        try:
            a,b,c,d=self.ti_zoom._exit()
        except:
            pass
        try:
            a,b,c,d=self.dpci_zoom._exit()
        except:
            pass
        try:
            a,b,c,d=self.dfi_zoom._exit()
        except:
            pass
        self.ti_pixel_Button.click()
        self.dpci_pixel_Button.click()
        self.dfi_pixel_Button.click()
        #if sender==self.ti_unzoom_Button:
        #self.ti_toolbar.home()
        y,x=self.TI.shape
        self.mpl_ti_widget.axes.set_xlim([0,x])
        self.mpl_ti_widget.axes.set_ylim([y,0])
        self.mpl_ti_widget.draw()
        histogram = np.histogram(self.TI, bins=500, range=(0,2))
        bins = histogram[1]
        central_bins = (bins[1:] + bins[:-1]) / 2.
        self.mpl_ti_hist_widget.axes.clear()
        self.mpl_ti_hist_widget.axes.fill_between(central_bins,0, histogram[0],color="black")
        self.mpl_ti_hist_widget.axes.set_xlabel("Grayvalue")
        self.mpl_ti_hist_widget.axes.set_ylabel("Number of Pixels")
        self.mpl_ti_hist_widget.axes.set_ylim([0,max(histogram[0])])

        self.mpl_ti_hist_widget.draw()

        #if sender==self.dpci_unzoom_Button:
        #self.dpci_toolbar.home()
        y,x=self.DPC.shape
        self.mpl_dpci_widget.axes.set_xlim([0,x])
        self.mpl_dpci_widget.axes.set_ylim([y,0])
        self.mpl_dpci_widget.draw()
        histogram = np.histogram(self.DPC, bins=500, range=(-np.pi,np.pi))
        bins = histogram[1]
        central_bins = (bins[1:] + bins[:-1]) / 2.
        self.mpl_dpci_hist_widget.axes.clear()
        self.mpl_dpci_hist_widget.axes.fill_between(central_bins,0, histogram[0],color="black")
        self.mpl_dpci_hist_widget.axes.set_xlabel("Grayvalue")
        self.mpl_dpci_hist_widget.axes.set_ylabel("Number of Pixels")
        self.mpl_dpci_hist_widget.axes.set_ylim([0,max(histogram[0])])
        self.mpl_dpci_hist_widget.draw()
        #if sender==self.dfi_unzoom_Button:
        #self.dfi_toolbar.home()
        y,x=self.DFI.shape
        self.mpl_dfi_widget.axes.set_xlim([0,x])
        self.mpl_dfi_widget.axes.set_ylim([y,0])
        self.mpl_dfi_widget.draw()
        histogram = np.histogram(self.DFI, bins=500, range=(0,2))
        bins = histogram[1]
        central_bins = (bins[1:] + bins[:-1]) / 2.
        self.mpl_dfi_hist_widget.axes.clear()
        self.mpl_dfi_hist_widget.axes.fill_between(central_bins,0, histogram[0],color="black")
        self.mpl_dfi_hist_widget.axes.set_xlabel("Grayvalue")
        self.mpl_dfi_hist_widget.axes.set_ylabel("Number of Pixels")
        self.mpl_dfi_hist_widget.axes.set_ylim([0,max(histogram[0])])
        self.mpl_dfi_hist_widget.draw()
    def osc_line_switch(self):
#==============================================================================
#       osc_line_switch:   Called by self.ti_hist_dat_Button, self.dpci_hist_dat_Button or self.dfi_hist_dat_Button
#
#                           Switches between the raw data image and the histogramm.
#==============================================================================
        sender=self.sender()

        if sender == self.ti_osc_line_Button:
            #cm_ti=self.cmap_list[self.ti_color_Combo.currentIndex()]
            if self.ti_osc_line_Button.text()=="Show Oscillation":
                self.mpl_ti_osc_dat_widget.setVisible(True)
                self.mpl_ti_line_widget.setVisible(False)
                self.ti_osc_line_Button.setText("Show Line Profile")
            elif self.ti_osc_line_Button.text()=="Show Line Profile":
                self.mpl_ti_osc_dat_widget.setVisible(False)
                self.mpl_ti_line_widget.setVisible(True)
                self.ti_osc_line_Button.setText("Show Oscillation")
        elif sender == self.dpci_osc_line_Button:
            #cm_ti=self.cmap_list[self.ti_color_Combo.currentIndex()]
            if self.dpci_osc_line_Button.text()=="Show Oscillation":
                self.mpl_dpci_osc_dat_widget.setVisible(True)
                self.mpl_dpci_line_widget.setVisible(False)
                self.dpci_osc_line_Button.setText("Show Line Profile")
            elif self.dpci_osc_line_Button.text()=="Show Line Profile":
                self.mpl_dpci_osc_dat_widget.setVisible(False)
                self.mpl_dpci_line_widget.setVisible(True)
                self.dpci_osc_line_Button.setText("Show Oscillation")
        elif sender == self.dfi_osc_line_Button:
            #cm_ti=self.cmap_list[self.ti_color_Combo.currentIndex()]
            if self.dfi_osc_line_Button.text()=="Show Oscillation":
                self.mpl_dfi_osc_dat_widget.setVisible(True)
                self.mpl_dfi_line_widget.setVisible(False)
                self.dfi_osc_line_Button.setText("Show Line Profile")
            elif self.dfi_osc_line_Button.text()=="Show Line Profile":
                self.mpl_dfi_osc_dat_widget.setVisible(False)
                self.mpl_dfi_line_widget.setVisible(True)
                self.dfi_osc_line_Button.setText("Show Oscillation")
        
    def data_hist_switch(self):
#==============================================================================
#       data_hist_switch:   Called by self.ti_hist_dat_Button, self.dpci_hist_dat_Button or self.dfi_hist_dat_Button
#
#                           Switches between the raw data image and the histogramm.
#==============================================================================
        sender=self.sender()

        if sender == self.ti_hist_dat_Button:
            cm_ti=self.cmap_list[self.ti_color_Combo.currentIndex()]
            if self.ti_hist_dat_Button.text()=="Show Histogram":
                self.mpl_ti_hist_widget.setVisible(True)
                self.mpl_ti_img_dat_widget.setVisible(False)

                self.ti_hist_dat_Button.setText("Show Data Image")
            elif self.ti_hist_dat_Button.text()=="Show Data Image":
                self.mpl_ti_hist_widget.setVisible(False)
                self.mpl_ti_img_dat_widget.setVisible(True)
                self.ti_hist_dat_Button.setText("Show Histogram")
        elif sender == self.dpci_hist_dat_Button:
            cm_dpci=self.cmap_list[self.dpci_color_Combo.currentIndex()]
            if self.dpci_hist_dat_Button.text()=="Show Histogram":
                self.mpl_dpci_hist_widget.setVisible(True)
                self.mpl_dpci_img_dat_widget.setVisible(False)

                self.dpci_hist_dat_Button.setText("Show Data Image")
            elif self.dpci_hist_dat_Button.text()=="Show Data Image":
                self.mpl_dpci_hist_widget.setVisible(False)
                self.mpl_dpci_img_dat_widget.setVisible(True)
                self.dpci_hist_dat_Button.setText("Show Histogram")
        elif sender == self.dfi_hist_dat_Button:
            cm_dfi=self.cmap_list[self.dfi_color_Combo.currentIndex()]
            if self.dfi_hist_dat_Button.text()=="Show Histogram":
                self.mpl_dfi_hist_widget.setVisible(True)
                self.mpl_dfi_img_dat_widget.setVisible(False)

                self.dfi_hist_dat_Button.setText("Show Data Image")
            elif self.dfi_hist_dat_Button.text()=="Show Data Image":
                self.mpl_dfi_hist_widget.setVisible(False)
                self.mpl_dfi_img_dat_widget.setVisible(True)
                self.dfi_hist_dat_Button.setText("Show Histogram")
    def vis_roi_thread(self):
        self.genericThread = GenericThread(self.vis_roi_handling)
        self.genericThread.start()


    def vis_roi_handling(self):
#==============================================================================
#       vis_roi_handling:   Called by vis_roi_Button.
#
#                           Handles the roi in the visibility tab
#==============================================================================
        if self.vis_roi_Button.isChecked():
            self.vis_ax_dat=self.mpl_vis_dat_widget.axes.imshow(self.vis_dat_img,vmin=self.vis_vminSpinBox.value(),vmax=self.vis_vmaxSpinBox.value(),cmap=plt.cm.gray)
            self.mpl_vis_dat_widget.axes.set_title("Visibility Data")
            self.mpl_vis_dat_widget.axes.set_xlabel("Pixel (x)")
            self.mpl_vis_dat_widget.axes.set_ylabel("Pixel (y)")
            self.mpl_vis_dat_widget.draw()

            self.vis_ax_ob=self.mpl_vis_ob_widget.axes.imshow(self.vis_ob_img,vmin=self.vis_vminSpinBox.value(),vmax=self.vis_vmaxSpinBox.value(),cmap=plt.cm.gray)
            self.mpl_vis_ob_widget.axes.set_title("Visibility OB")
            self.mpl_vis_ob_widget.axes.set_xlabel("Pixel (x)")
            self.mpl_vis_ob_widget.axes.set_ylabel("Pixel (y)")
            self.mpl_vis_ob_widget.draw()
            ax1=self.mpl_vis_dat_widget.axes
            ax2=self.mpl_vis_ob_widget.axes
            self.vis_roi=ROI(ax1,ax2)

            


        else:
            roi_x0,roi_x1,roi_y0,roi_y1=self.vis_roi._exit()

            
            self.vis_mean_dat_Box.setText(str(np.around(np.mean(self.vis_dat_img[roi_y0:roi_y1,roi_x0:roi_x1]),2)))
            self.vis_mean_ob_Box.setText(str(np.around(np.mean(self.vis_ob_img[roi_y0:roi_y1,roi_x0:roi_x1]),2)))
    def phase_roi_thread(self):
        self.genericThread = GenericThread(self.phase_roi_handling)
        self.genericThread.start()

    def phase_roi_handling(self):
#==============================================================================
#      phase_roi_handling:   Called by phase_roi_Button.
#
#                            Handles the roi in the phase tab
#==============================================================================
        if self.phase_roi_Button.isChecked():
            self.phase_ax_dat=self.mpl_phase_dat_widget.axes.imshow(self.phase_dat_img,vmin=self.phase_vminSpinBox.value(),vmax=self.phase_vmaxSpinBox.value(),cmap=plt.cm.gray)
            self.mpl_phase_dat_widget.axes.set_title("Phase Data")
            self.mpl_phase_dat_widget.axes.set_xlabel("Pixel (x)")
            self.mpl_phase_dat_widget.axes.set_ylabel("Pixel (y)")
            self.mpl_phase_dat_widget.draw()

            self.phase_ax_ob=self.mpl_phase_ob_widget.axes.imshow(self.phase_ob_img,vmin=self.phase_vminSpinBox.value(),vmax=self.phase_vmaxSpinBox.value(),cmap=plt.cm.gray)
            self.mpl_phase_ob_widget.axes.set_title("Phase OB")
            self.mpl_phase_ob_widget.axes.set_xlabel("Pixel (x)")
            self.mpl_phase_ob_widget.axes.set_ylabel("Pixel (y)")
            self.mpl_phase_ob_widget.draw()
            ax1=self.mpl_phase_dat_widget.axes
            ax2=self.mpl_phase_ob_widget.axes
            self.phase_roi=ROI(ax1,ax2)

            


        else:
            roi_x0,roi_x1,roi_y0,roi_y1=self.phase_roi._exit()

            
            self.phase_mean_dat_Box.setText(str(np.around(np.mean(self.phase_dat_img[roi_y0:roi_y1,roi_x0:roi_x1]),2)))
            self.phase_mean_ob_Box.setText(str(np.around(np.mean(self.phase_ob_img[roi_y0:roi_y1,roi_x0:roi_x1]),2)))

    def replot_vis(self):
#==============================================================================
#      replot_vis:      Called by changing the limits in the visibility tab
#
#                       Replots the image with the limits
#==============================================================================
        
        self.vis_ax_dat.set_clim(vmin=self.vis_vminSpinBox.value(),vmax=self.vis_vmaxSpinBox.value())
        self.vis_ax_ob.set_clim(vmin=self.vis_vminSpinBox.value(),vmax=self.vis_vmaxSpinBox.value())
        
        self.mpl_vis_dat_widget.draw()
        self.mpl_vis_ob_widget.draw()

    def replot_phase(self):
#==============================================================================
#      replot_phase:      Called by changing the limits in the phase tab
#
#                         Replots the image with the limits
#==============================================================================
        
        self.phase_ax_dat.set_clim(vmin=self.phase_vminSpinBox.value(),vmax=self.phase_vmaxSpinBox.value())
        self.phase_ax_ob.set_clim(vmin=self.phase_vminSpinBox.value(),vmax=self.phase_vmaxSpinBox.value())
        
        self.mpl_phase_dat_widget.draw()
        self.mpl_phase_ob_widget.draw()

    def save_oscillation_handling(self,multi_calc=None):
        if multi_calc != None:
            sender = self.ti_save_Button
        else:
            sender = self.sender()
        if sender == self.ti_save_Button:
            fname=str(self.result_dir_lineEdit.text())+"Data_Oscillation ("+str(self.file_id_lineEdit.text())+") Pixel("+str(self.ti_osc_pix[0])+", "+str(self.ti_osc_pix[1])+").txt"
        elif sender == self.dpci_save_Button:
            fname=str(self.result_dir_lineEdit.text())+"Data_Oscillation ("+str(self.file_id_lineEdit.text())+") Pixel("+str(self.dpci_osc_pix[0])+", "+str(self.dpci_osc_pix[1])+").txt"
        elif sender == self.dfi_save_Button:
            fname=str(self.result_dir_lineEdit.text())+"Data_Oscillation ("+str(self.file_id_lineEdit.text())+") Pixel("+str(self.dfi_osc_pix[0])+", "+str(self.dfi_osc_pix[1])+").txt"

        if os.path.isfile(str(fname)) == True:
            if self.multi_igno_Checkbox.isChecked() ==False:
                self.overwrite_warning = QtWidgets.QMessageBox(self)
                self.overwrite_warning.setWindowTitle("YOYO-ANGEL")
                self.overwrite_warning .setStandardButtons(QtWidgets.QMessageBox.Save|QtWidgets.QMessageBox.Cancel)
                #self.dialog.setStandardButtons(QtWidgets.QMessageBox.Abort)
                self.overwrite_warning .setIcon(QtWidgets.QMessageBox.Warning)
                self.overwrite_warning .setText("Warning! Continuing will overwrite a file")

                pressed=self.overwrite_warning .exec_()
                
                if pressed == QtWidgets.QMessageBox.Save:
                    if sender == self.ti_save_Button:
                        osc_plot=self.mpl_ti_osc_dat_widget.figure
                        salo.save_oscillation(self.result_dir_lineEdit.text(),osc_plot,self.ti_osc_raw,self.ti_osc_par_dat,self.ti_osc_par_ob,self.load_data_list,self.load_ob_list,self.load_dc_list,self.ti_osc_pix,self.roi_list,self.file_id_lineEdit.text())
                    elif sender == self.dpci_save_Button:
                        osc_plot=self.mpl_dpci_osc_dat_widget.figure
                        salo.save_oscillation(self.result_dir_lineEdit.text(),osc_plot,self.dpci_osc_raw,self.dpci_osc_par_dat,self.dpci_osc_par_ob,self.load_data_list,self.load_ob_list,self.load_dc_list,self.dpci_osc_pix,self.roi_list,self.file_id_lineEdit.text())
                    elif sender == self.dfi_save_Button:
                        osc_plot=self.mpl_dfi_osc_dat_widget.figure
                        salo.save_oscillation(self.result_dir_lineEdit.text(),osc_plot,self.dfi_osc_raw,self.dfi_osc_par_dat,self.dfi_osc_par_ob,self.load_data_list,self.load_ob_list,self.load_dc_list,self.dfi_osc_pix,self.roi_list,self.file_id_lineEdit.text())

                    if self.multi_Checkbox.isChecked()== False:
                        self.save_msg = QtWidgets.QMessageBox(self)
                        self.save_msg.setWindowTitle("yoyo-ANGEL")
                        self.save_msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                        self.save_msg.setIcon(QtWidgets.QMessageBox.Information)
                        self.save_msg.setText("Files have been saved")
                        self.save_msg.exec_()
        else:
            if sender == self.ti_save_Button:
                osc_plot=self.mpl_ti_osc_dat_widget.figure
                salo.save_oscillation(self.result_dir_lineEdit.text(),osc_plot,self.ti_osc_raw,self.ti_osc_par_dat,self.ti_osc_par_ob,self.load_data_list,self.load_ob_list,self.load_dc_list,self.ti_osc_pix,self.roi_list,self.file_id_lineEdit.text())
            elif sender == self.dpci_save_Button:
                salo.osc_plot=self.mpl_dpci_osc_dat_widget.figure
                save_oscillation(self.result_dir_lineEdit.text(),osc_plot,self.dpci_osc_raw,self.dpci_osc_par_dat,self.dpci_osc_par_ob,self.load_data_list,self.load_ob_list,self.load_dc_list,self.dpci_osc_pix,self.roi_list,self.file_id_lineEdit.text())
            elif sender == self.dfi_save_Button:
                salo.osc_plot=self.mpl_dfi_osc_dat_widget.figure
                save_oscillation(self.result_dir_lineEdit.text(),osc_plot,self.dfi_osc_raw,self.dfi_osc_par_dat,self.dfi_osc_par_ob,self.load_data_list,self.load_ob_list,self.load_dc_list,self.dfi_osc_pix,self.roi_list,self.file_id_lineEdit.text())

            if self.multi_Checkbox.isChecked()== False:
                self.save_msg = QtWidgets.QMessageBox(self)
                self.save_msg.setWindowTitle("yoy1-ANGEL")
                self.save_msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                self.save_msg.setIcon(QtWidgets.QMessageBox.Information)
                self.save_msg.setText("Files have been saved")
                self.save_msg.exec_()
                
    def save_line_handling(self):

        sender = self.sender()
        if sender == self.ti_line_save_Button:
            fname=str(self.result_dir_lineEdit.text())+"TI_Line_Profile ("+str(self.file_id_lineEdit.text())+") Pixel("+str(self.ti_osc_pix[0])+", "+str(self.ti_osc_pix[1])+").txt"
        elif sender == self.dpci_line_save_Button:
            fname=str(self.result_dir_lineEdit.text())+"DPCI_Line_Profile ("+str(self.file_id_lineEdit.text())+") Pixel("+str(self.dpci_osc_pix[0])+", "+str(self.dpci_osc_pix[1])+").txt"
        elif sender == self.dfi_line_save_Button:
            fname=str(self.result_dir_lineEdit.text())+"DFI_Line_Profile ("+str(self.file_id_lineEdit.text())+") Pixel("+str(self.dfi_osc_pix[0])+", "+str(self.dfi_osc_pix[1])+").txt"

        if os.path.isfile(str(fname)) == True:
            if self.multi_igno_Checkbox.isChecked() ==False:
                self.overwrite_warning = QtWidgets.QMessageBox(self)
                self.overwrite_warning.setWindowTitle("yeah-ANGEL")
                self.overwrite_warning .setStandardButtons(QtWidgets.QMessageBox.Save|QtWidgets.QMessageBox.Cancel)
                #self.dialog.setStandardButtons(QtWidgets.QMessageBox.Abort)
                self.overwrite_warning .setIcon(QtWidgets.QMessageBox.Warning)
                self.overwrite_warning .setText("Warning! Continuing will overwrite a file")

                pressed=self.overwrite_warning .exec_()
                
                if pressed == QtWidgets.QMessageBox.Save:
                    if sender == self.ti_line_save_Button:
                        line_plot=self.mpl_ti_line_widget.figure
                        salo.save_line(self.result_dir_lineEdit.text(),"TI",line_plot,self.z_ti,self.dist_list,self.pix_list,self.load_data_list,self.load_ob_list,self.load_dc_list,self.roi_list,self.file_id_lineEdit.text())
                    elif sender == self.dpci_line_save_Button:
                        line_plot=self.mpl_dpci_line_widget.figure
                        salo.save_line(self.result_dir_lineEdit.text(),"DPCI",line_plot,self.z_dpci,self.dist_list,self.pix_list,self.load_data_list,self.load_ob_list,self.load_dc_list,self.roi_list,self.file_id_lineEdit.text())
                    elif sender == self.dfi_line_save_Button:
                        line_plot=self.mpl_dfi_line_widget.figure
                        salo.save_line(self.result_dir_lineEdit.text(),"DFI",line_plot,self.z_dfi,self.dist_list,self.pix_list,self.load_data_list,self.load_ob_list,self.load_dc_list,self.roi_list,self.file_id_lineEdit.text())

                    if self.multi_Checkbox.isChecked()== False:
                        self.save_msg = QtWidgets.QMessageBox(self)
                        self.save_msg.setWindowTitle("youf-ANGEL")
                        self.save_msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                        self.save_msg.setIcon(QtWidgets.QMessageBox.Information)
                        self.save_msg.setText("Files have been saved")
                        self.save_msg.exec_()
        else:
            if sender == self.ti_line_save_Button:
                line_plot=self.mpl_ti_line_widget.figure
                salo.save_line(self.result_dir_lineEdit.text(),"TI",line_plot,self.z_ti,self.dist_list,self.pix_list,self.load_data_list,self.load_ob_list,self.load_dc_list,self.roi_list,self.file_id_lineEdit.text())
            elif sender == self.dpci_line_save_Button:
                line_plot=self.mpl_dpci_line_widget.figure
                salo.save_line(self.result_dir_lineEdit.text(),"DPCI",line_plot,self.z_dpci,self.dist_list,self.pix_list,self.load_data_list,self.load_ob_list,self.load_dc_list,self.roi_list,self.file_id_lineEdit.text())
            elif sender == self.dfi_line_save_Button:
                line_plot=self.mpl_dfi_line_widget.figure
                salo.save_line(self.result_dir_lineEdit.text(),"DFI",line_plot,self.z_dfi,self.dist_list,self.pix_list,self.load_data_list,self.load_ob_list,self.load_dc_list,self.roi_list,self.file_id_lineEdit.text())
            if self.multi_Checkbox.isChecked()== False:
                self.save_msg = QtWidgets.QMessageBox(self)
                self.save_msg.setWindowTitle("via-ANGEL")
                self.save_msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                self.save_msg.setIcon(QtWidgets.QMessageBox.Information)
                self.save_msg.setText("Files have been saved")
                self.save_msg.exec_()

    def save_img_handling(self):
        sender = self.sender()
        if sender == self.ti_save_Button2:
            fname=self.result_dir_lineEdit.text()+"TI Image ("+self.file_id_lineEdit.text()+")_Colormap_"+self.ti_color_Combo.currentText()
            save_fig=self.mpl_ti_widget.figure
        elif sender == self.dpci_save_Button2:
            fname=self.result_dir_lineEdit.text()+"DPCI Image ("+self.file_id_lineEdit.text()+")_Colormap_"+self.dpci_color_Combo.currentText()
            save_fig=self.mpl_dpci_widget.figure
        elif sender == self.dfi_save_Button2:
            fname=self.result_dir_lineEdit.text()+"DFI Image ("+self.file_id_lineEdit.text()+")_Colormap_"+self.dfi_color_Combo.currentText()
            save_fig=self.mpl_dfi_widget.figure



        #cm_ti=self.cmap_list[self.ti_color_Combo.currentIndex()]
        #ti_save=plt.imshow(self.TI,vmin=self.ti_vminSpinBox.value(),vmax=self.ti_vmaxSpinBox.value(),cmap=cm_ti)
        if os.path.isfile(str(fname)+".pdf") == True:
            if self.multi_igno_Checkbox.isChecked() ==False:
                self.overwrite_warning = QtWidgets.QMessageBox(self)
                self.overwrite_warning.setWindowTitle("vio-ANGEL")
                self.overwrite_warning .setStandardButtons(QtWidgets.QMessageBox.Save|QtWidgets.QMessageBox.Cancel)
                #self.dialog.setStandardButtons(QtWidgets.QMessageBox.Abort)
                self.overwrite_warning .setIcon(QtWidgets.QMessageBox.Warning)
                self.overwrite_warning .setText("Warning! Continuing will overwrite a file")

                pressed=self.overwrite_warning .exec_()
                
                if pressed == QtWidgets.QMessageBox.Save:
                    pdf_file=PdfPages(str(fname)+".pdf")
                    pdf_file.savefig(save_fig)
                    pdf_file.close()
                    if self.multi_Checkbox.isChecked()== False:
                        self.save_msg = QtWidgets.QMessageBox(self)
                        self.save_msg.setWindowTitle("ANGEllll")
                        self.save_msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                        self.save_msg.setIcon(QtWidgets.QMessageBox.Information)
                        self.save_msg.setText("Files have been saved")
                        self.save_msg.exec_()
        else:
            pdf_file=PdfPages(str(fname)+".pdf")
            pdf_file.savefig(save_fig)
            pdf_file.close()
            if self.multi_Checkbox.isChecked()== False:
                self.save_msg = QtWidgets.QMessageBox(self)
                self.save_msg.setWindowTitle("ANGELie")
                self.save_msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                self.save_msg.setIcon(QtWidgets.QMessageBox.Information)
                self.save_msg.setText("Files have been saved")
                self.save_msg.exec_()
        #ti_save=None


    def save_ngi_files_handling(self):

        rot_G0=self.par_rot_G0rz_DSpinBox.value()
        period_number=self.par_per_SpinBox.value()
        full_per=self.par_full_per_Combo.currentText()
        gamma_dat_par=[self.par_grail_filt_dat_thr1_SpinBox.value(),self.par_grail_filt_dat_thr2_SpinBox.value(),self.par_grail_filt_dat_thr3_SpinBox.value(),self.par_grail_filt_dat_sigma_DSpinBox.value()]
        gamma_dc_par=[self.par_grail_filt_dc_thr1_SpinBox.value(),self.par_grail_filt_dc_thr2_SpinBox.value(),self.par_grail_filt_dc_thr3_SpinBox.value(),self.par_grail_filt_dc_sigma_DSpinBox.value()]
        data_files=create_files_list(self.load_data_list)
        ob_files=create_files_list(self.load_ob_list)
        dc_files=create_files_list(self.load_dc_list)

        header=[self.im_pat_LineEdit.text(),data_files,self.ob_pat_LineEdit.text(),ob_files,self.dc_pat_LineEdit.text(),dc_files,self.im_num_SpinBox.value(),self.par_per_SpinBox.value(),
                self.par_full_per_Combo.currentText(),self.roi_list,self.sample_lineEdit.text(),self.environment_lineEdit.text(),"test",self.fit_Combo.text(),
                self.par_rot_G0rz_DSpinBox.value()]
        data=[self.TI,self.DPC,self.DFI,self.phi_ob,self.phi_data,self.vis_dat_img,self.vis_ob_img,self.a0_data,self.a0_ob]
        
        if os.path.isfile(str(self.result_dir_lineEdit.text())+"Logbook_"+str(self.file_id_lineEdit.text())+".cfg") == True:
            if self.multi_igno_Checkbox.isChecked() ==False:
                self.overwrite_warning = QtWidgets.QMessageBox(self)
                self.overwrite_warning.setWindowTitle("ANGEL-2")
                self.overwrite_warning .setStandardButtons(QtWidgets.QMessageBox.Save|QtWidgets.QMessageBox.Cancel)
                #self.dialog.setStandardButtons(QtWidgets.QMessageBox.Abort)
                self.overwrite_warning .setIcon(QtWidgets.QMessageBox.Warning)
                self.overwrite_warning .setText("Warning! Continuing will overwrite a file")

                pressed=self.overwrite_warning .exec_()
            
                if pressed == QtWidgets.QMessageBox.Save:
                    salo.save_log_file(self.result_dir_lineEdit.text(),self.load_data_list,self.load_ob_list,self.load_dc_list,"ANTARES",self.sample_lineEdit.text(),self.environment_lineEdit.text(),self.comment_plainText.toPlainText(),self.version,rot_G0,period_number,full_per,
                          self.par_bin_Combo.currentText(),self.par_bin_SpinBox.value(),self.par_median_Combo.currentText(),self.par_median_SpinBox.value(),self.par_grail_filt_dat_Combo.currentText(),gamma_dat_par,self.par_grail_filt_dc_Combo.currentText(),gamma_dc_par,self.roi_list,self.fit_Combo.text()
                          ,self.file_id_lineEdit.text())

                    salo.save_ngi_files(self.result_dir_lineEdit.text(),header,data,self.file_id_lineEdit.text())
                    if self.multi_Checkbox.isChecked()== False:
                        self.save_msg = QtWidgets.QMessageBox(self)
                        self.save_msg.setWindowTitle("ANGEL-3")
                        self.save_msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                        self.save_msg.setIcon(QtWidgets.QMessageBox.Information)
                        self.save_msg.setText("Files have been saved")
                        self.save_msg.exec_()
            elif self.multi_igno_Checkbox.isChecked() ==True:
                salo.save_log_file(self.result_dir_lineEdit.text(),self.load_data_list,self.load_ob_list,self.load_dc_list,"ANTARES",self.sample_lineEdit.text(),self.environment_lineEdit.text(),self.comment_plainText.toPlainText(),self.version,rot_G0,period_number,full_per,
                          self.par_bin_Combo.currentText(),self.par_bin_SpinBox.value(),self.par_median_Combo.currentText(),self.par_median_SpinBox.value(),self.par_grail_filt_dat_Combo.currentText(),gamma_dat_par,self.par_grail_filt_dc_Combo.currentText(),gamma_dc_par,self.roi_list,self.fit_Combo.text()
                          ,self.file_id_lineEdit.text())

                salo.save_ngi_files(self.result_dir_lineEdit.text(),header,data,self.file_id_lineEdit.text())
        else:
            salo.save_log_file(self.result_dir_lineEdit.text(),self.load_data_list,self.load_ob_list,self.load_dc_list,"ANTARES",self.sample_lineEdit.text(),self.environment_lineEdit.text(),self.comment_plainText.toPlainText(),self.version,rot_G0,period_number,full_per,
                      self.par_bin_Combo.currentText(),self.par_bin_SpinBox.value(),self.par_median_Combo.currentText(),self.par_median_SpinBox.value(),self.par_grail_filt_dat_Combo.currentText(),gamma_dat_par,self.par_grail_filt_dc_Combo.currentText(),gamma_dc_par,self.roi_list,self.fit_Combo.text(),self.file_id_lineEdit.text())

            salo.save_ngi_files(self.result_dir_lineEdit.text(),header,data,self.file_id_lineEdit.text())
            if self.multi_Checkbox.isChecked()== False:
                self.save_msg = QtWidgets.QMessageBox(self)
                self.save_msg.setWindowTitle("ANGEL-4")
                self.save_msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                self.save_msg.setIcon(QtWidgets.QMessageBox.Information)
                self.save_msg.setText("Files have been saved")
                self.save_msg.exec_()
        self.calc_state=3

    def load_files_handling(self):
        
        path=QtWidgets.QFileDialog.getOpenFileName(self,"Choose Log File to open",self.homepath)
        
        if str(path[-3:]) == "cfg":

            instrument,file_id,sample,environment,comment,data_path,data_files,ob_path,ob_files,dc_path,dc_files,per_num,full_per,rot,roi_list,gamma_dat_bool,gamma_dat_thr1,gamma_dat_thr2,gamma_dat_thr3,gamma_dat_sigma,gamma_dc_bool,gamma_dc_thr1,gamma_dc_thr2,gamma_dc_thr3,gamma_dc_sigma,median_bool,median_radius,binning_bool,binning_radius,fit=salo.load_log_file(path)
            data_files=[str(data_path)+str(x)for x in data_files]
            ob_files=[str(ob_path)+str(x)for x in ob_files]
            dc_files=[str(dc_path)+str(x)for x in dc_files]
            if os.path.isdir(str(data_path)):
                self.data_dir_lineEdit.setText(str(data_path)+str(os.path.sep))
                self.first_data_file_Combo.clear()
                self.first_data_file_Combo.addItems(data_files)
                self.last_data_file_Combo.clear()
                self.last_data_file_Combo.addItems(data_files)
                self.last_data_file_Combo.setCurrentIndex(self.last_data_file_Combo.count()-1)
                self.load_data_Button.setEnabled(True)
                self.data_list=glob.glob(str(self.data_dir_lineEdit.text())+'*.fits')
                self.data_list.sort()
            else:
                self.load_warning = QtWidgets.QMessageBox(self)
                self.load_warning.setWindowTitle("ANGES-5")
                self.load_warning.setStandardButtons(QtWidgets.QMessageBox.Ok)
                #self.dialog.setStandardButtons(QtWidgets.QMessageBox.Abort)
                self.load_warning.setIcon(QtWidgets.QMessageBox.Warning)
                self.load_warning.setText("Warning!  Data Directory not found")

                self.load_warning.exec_()
            if os.path.isdir(str(ob_path)):
                self.ob_dir_lineEdit.setText(str(ob_path)+str(os.path.sep))
                self.first_ob_file_Combo.clear()
                self.first_ob_file_Combo.addItems(ob_files)
                self.last_ob_file_Combo.clear()
                self.last_ob_file_Combo.addItems(ob_files)
                self.last_ob_file_Combo.setCurrentIndex(self.last_ob_file_Combo.count()-1)
                self.load_ob_Button.setEnabled(True)
                self.ob_list=glob.glob(str(self.ob_dir_lineEdit.text())+'*.fits')
                self.ob_list.sort()
            else:
                self.load_warning = QtWidgets.QMessageBox(self)
                self.load_warning.setWindowTitle("ANGES-6")
                self.load_warning.setStandardButtons(QtWidgets.QMessageBox.Ok)
                #self.dialog.setStandardButtons(QtWidgets.QMessageBox.Abort)
                self.load_warning.setIcon(QtWidgets.QMessageBox.Warning)
                self.load_warning.setText("Warning!  OB Directory not found")

                self.load_warning.exec_()

            if os.path.isdir(str(dc_path)):
                self.dc_dir_lineEdit.setText(str(dc_path)+str(os.path.sep))
                self.first_dc_file_Combo.clear()
                self.first_dc_file_Combo.addItems(dc_files)
                self.last_dc_file_Combo.clear()
                self.last_dc_file_Combo.addItems(dc_files)
                self.last_dc_file_Combo.setCurrentIndex(self.last_dc_file_Combo.count()-1)
                self.load_dc_Button.setEnabled(True)
                self.dc_list=glob.glob(str(self.dc_dir_lineEdit.text())+'*.fits')
                self.dc_list.sort()
            else:
                self.load_warning = QtWidgets.QMessageBox(self)
                self.load_warning.setWindowTitle("ANGES-7")
                self.load_warning.setStandardButtons(QtWidgets.QMessageBox.Ok)
                #self.dialog.setStandardButtons(QtWidgets.QMessageBox.Abort)
                self.load_warning.setIcon(QtWidgets.QMessageBox.Warning)
                self.load_warning.setText("Warning!  OB Directory not found")

                self.load_warning.exec_()
            if instrument == "ANTARES":
                self.instrument_Combo.setCurrentIndex(0)
            elif instrument == "ICON":
                self.instrument_Combo.setCurrentIndex(1)
            elif instrument == "other":
                self.instrument_Combo.setCurrentIndex(2)


            self.file_id_lineEdit.setText(str(file_id))
            self.sample_lineEdit.setText(str(sample))
            self.environment_lineEdit.setText(str(environment))
            self.comment_plainText.setPlainText(str(comment))



            self.scanned_periods_Spinbox.setValue(int(per_num))
            if full_per == True:
                self.full_per_Combo.setCurrentIndex(0)
            else:
                self.full_per_Combo.setCurrentIndex(1)

            self.rot_G0rz_DSpinbox.setValue(float(rot))
            self.update_roi(roi_list)


            if gamma_dat_bool == True:
                self.grail_filt_dat_CheckBox.setChecked(True)
            else:
                self.grail_filt_dat_CheckBox.setChecked(False)
            self.grail_filt_dat_thr1_SpinBox.setValue(int(gamma_dat_thr1))
            self.grail_filt_dat_thr2_SpinBox.setValue(int(gamma_dat_thr2))
            self.grail_filt_dat_thr3_SpinBox.setValue(int(gamma_dat_thr3))
            self.grail_filt_dat_sigma_DSpinBox.setValue(float(gamma_dat_sigma))

            if gamma_dc_bool == True:
                self.grail_filt_dc_CheckBox.setChecked(True)
            else:
                self.grail_filt_dc_CheckBox.setChecked(False)
            self.grail_filt_dc_thr1_SpinBox.setValue(int(gamma_dc_thr1))
            self.grail_filt_dc_thr2_SpinBox.setValue(int(gamma_dc_thr2))
            self.grail_filt_dc_thr3_SpinBox.setValue(int(gamma_dc_thr3))
            self.grail_filt_dc_sigma_DSpinBox.setValue(float(gamma_dc_sigma))

            if median_bool == True:
                self.median2_CheckBox.setChecked(True)

            else:
                self.median2_CheckBox.setChecked(False)
            self.median2_SpinBox.setValue(int(median_radius))

            if binning_bool == True:
                self.bin_CheckBox.setChecked(True)

            else:
                self.bin_CheckBox.setChecked(False)
            self.bin_SpinBox.setValue(int(binning_radius))

            if fit =="MAT":
                self.choose_fit_Combo.setCurrentIndex(0)
            elif fit == "FFT":
                self.choose_fit_Combo.setCurrentIndex(2)
            elif fit == "SIN":
                self.choose_fit_Combo.setCurrentIndex(1)

        else:
            self.path_warning = QtWidgets.QMessageBox(self)
            self.path_warning.setWindowTitle("ANGES-8")
            self.path_warning .setStandardButtons(QtWidgets.QMessageBox.Ok)
            #self.dialog.setStandardButtons(QtWidgets.QMessageBox.Abort)
            self.path_warning .setIcon(QtWidgets.QMessageBox.Warning)
            self.path_warning .setText("Warning! This is not a Logbook file")
            self.path_warning .exec_()

    def choose_excel(self):
        
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Excel File',self.homepath)
        #print('Test')
        #print(fname[0])
        self.excel_dir_lineEdit.setText(str(fname[0]))
        self.first_data_list,self.last_data_list,self.first_ob_list,self.last_ob_list,self.first_dc_list,self.last_dc_list,self.period_list,self.fit_list,self.multi_roi_list,self.gamma_dat,self.gamma_dat_thr1,self.gamma_dat_thr2,self.gamma_dat_thr3,self.gamma_dat_sig,self.gamma_dc,self.gamma_dc_thr1,self.gamma_dc_thr2,self.gamma_dc_thr3,self.gamma_dc_sig,self.result_list,self.file_id_list,self.sample_list,self.used_env_list,self.osc_pixel_list,self.img_per_step_list,self.rot_list,self.epi_corr_list,self.epi_corr_val_list=salo.load_excel(str(fname[0]))
        rows=np.arange(0,len(self.first_data_list))+1
        rows=[str(x) for x in rows]
        
        self.first_line_Combo.clear()
        self.last_line_Combo.clear()
        self.first_line_Combo.addItems(rows)
        self.last_line_Combo.addItems(rows)
        self.last_line_Combo.setCurrentIndex(self.last_line_Combo.count()-1)
    def multi_calc_thread(self):
        self.multi_calc_Thread = GenericThread(self.multi_calc)


        
        self.multi_calc_Thread.start()
        #self.connect(self.multi_calc_Thread,QtCore.SIGNAL("started()"),self.disable_button)
        self.multi_calc_Thread.startSignal.connect(self.disable_button)
        #self.connect(self.multi_calc_Thread,QtCore.SIGNAL("finished()"),self.enable_button)
        self.multi_calc_Thread.startSignal.connect(self.enable_button)
    def multi_calc(self):
        first_data_list=self.first_data_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        
        last_data_list=self.last_data_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        first_ob_list=self.first_ob_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        
        last_ob_list=self.last_ob_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        first_dc_list=self.first_dc_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        last_dc_list=self.last_dc_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        period_list=self.period_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        fit_list=self.fit_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        multi_roi_list=self.multi_roi_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        gamma_dat=self.gamma_dat[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        gamma_dat_thr1=self.gamma_dat_thr1[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        gamma_dat_thr2=self.gamma_dat_thr2[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        gamma_dat_thr3=self.gamma_dat_thr3[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        gamma_dat_sig=self.gamma_dat_sig[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        gamma_dc=self.gamma_dc[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        gamma_dc_thr1=self.gamma_dc_thr1[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        gamma_dc_thr2=self.gamma_dc_thr2[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        gamma_dc_thr3=self.gamma_dc_thr3[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        gamma_dc_sig=self.gamma_dc_sig[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        result_list=self.result_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        file_id_list=self.file_id_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        sample_list=self.sample_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        used_env_list=self.used_env_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        osc_pixel_list=self.osc_pixel_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        rot_list=self.rot_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        img_per_step_list=self.img_per_step_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        epi_corr=self.epi_corr_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        epi_corr_val=self.epi_corr_val_list[self.first_line_Combo.currentIndex():self.last_line_Combo.currentIndex()+1]
        
        for i in range (0,len(first_data_list)):
            
            #self.emit(QtCore.SIGNAL('set_text'),[self.row_Label,"Calculating data set with ID: "+str(file_id_list[i])])
            self.settextSignal.emit([self.row_Label,"Calculating data set with ID: "+str(file_id_list[i])])
            data_dir=first_data_list[i][0:first_data_list[i].rfind(str(os.path.sep))]
            ob_dir=first_ob_list[i][0:first_ob_list[i].rfind(str(os.path.sep))]
            dc_dir=first_dc_list[i][0:first_dc_list[i].rfind(str(os.path.sep))]
            if str(first_data_list[i][-5:])!=".fits":
                    first_data_list[i]=first_data_list[i]+".fits"
            if str(last_data_list[i][-5:])!=".fits":
                    last_data_list[i]=last_data_list[i]+".fits"

            if str(first_ob_list[i][-5:])!=".fits":
                    first_ob_list[i]=first_ob_list[i]+".fits"
            if str(last_ob_list[i][-5:])!=".fits":
                    last_ob_list[i]=last_ob_list[i]+".fits"

            if str(first_dc_list[i][-5:])!=".fits":
                    first_dc_list[i]=first_dc_list[i]+".fits"
            if str(last_dc_list[i][-5:])!=".fits":
                    last_dc_list[i]=last_dc_list[i]+".fits"
            while os.path.isfile(str(first_data_list[i])) is False or os.path.isfile(str(last_data_list[i])) is False or os.path.isfile(str(first_ob_list[i])) is False or os.path.isfile(str(last_ob_list[i])) is False or os.path.isfile(str(first_dc_list[i])) is False or os.path.isfile(str(last_dc_list[i])) is False:

                date = datetime.datetime.now()
                date = date.strftime("%Y-%m-%d %H:%M")
                msg= "Not all images availlable. Waiting for 5 minutes. Current time is: " +str(date)
                
                #self.emit(QtCore.SIGNAL('status'),[self.working,str(msg)])
                self.statusSignal.emit([self.working,str(msg)])
                time.sleep(300)
            else:
                
                
                self.calc_state=0
                self.multi_load_fin=[False,False,False]
                #self.emit(QtCore.SIGNAL('set_value'),[self.img_per_step_Spinbox,int(float(img_per_step_list[i]))])
                self.setvalueSignal.emit([self.img_per_step_Spinbox,int(float(img_per_step_list[i]))])
                #self.emit(QtCore.SIGNAL('set_value'),[self.rot_G0rz_DSpinbox,float(rot_list[i])])
                self.setvalueSignal.emit([self.rot_G0rz_DSpinbox,float(rot_list[i])])
                
                #self.emit(QtCore.SIGNAL('set_text'),[self.data_dir_lineEdit,str(data_dir)+str(os.path.sep)])
                self.settextSignal.emit([self.data_dir_lineEdit,str(data_dir)+str(os.path.sep)])
                
                self.data_list=glob.glob(str(data_dir)+str(os.path.sep)+'*.fits')
                self.data_list.sort()
                
                #self.emit(QtCore.SIGNAL('set_combo'),[self.first_data_file_Combo,str(first_data_list[i])])
                self.setcomboSignal.emit([self.first_data_file_Combo,str(first_data_list[i])])
                #self.emit(QtCore.SIGNAL('set_combo'),[self.last_data_file_Combo,str(last_data_list[i])])
                self.setcomboSignal.emit([self.last_data_file_Combo,str(last_data_list[i])])

                #self.emit(QtCore.SIGNAL('set_text'),[self.ob_dir_lineEdit,str(ob_dir)+str(os.path.sep)])
                self.settextSignal.emit([self.ob_dir_lineEdit,str(ob_dir)+str(os.path.sep)])
                
                self.ob_list=glob.glob(str(ob_dir)+str(os.path.sep)+'*.fits')
                self.ob_list.sort()
                #self.emit(QtCore.SIGNAL('set_combo'),[self.first_ob_file_Combo,str(first_ob_list[i])])
                self.setcomboSignal.emit([self.first_ob_file_Combo,str(first_ob_list[i])])
                #self.emit(QtCore.SIGNAL('set_combo'),[self.last_ob_file_Combo,str(last_ob_list[i])])
                self.setcomboSignal.emit([self.last_ob_file_Combo,str(last_ob_list[i])])
                
                
                #self.emit(QtCore.SIGNAL('set_text'),[self.dc_dir_lineEdit,str(dc_dir)+str(os.path.sep)])
                self.settextSignal.emit([self.dc_dir_lineEdit,str(dc_dir)+str(os.path.sep)])
                
                self.dc_list=glob.glob(str(dc_dir)+str(os.path.sep)+'*.fits')
                self.dc_list.sort()
                
                #self.emit(QtCore.SIGNAL('set_combo'),[self.first_dc_file_Combo,str(first_dc_list[i])])
                self.setcomboSignal.emit([self.first_dc_file_Combo,str(first_dc_list[i])])
                #self.emit(QtCore.SIGNAL('set_combo'),[self.last_dc_file_Combo,str(last_dc_list[i])])
                self.setcomboSignal.emit([self.last_dc_file_Combo,str(last_dc_list[i])])
                
                #self.emit(QtCore.SIGNAL('call_func'),[self.load_img_files,self.load_data_Button])
                self.callfuncSignal.emit([self.load_img_files,self.load_data_Button])
                
                #self.emit(QtCore.SIGNAL('call_func'),[self.load_img_files,self.load_ob_Button])
                self.callfuncSignal.emit([self.load_img_files,self.load_ob_Button])
                
                #self.emit(QtCore.SIGNAL('call_func'),[self.load_img_files,self.load_dc_Button])
                self.callfuncSignal.emit([self.load_img_files,self.load_dc_Button])
                if gamma_dat[i] == "yes":
                    
                    #self.emit(QtCore.SIGNAL('set_bool'),[self.grail_filt_dat_CheckBox,True])
                    self.setboolSignal.emit([self.grail_filt_dat_CheckBox,True])
                    #self.emit(QtCore.SIGNAL('set_value'),[self.grail_filt_dat_thr1_SpinBox,int(float(gamma_dat_thr1[i]))])
                    self.setvalueSignal.emit([self.grail_filt_dat_thr1_SpinBox,int(float(gamma_dat_thr1[i]))])
                    #self.emit(QtCore.SIGNAL('set_value'),[self.grail_filt_dat_thr2_SpinBox,int(float(gamma_dat_thr2[i]))])
                    self.setvalueSignal.emit([self.grail_filt_dat_thr2_SpinBox,int(float(gamma_dat_thr2[i]))])
                    #self.emit(QtCore.SIGNAL('set_value'),[self.grail_filt_dat_thr3_SpinBox,int(float(gamma_dat_thr3[i]))])
                    self.setvalueSignal.emit([self.grail_filt_dat_thr3_SpinBox,int(float(gamma_dat_thr3[i]))])
                    #self.emit(QtCore.SIGNAL('set_value'),[self.grail_filt_dat_sigma_DSpinBox,float(gamma_dat_sig[i])])
                    self.setvalueSignal.emit([self.grail_filt_dat_sigma_DSpinBox,float(gamma_dat_sig[i])])
                else:
                    
                    #self.emit(QtCore.SIGNAL('set_bool'),[self.grail_filt_dat_CheckBox,False])
                    self.setboolSignal.emit([self.grail_filt_dat_CheckBox,False])
                
                

                if gamma_dc[i] == "yes":
                    
                    #self.emit(QtCore.SIGNAL('set_bool'),[self.grail_filt_dc_CheckBox,True])
                    self.setboolSignal.emit([self.grail_filt_dc_CheckBox,True])
                    #self.emit(QtCore.SIGNAL('set_value'),[self.grail_filt_dc_thr1_SpinBox,int(float(gamma_dc_thr1[i]))])
                    self.setvalueSignal.emit([self.grail_filt_dc_thr1_SpinBox,int(float(gamma_dc_thr1[i]))])
                    #self.emit(QtCore.SIGNAL('set_value'),[self.grail_filt_dc_thr2_SpinBox,int(float(gamma_dc_thr2[i]))])
                    self.setvalueSignal.emit([self.grail_filt_dc_thr2_SpinBox,int(float(gamma_dc_thr2[i]))])
                    #self.emit(QtCore.SIGNAL('set_value'),[self.grail_filt_dc_thr3_SpinBox,int(float(gamma_dc_thr3[i]))])
                    self.setvalueSignal.emit([self.grail_filt_dc_thr3_SpinBox,int(float(gamma_dc_thr3[i]))])
                    #self.emit(QtCore.SIGNAL('set_value'),[self.grail_filt_dc_sigma_DSpinBox,float(gamma_dc_sig[i])])
                    self.setvalueSignal.emit([self.grail_filt_dc_sigma_DSpinBox,float(gamma_dc_sig[i])])
                else:
                    
                    #self.emit(QtCore.SIGNAL('set_bool'),[self.grail_filt_dc_CheckBox,False])
                    self.setboolSignal.emit([self.grail_filt_dc_CheckBox,False])
                
                
                
                
                
                if epi_corr[i] == "yes":
                    
                    #self.emit(QtCore.SIGNAL('set_bool'),[self.epithermal_corr_CheckBox,True])
                    self.setboolSignal.emit([self.epithermal_corr_CheckBox,True])
                    #elf.emit(QtCore.SIGNAL('set_value'),[self.epithermal_corr_DSpinBox,float(epi_corr_val[i])])
                    self.setvalueSignal.emit([self.epithermal_corr_DSpinBox,float(epi_corr_val[i])])
                else:
                    
                    #self.emit(QtCore.SIGNAL('set_bool'),[self.epithermal_corr_CheckBox,False])
                    self.setboolSignal.emit([self.epithermal_corr_CheckBox,False])
                
                    
                    
               
                #self.emit(QtCore.SIGNAL('set_text'),[self.result_dir_lineEdit,str(result_list[i])+str(os.path.sep)])
                self.settextSignal.emit([self.result_dir_lineEdit,str(result_list[i])+str(os.path.sep)])
                try:
                    os.makedirs(result_list[i])
                except OSError:
                    if not os.path.isdir(result_list[i]):
                        raise
                
                #self.emit(QtCore.SIGNAL('set_text'),[self.file_id_lineEdit,str(file_id_list[i])])
                self.settextSignal.emit([self.file_id_lineEdit,str(file_id_list[i])])
                
                
                #self.emit(QtCore.SIGNAL('set_text'),[self.environment_lineEdit,str(sample_list[i])])
                self.settextSignal.emit([self.environment_lineEdit,str(sample_list[i])])
                
                #self.emit(QtCore.SIGNAL('set_text'),[self.sample_lineEdit,str(used_env_list[i])])
                self.settextSignal.emit([self.sample_lineEdit,str(used_env_list[i])])
                
                try:
                    temp_roi=ast.literal_eval(str(multi_roi_list[i]))
                    
                except:
                    temp_roi=None
                try:
                    temp_pixel=ast.literal_eval(str(osc_pixel_list[i]))
                    
                    
                except:
                    #temp_roi=None
                    temp_pixel=None
                
                if isinstance(temp_roi,list)==True and len(temp_roi)==4:
                    #self.emit(QtCore.SIGNAL('set_text'),[self.roi_LineEdit,str(multi_roi_list[i])])
                    self.settextSignal.emit([self.roi_LineEdit,str(multi_roi_list[i])])
                    #self.roi_LineEdit.setText(str(multi_roi_list[i]))#
                    #self.emit(QtCore.SIGNAL('call_func'),[self.update_roi,temp_roi])
                    self.callfuncSignal.emit([self.update_roi,temp_roi])
                    
                else:
                        pass
                if isinstance(temp_pixel,list) and len(temp_pixel)==2:
                    if isinstance(temp_roi,list)==True and len(temp_roi)==4:
                        self.default_pixel=[temp_pixel[0]-temp_roi[2],temp_pixel[1]-temp_roi[0]]
                    else:
                        self.default_pixel=[temp_pixel[0],temp_pixel[1]]    
                else:
                    pass

                index =self.choose_fit_Combo.findText(str(fit_list[i]))
                if index >=0:
                    #self.emit(QtCore.SIGNAL('set_index'),[self.choose_fit_Combo,index])
                    self.setindexSignal.emit([self.choose_fit_Combo,index])
                
                
                while self.multi_load_fin != [True,True,True]:
                    time.sleep(3)
                time.sleep(5)
                
                #self.emit(QtCore.SIGNAL('call_func'),[self.calc_ngi,"None"])
                self.callfuncSignal.emit([self.calc_ngi,"None"])
                while self.calc_state == 0:
                    time.sleep(3)
                    
                #self.emit(QtCore.SIGNAL('call_func'),[self.ngi_calc_gui,1])
                self.callfuncSignal.emit([self.ngi_calc_gui,1])
                while self.calc_state == 1:
                    time.sleep(3)
                
                


                #self.emit(QtCore.SIGNAL('call_func'),[self.save_oscillation_handling,1])
                self.callfuncSignal.emit([self.save_oscillation_handling,1])
                #self.save_oscillation_handling(1)
                #self.emit(QtCore.SIGNAL('call_func'),[self.save_ngi_files_handling,"None"])
                self.callfuncSignal.emit([self.save_ngi_files_handling,"None"])
                #self.save_ngi_files_handling()
                while self.calc_state != 3:
                    time.sleep(3)
                #self.emit(QtCore.SIGNAL('progress'),[self.multi_calc_progressBar,100*(i+1)/len(first_data_list)])
                self.progressSignal.emit([self.multi_calc_progressBar,100*(i+1)/len(first_data_list)])
                #self.multi_calc_progressBar.setValue(100*(i+1)/len(first_data_list))
                
    def multi_calc_dat_thread(self):
        self.multi_calc_dat_Thread = GenericThread(self.multi_calc_dat)


        #self.plotting.autoRefresh()
        self.multi_calc_dat_Thread.start()
        #self.connect(self.multi_calc_Thread,QtCore.SIGNAL("started()"),self.disable_button)
        self.multi_calc_Thread.startSignal.connect(self.disable_button)
        #self.connect(self.multi_calc_Thread,QtCore.SIGNAL("finished()"),self.enable_button)
        self.multi_calc_Thread.startSignal.connect(self.enable_button)

    def multi_calc_dat(self):
        counter=0
        while True:
            scan_list=mc.check_scan(folder,scan_order,exp_img,start_scan)
            while type(scan_list) != list:
                pass
            else:
                first_data_list,last_data_list,first_ob_list,last_ob_list,data_inf_list,ob_inf_list,file_id_list=mc.prep_scan_data(scan_list,start_scan,scan_order,file_identifier)
                temp_ind=folder.rfind(str(os.path.sep)+"data")
                eval_path=str(path[:temp_ind])+str(os.path.sep)+"eval"
            
                
            
                for i in range (counter,len(first_data_list)):
                    #self.row_Label.setText("Calculating data set with ID: "+str(file_id_list[i]))
                    #self.emit(QtCore.SIGNAL('set_text'),[self.row_Label,"Calculating data set with ID: "+str(file_id_list[i])])
                    self.settextSignal.emit([self.row_Label,"Calculating data set with ID: "+str(file_id_list[i])])
                    data_dir=first_data_list[i][0:first_data_list[i].rfind(str(os.path.sep))]
                    ob_dir=first_ob_list[i][0:first_ob_list[i].rfind(str(os.path.sep))]
                    if str(first_data_list[i][-5:])!=".fits":
                            first_data_list[i]=first_data_list[i]+".fits"
                    if str(last_data_list[i][-5:])!=".fits":
                            last_data_list[i]=last_data_list[i]+".fits"
        
                    if str(first_ob_list[i][-5:])!=".fits":
                            first_ob_list[i]=first_ob_list[i]+".fits"
                    if str(last_ob_list[i][-5:])!=".fits":
                            last_ob_list[i]=last_ob_list[i]+".fits"
               
                    
                    
                    self.calc_state=0
                    self.multi_load_fin=[False,False,False]
                    #self.emit(QtCore.SIGNAL('set_value'),[self.img_per_step_Spinbox,int(float(img_per_step_list[i]))])
                    self.setvalueSignal.emit([self.img_per_step_Spinbox,int(float(img_per_step_list[i]))])
                    #self.img_per_step_Spinbox.setValue(int(float(img_per_step_list[i]))) 
                    #self.emit(QtCore.SIGNAL('set_value'),[self.rot_G0rz_DSpinbox,float(rot_list[i])])
                    self.setvalueSignal.emit([self.rot_G0rz_DSpinbox,float(rot_list[i])])
                    #self.rot_G0rz_DSpinbox.setValue(float(rot_list[i]))
                    #self.emit(QtCore.SIGNAL('set_text'),[self.data_dir_lineEdit,str(data_dir)+str(os.path.sep)])
                    self.settextSignal.emit([self.data_dir_lineEdit,str(data_dir)+str(os.path.sep)])
                    #self.data_dir_lineEdit.setText(str(data_dir)+str(os.path.sep))
                    self.data_list=glob.glob(str(data_dir)+str(os.path.sep)+'*.fits')
                    self.data_list.sort()
                    
                    #self.emit(QtCore.SIGNAL('set_combo'),[self.first_data_file_Combo,str(first_data_list[i])])
                    self.setcomboSignal.emit([self.first_data_file_Combo,str(first_data_list[i])])
                    #self.emit(QtCore.SIGNAL('set_combo'),[self.last_data_file_Combo,str(last_data_list[i])])
                    self.setcomboSignal.emit([self.last_data_file_Combo,str(last_data_list[i])])
                    #self.first_data_file_Combo.clear()
                    #self.last_data_file_Combo.clear()
    
                    #self.first_data_file_Combo.addItem(str(first_data_list[i]))
                    #self.last_data_file_Combo.addItem(str(last_data_list[i]))
    
                    #self.emit(QtCore.SIGNAL('set_text'),[self.ob_dir_lineEdit,str(ob_dir)+str(os.path.sep)])
                    self.settextSignal.emit([self.ob_dir_lineEdit,str(ob_dir)+str(os.path.sep)])
                    #self.ob_dir_lineEdit.setText(str(ob_dir)+str(os.path.sep))
                    self.ob_list=glob.glob(str(ob_dir)+str(os.path.sep)+'*.fits')
                    self.ob_list.sort()
                    #self.emit(QtCore.SIGNAL('set_combo'),[self.first_ob_file_Combo,str(first_ob_list[i])])
                    self.setcomboSignal.emit([self.first_ob_file_Combo,str(first_ob_list[i])])
                    #self.emit(QtCore.SIGNAL('set_combo'),[self.last_ob_file_Combo,str(last_ob_list[i])])
                    self.setcomboSignal.emit([self.last_ob_file_Combo,str(last_ob_list[i])])
                    
                    #self.first_ob_file_Combo.clear()
                    #self.last_ob_file_Combo.clear()
                    #self.first_ob_file_Combo.addItem(str(first_ob_list[i]))
                    #self.last_ob_file_Combo.addItem(str(last_ob_list[i]))
                    #self.emit(QtCore.SIGNAL('set_text'),[self.dc_dir_lineEdit,str(dc_dir)+str(os.path.sep)])
                    self.settextSignal.emit([self.dc_dir_lineEdit,str(dc_dir)+str(os.path.sep)])
                    #self.dc_dir_lineEdit.setText(str(dc_dir)+str(os.path.sep))
                    self.dc_list=glob.glob(str(dc_dir)+str(os.path.sep)+'*.fits')
                    self.dc_list.sort()
                    
                    #self.emit(QtCore.SIGNAL('set_combo'),[self.first_dc_file_Combo,str(first_dc_list[i])])
                    self.setcomboSignal.emit([self.first_dc_file_Combo,str(first_dc_list[i])])
                    #self.emit(QtCore.SIGNAL('set_combo'),[self.last_dc_file_Combo,str(last_dc_list[i])])
                    self.setcomboSignal.emit([self.last_dc_file_Combo,str(last_dc_list[i])])
                    
                    #self.emit(QtCore.SIGNAL('call_func'),[self.load_img_files,self.load_data_Button])
                    self.callfuncSignal.emi([self.load_img_files,self.load_data_Button])
                    
                    #self.emit(QtCore.SIGNAL('call_func'),[self.load_img_files,self.load_ob_Button])
                    self.callfuncSoignal.emit([self.load_img_files,self.load_ob_Button])
                    
                    #self.emit(QtCore.SIGNAL('call_func'),[self.load_img_files,self.load_dc_Button])
                    self.callfuncSignal.emit([self.load_img_files,self.load_dc_Button])
    
                    if gamma_dat[i] == "yes":
                        #self.grail_filt_dat_CheckBox.setChecked(True)
                        #self.emit(QtCore.SIGNAL('set_bool'),[self.grail_filt_dat_CheckBox,True])
                        self.setboolSignal.emit([self.grail_filt_dat_CheckBox,True])
                    else:
                        #self.grail_filt_dat_CheckBox.setChecked(False)
                        #self.emit(QtCore.SIGNAL('set_bool'),[self.grail_filt_dat_CheckBox,False])
                        self.setboolSignal.emit([self.grail_filt_dat_CheckBox,False])
                    #self.grail_filt_dat_thr1_SpinBox.setValue(int(float(gamma_dat_thr1[i])))
                    #self.grail_filt_dat_thr2_SpinBox.setValue(int(float(gamma_dat_thr2[i])))
                    #self.grail_filt_dat_thr3_SpinBox.setValue(int(float(gamma_dat_thr3[i])))
                    #self.grail_filt_dat_sigma_DSpinBox.setValue(float(gamma_dat_sig[i]))
                    
                    #self.emit(QtCore.SIGNAL('set_value'),[self.grail_filt_dat_thr1_SpinBox,int(float(gamma_dat_thr1[i]))])
                    self.setvalueSignal.emit([self.grail_filt_dat_thr1_SpinBox,int(float(gamma_dat_thr1[i]))])
                    #self.emit(QtCore.SIGNAL('set_value'),[self.grail_filt_dat_thr2_SpinBox,int(float(gamma_dat_thr2[i]))])
                    self.setvalueSignal.emit([self.grail_filt_dat_thr2_SpinBox,int(float(gamma_dat_thr2[i]))])
                    #self.emit(QtCore.SIGNAL('set_value'),[self.grail_filt_dat_thr3_SpinBox,int(float(gamma_dat_thr3[i]))])
                    self.setvalueSignal.emit([self.grail_filt_dat_thr3_SpinBox,int(float(gamma_dat_thr3[i]))])
                    #self.emit(QtCore.SIGNAL('set_value'),[self.grail_filt_dat_sigma_DSpinBox,float(gamma_dat_sig[i])])
                    self.setvalueSignal.emit([self.grail_filt_dat_sigma_DSpinBox,float(gamma_dat_sig[i])])
                    if gamma_dc[i] == "yes":
                        #self.grail_filt_dc_CheckBox.setChecked(True)
                        #self.emit(QtCore.SIGNAL('set_bool'),[self.grail_filt_dc_CheckBox,True])
                        self.setboolSignal.emit([self.grail_filt_dc_CheckBox,True])
                    else:
                        #self.grail_filt_dc_CheckBox.setChecked(False)
                        #self.emit(QtCore.SIGNAL('set_bool'),[self.grail_filt_dc_CheckBox,False])
                        self.setboolSignal.emit([self.grail_filt_dc_CheckBox,False])
                    #self.grail_filt_dc_thr1_SpinBox.setValue(int(float(gamma_dc_thr1[i])))
                    #self.grail_filt_dc_thr2_SpinBox.setValue(int(float(gamma_dc_thr2[i])))
                    #self.grail_filt_dc_thr3_SpinBox.setValue(int(float(gamma_dc_thr3[i])))
                    #self.grail_filt_dc_sigma_DSpinBox.setValue(float(gamma_dc_sig[i]))
                    #self.emit(QtCore.SIGNAL('set_value'),[self.grail_filt_dc_thr1_SpinBox,int(float(gamma_dc_thr1[i]))])
                    self.setvalueSignal.emit([self.grail_filt_dc_thr1_SpinBox,int(float(gamma_dc_thr1[i]))])
                    #self.emit(QtCore.SIGNAL('set_value'),[self.grail_filt_dc_thr2_SpinBox,int(float(gamma_dc_thr2[i]))])
                    self.setvalueSignal.emit([self.grail_filt_dc_thr2_SpinBox,int(float(gamma_dc_thr2[i]))])
                    #self.emit(QtCore.SIGNAL('set_value'),[self.grail_filt_dc_thr3_SpinBox,int(float(gamma_dc_thr3[i]))])
                    self.setvalueSignal.emit([self.grail_filt_dc_thr3_SpinBox,int(float(gamma_dc_thr3[i]))])
                    #self.emit(QtCore.SIGNAL('set_value'),[self.grail_filt_dc_sigma_DSpinBox,float(gamma_dc_sig[i])])
                    self.setvalueSignal.emit([self.grail_filt_dc_sigma_DSpinBox,float(gamma_dc_sig[i])])
                    
                    
                    
                    if epi_corr[i] == "yes":
                        #self.grail_filt_dc_CheckBox.setChecked(True)
                        #self.emit(QtCore.SIGNAL('set_bool'),[self.epithermal_corr_CheckBox,True])
                        self.setboolSignal.emit([self.epithermal_corr_CheckBox,True])
                    else:
                        #self.grail_filt_dc_CheckBox.setChecked(False)
                        #self.emit(QtCore.SIGNAL('set_bool'),[self.epithermal_corr_CheckBox,False])
                        self.setboolSignal.emit([self.epithermal_corr_CheckBox,False])
                    #self.emit(QtCore.SIGNAL('set_value'),[self.epithermal_corr_DSpinBox,float(epi_corr_val[i])])
                    self.setvalueSignal.emit([self.epithermal_corr_DSpinBox,float(epi_corr_val[i])])
                        
                        
                    #self.result_dir_lineEdit.setText(str(result_list[i])+str(os.path.sep))
                   # self.emit(QtCore.SIGNAL('set_text'),[self.result_dir_lineEdit,str(result_list[i])+str(os.path.sep)])
                    self.setvalueSignal.emit([self.result_dir_lineEdit,str(result_list[i])+str(os.path.sep)])
                    try:
                        os.makedirs(result_list[i])
                    except OSError:
                        if not os.path.isdir(result_list[i]):
                            raise
                    #self.file_id_lineEdit.setText(str(file_id_list[i]))
                    #self.emit(QtCore.SIGNAL('set_text'),[self.file_id_lineEdit,str(file_id_list[i])])
                    self.settextSignal.emit([self.file_id_lineEdit,str(file_id_list[i])])
                    
                    #self.environment_lineEdit.setText(str(sample_list[i]))
                    #self.emit(QtCore.SIGNAL('set_text'),[self.environment_lineEdit,str(sample_list[i])])
                    self.settextSignal.emit([self.environment_lineEdit,str(sample_list[i])])
                    
                    #self.sample_lineEdit.setText(str(used_env_list[i]))
                    #self.emit(QtCore.SIGNAL('set_text'),[self.sample_lineEdit,str(used_env_list[i])])
                    self.settextSignal.emit([self.sample_lineEdit,str(used_env_list[i])])
                   
                    try:
                        temp_roi=ast.literal_eval(str(multi_roi_list[i]))
                       
                    except:
                        temp_roi=None
                    try:
                        temp_pixel=ast.literal_eval(str(osc_pixel_list[i]))
                        
                      
                    except:
                        #temp_roi=None
                        temp_pixel=None
                    
                    if isinstance(temp_roi,list)==True and len(temp_roi)==4:
                        #self.emit(QtCore.SIGNAL('set_text'),[self.roi_LineEdit,str(multi_roi_list[i])])
                        self.settextSignal.emit([self.roi_LineEdit,str(multi_roi_list[i])])
                        #self.roi_LineEdit.setText(str(multi_roi_list[i]))#
                        #self.emit(QtCore.SIGNAL('call_func'),[self.update_roi,temp_roi])
                        self.callfuncSignal.emit([self.update_roi,temp_roi])
                      
                    else:
                            pass
                    if isinstance(temp_pixel,list) and len(temp_pixel)==2:
                        if isinstance(temp_roi,list)==True and len(temp_roi)==4:
                            self.default_pixel=[temp_pixel[0]-temp_roi[2],temp_pixel[1]-temp_roi[0]]
                        else:
                            self.default_pixel=[temp_pixel[0],temp_pixel[1]]    
                    else:
                        pass
    
                    index =self.choose_fit_Combo.findText(str(fit_list[i]))
                    if index >=0:
                        #self.emit(QtCore.SIGNAL('set_index'),[self.choose_fit_Combo,index])
                        self.setindexSignal.emit([self.choose_fit_Combo,index])
                    
                   
                    while self.multi_load_fin != [True,True,True]:
                        time.sleep(3)
                    time.sleep(5)
                    #self.calc_ngi()
                    #self.emit(QtCore.SIGNAL('call_func'),[self.calc_ngi,"None"])
                    self.callfuncSignal.emit([self.calc_ngi,"None"])
                    while self.calc_state == 0:
                        time.sleep(3)
                     
                    #self.emit(QtCore.SIGNAL('call_func'),[self.ngi_calc_gui,1])
                    self.callfuncSignal.emit([self.ngi_calc_gui,1])
                    while self.calc_state == 1:
                        time.sleep(3)
                    
                    
    
    
                    #self.emit(QtCore.SIGNAL('call_func'),[self.save_oscillation_handling,1])
                    self.callfuncSignal.emit([self.save_oscillation_handling,1])
                    #self.save_oscillation_handling(1)
                    #self.emit(QtCore.SIGNAL('call_func'),[self.save_ngi_files_handling,"None"])
                    self.callfuncSignal.emit([self.save_ngi_files_handling,"None"])
                    #self.save_ngi_files_handling()
                    while self.calc_state != 3:
                        time.sleep(3)
                    #self.emit(QtCore.SIGNAL('progress'),[self.multi_calc_progressBar,100*(i+1)/len(first_data_list)])
                    self.progressSignal.emit([self.multi_calc_progressBar,100*(i+1)/len(first_data_list)])
                    counter+=1
                        #self.multi_calc_progressBar.setValue(100*(i+1)/len(first_data_list))
    def set_value(self,input_list):
        input_list[0].setValue(input_list[1])
    def set_combo(self,input_list):
        input_list[0].clear()
        input_list[0].addItem(input_list[1])
    def set_text(self,input_list):
        input_list[0].setText(input_list[1])
    def set_bool(self,input_list):
        input_list[0].setChecked(input_list[1])
    def set_index(self,input_list):
        input_list[0].setCurrentIndex(input_list[1])
    def call_func(self,input_list):
      
        if input_list[1] == "None":
            input_list[0]()
        else:
            input_list[0](input_list[1])
        
        
    def disable_button(self):
        self.multi_stop_Button.setEnabled(True)
        self.multi_calc_Button.setEnabled(False)

    def enable_button(self):
        self.multi_stop_Button.setEnabled(False)
        self.multi_calc_Button.setEnabled(True)

    def multi_stop(self):
        self.multi_calc_Thread.terminate()
        self.calc_Button.setEnabled(False)
        #self.emit(QtCore.SIGNAL('progress'),[self.multi_calc_progressBar,0])
        self.progressSignal.emti([self.multi_calc_progressBar,0])
        #self.emit(QtCore.SIGNAL('progress'),[self.calc_progressBar,0])
        self.progressSignal.emit([self.calc_progressBar,0])
    def load_log_file(self,num=None):
        
      
        if num == 8 or num == False:
            
            self.log.clear()
            log_file=open("DEBUG.log","r")
            for line in log_file.readlines():
                self.log.insertPlainText(line)
            log_file.close()
            self.log.moveCursor(QtGui.QTextCursor.End)
        
            
        
        
        









    """
    def int_osc(self,x,a0,a1,phi):
        y=a0+a1*np.cos(x-phi)
        return y
    """

    
class GenericThread(QtCore.QThread):
    startSignal = QtCore.pyqtSignal(int)
    finishedSignal = QtCore.pyqtSignal(int)
    def __init__(self, function, *args, **kwargs):
        
        QtCore.QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    def run(self):
        self.startSignal.emit(1)
        self.function(*self.args,**self.kwargs)
        #self.emit(QtCore.SIGNAL('finished'),1)
        self.finishedSignal.emit(1)
    
class QPlainTextEditLogger(QtCore.QObject):
    def __init__(self, parent,queue):
        super(QPlainTextEditLogger,self).__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True) 
        self.widget.setCenterOnScroll(False)
        self.queue=queue
        #self.log = open("DEBUG.log","w")

    def start(self):
        while True:
            try:
                record = self.queue.get()
                if record is None:  # We send this as a sentinel to tell the listener to quit.
                    break
                logger = logging.getLogger(record.name)
                logger.handle(record)  # No level or filter logic applied - just do it!
              
            except Exception:
                import sys, traceback
               
                traceback.print_exc(file=sys.stderr)



class Logger_err(QtWidgets.QPlainTextEdit):
    def __init__(self):
        super(Logger_err, self).__init__()
        self.terminal = sys.stderr
        
        self.setWordWrapMode(0)
        self.setLineWrapMode(0)
        self.error=open("Error.txt","w")
        

    def write(self, message):
        self.error.write(message)
        self.terminal.write(message)
        
        #self.insertPlainText(str(message))
    def flush(self):
        pass 
class Logger(QtWidgets.QPlainTextEdit):
    def __init__(self):
        super(Logger, self).__init__()
        self.terminal = sys.stdout
        
        self.setWordWrapMode(0)
        self.setLineWrapMode(0)
        self.error=open("Warnings.txt","w")
        

    def write(self, message):
        self.error.write(message)
        #self.terminal.write(message)
        
        #self.insertPlainText(str(message))
    def flush(self):
        pass 
    
######################Saving Functions#####################################
#





######################Saving Functions#####################################
######################Backend Functions#####################################
def osc_calc(event_x,event_y,data_list,ob_list,dc_median,total_im_num,a0_data,a1_data,phi_data,a0_ob,a1_ob,phi_ob,img_per_step,G0_rot,data_pos_list=None,ob_pos_list=None):
    antares_stepping=11.564
    x_list_dat=[]
    x_list_ob=[]
    y_raw_list_dat=[]
    y_raw_list_ob=[]
    y_fit_list_dat=[]
    y_fit_list_ob=[]

    im_num=int(total_im_num/img_per_step)
    for i in range(0,im_num):
        if data_pos_list == None:
            x_list_dat.append(2*np.pi*i/(im_num-1))
            x_list_ob.append(2*np.pi*i/(im_num-1))

        y_raw_list_dat.append(data_list[i][event_y][event_x]-dc_median[event_y][event_x])
        y_raw_list_ob.append(ob_list[i][event_y][event_x]-dc_median[event_y][event_x])
    if data_pos_list !=None:
        x_list_dat=data_pos_list
        x_list_ob=ob_pos_list
        div=antares_stepping/np.cos(np.deg2rad(G0_rot))
      
    elif data_pos_list ==None:
        div=2*np.pi
    x_list_fit_dat=np.arange(min(x_list_dat), max(x_list_dat), 0.001)
    x_list_fit_ob=np.arange(min(x_list_ob), max(x_list_ob), 0.001)

    for j in x_list_fit_dat:
        y_fit_list_dat.append(int_osc(2*np.pi*j/(div),a0_data[event_y][event_x],a1_data[event_y][event_x],phi_data[event_y][event_x]))
    for j in x_list_fit_ob:
        y_fit_list_ob.append(int_osc(2*np.pi*j/(div),a0_ob[event_y][event_x],a1_ob[event_y][event_x],phi_ob[event_y][event_x]))

    if data_pos_list == None:
        x_list_raw_dat=np.arange(0,im_num)
        x_list_fit_dat[:]=[x*((im_num-1)/(2*np.pi)) for x in x_list_fit_dat]
        x_list_raw_ob=np.arange(0,im_num)
        x_list_fit_ob[:]=[x*((im_num-1)/(2*np.pi)) for x in x_list_fit_ob]
    else:

        x_list_raw_dat=x_list_dat
        x_list_fit_dat[:]=x_list_fit_dat
        x_list_raw_ob=x_list_ob
        x_list_fit_ob[:]=x_list_fit_ob
    

    return x_list_raw_dat,x_list_raw_ob,y_raw_list_dat,y_raw_list_ob,x_list_fit_dat,x_list_fit_ob,y_fit_list_dat,y_fit_list_ob

def int_osc(x,a0,a1,phi):
        y=a0+a1*np.sin(x-phi)
        return y

def create_files_list(file_list):
    data_list_temp=[]
    for i in range (0,len(file_list)):
        temp_ind=file_list[i].rfind(str(os.path.sep))
        data_list_temp.append(file_list[i][temp_ind:])
    return data_list_temp
def getheader(datafile,parameter):
    try:
        hv=float(str(fits.getval(datafile,parameter)))#[:-3])
    except ValueError:
        hv=float(str(fits.getval(datafile,parameter))[:-3])
    return hv
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
######################Backend Functions#####################################

        #fname.setFileMode(QtWidgets.QFileDialog.Directory)



if __name__ == "__main__":
    multiprocessing.freeze_support()
    sys.exit(main(sys.argv))
