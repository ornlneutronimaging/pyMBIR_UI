import os
import logging
import multiprocessing

import numpy as np
import matplotlib.pyplot as plt
from PyQt5 import QtCore, QtGui, QtWidgets

from .matplotlibwidget import MatplotlibWidget, Preview, ROI, Filter_Preview, LINE
from . import newcolormaps as nmap
from ..utility_backend import multi_logger as ml

# from utility_backend.pool_ext import Pool_win,Process

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


def _setupUI(ANGELMain, __version__):
    """
    _setupUI:  Function used to call all the subfunctions, which create the different widgets of the GUI.
               Also responsible for size and loading LOGOS. Additionally it creates some general class variables
               that have to be created immediately.
    """
    ANGELMain.setWindowTitle("ANGEL")
    # ANGELMain.resize(500, 50)
    # ANGELMain.showMaximized()

    ANGELMain.version = __version__
    fpath = os.path.dirname(os.path.abspath(__file__))
    # =fpath+ str(os.path.sep)+'guiresources'+str(os.path.sep)+'ANTARES_LOGO.png'
    ANGELMain.antares_logo_path = resource_path('guiresources' + str(os.path.sep) + 'ANTARES_LOGO.png')
    fpath = os.path.dirname(os.path.abspath(__file__))
    # ANGELMain.frm2_logo_path=fpath+ str(os.path.sep)+'guiresources'+str(os.path.sep)+'FRM2_OS_CMYK.jpg'
    ANGELMain.setWindowIcon(QtGui.QIcon(ANGELMain.antares_logo_path))
    ANGELMain.centralwidget = QtWidgets.QWidget()

    ANGELMain.setCentralWidget(ANGELMain.centralwidget)
    ANGELMain.tabWidget = QtWidgets.QTabWidget(ANGELMain.centralwidget)
    # ANGELMain.tabWidget.setGeometry(QtCore.QRect(0, 0, QMainWindow.width(), 341))
    # ANGELMain.tabWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Minimum)
    # ANGELMain.tabWidget.setMaximumHeight(0.3 *QMainWindow.height())
    ANGELMain.tabWidget2 = QtWidgets.QTabWidget(ANGELMain.centralwidget)
    # ANGELMain.tabWidget2.setGeometry(QtCore.QRect(0, 0, QMainWindow.width(), 341))
    # ANGELMain.tabWidget2.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
    # ANGELMain.tabWidget2.setMaximumHeight(0.5 *QMainWindow.height())
    # ANGELMain.tabWidget.setMinimumHeight(0.4 *QMainWindow.height())
    # ANGELMain.tabWidget.setObjectName(_fromUtf8("tabWidget"))
    ANGELMain.preview_img = Preview("Preview", parent=ANGELMain)

    # ANGELMain.filter_img=Filter_Preview("Filter Preview")
    ANGELMain.main_layout = QtWidgets.QVBoxLayout()
    ANGELMain.main_layout.addWidget(ANGELMain.tabWidget)
    # ANGELMain.test_layout.addStretch(0)
    ANGELMain.main_layout.addWidget(ANGELMain.tabWidget2)
    ANGELMain.cmap_list = [plt.cm.gray, nmap.magma, nmap.inferno, nmap.plasma, nmap.viridis, nmap.parcula]
    ANGELMain.centralwidget.setLayout(ANGELMain.main_layout)
    _start_tab(ANGELMain)
    _data_tab(ANGELMain)
    _ob_tab(ANGELMain)
    _dc_tab(ANGELMain)
    _img_pro_tab(ANGELMain)
    _result_tab(ANGELMain)
    _parameter_tab(ANGELMain)
    _multi_tab(ANGELMain)
    _info_tab(ANGELMain)

    ANGELMain.tabWidget.setTabEnabled(7, False)
    # ANGELMain.tabWidget.setTabEnabled(4, False)
    ANGELMain.tabWidget.setTabEnabled(5, False)

    # ANGELMain.tabWidget.setMaximumHeight(280)

    _calc_tab(ANGELMain)
    _vis_tab(ANGELMain)
    _phase_tab(ANGELMain)
    _ti_tab(ANGELMain)
    _dpci_tab(ANGELMain)
    _dfi_tab(ANGELMain)

    ANGELMain.tabWidget2.setTabEnabled(1, False)
    ANGELMain.tabWidget2.setTabEnabled(2, False)
    ANGELMain.tabWidget2.setTabEnabled(3, False)
    ANGELMain.tabWidget2.setTabEnabled(4, False)
    ANGELMain.tabWidget2.setTabEnabled(5, False)
    ANGELMain.ready = "QStatusBar{padding-left:8px;background:rgba(105,105,105,75);color:green;font-weight:normal;}"
    ANGELMain.working = "QStatusBar{padding-left:8px;background:rgba(105,105,105,75);color:rgb(210,105,30);font-weight:normal;}"
    ANGELMain.warning = "QStatusBar{padding-left:8px;background:rgba(255,179,26,255);color:black;font-weight:bold;}"
    ANGELMain.error = "QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}"
    ANGELMain.statusBar()
    ANGELMain.statusBar().setStyleSheet(ANGELMain.ready)
    ANGELMain.statusBar().showMessage('Ready')
    ANGELMain.roi_list = [0, 0, 0, 0]
    ANGELMain.norm_roi_list = [0, 0, 0, 0]
    ANGELMain.default_pixel = None
    ANGELMain.homepath = os.path.expanduser('~')


def _start_tab(ANGELMain):
    """
    _start_tab: First tab of the upper tab widget. Responsible for basic informations such as the instrument used,
                the number of scanned periods, if a full period has been scanned, which angle the gratings have been rotated
                and if multiple data sets have to be calculated.

                Calls the _start_tab_layout function which sets up the layout of the tab
    """
    ANGELMain.tab_Start = QtWidgets.QWidget()

    ANGELMain.antares_Label = QtWidgets.QLabel()

    antares_logo = QtGui.QPixmap(ANGELMain.antares_logo_path)
    antares_logo = antares_logo.scaled(423, 200, aspectRatioMode=QtCore.Qt.KeepAspectRatio)

    ANGELMain.antares_Label.setPixmap(antares_logo)
    # ANGELMain.antares_Label.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.MinimumExpanding)
    ANGELMain.frm2_Label = QtWidgets.QLabel()
    # frm2_logo=QtWidgets.QPixmap(ANGELMain.frm2_logo_path)
    # frm2_logo=frm2_logo.scaled(200,200,aspectRatioMode =QtCore.Qt.KeepAspectRatio)
    # ANGELMain.frm2_Label.setPixmap(frm2_logo)

    ANGELMain.instrument_Combo = QtWidgets.QComboBox()
    ANGELMain.instrument_Combo.addItems(["ANTARES", "ICON", "CG-1D", "SNAP-FITS", "SNAP-TIFF", "other"])
    # ANGELMain.instrument_Combo.setCurrentIndex(2)  # CG-1D
    ANGELMain.instrument_Label = QtWidgets.QLabel("Instrument used for Experiment:")
    ANGELMain.instrument_Label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    ANGELMain.scanned_periods_Label = QtWidgets.QLabel("Number of scanned Periods:")
    ANGELMain.scanned_periods_Spinbox = QtWidgets.QSpinBox()
    ANGELMain.scanned_periods_Spinbox.setRange(1, 100)
    ANGELMain.scanned_periods_Spinbox.setValue(1)

    ANGELMain.full_per_Label = QtWidgets.QLabel("Full Period:")
    ANGELMain.full_per_Combo = QtWidgets.QComboBox()
    ANGELMain.full_per_Combo.addItems(["True", "False"])

    ANGELMain.rot_G0rz_Label = QtWidgets.QLabel("Rotation of G0rz")
    ANGELMain.rot_G0rz_DSpinbox = QtWidgets.QDoubleSpinBox()
    ANGELMain.rot_G0rz_DSpinbox.setRange(-360, 360)
    ANGELMain.rot_G0rz_DSpinbox.setSingleStep(0.01)
    ANGELMain.rot_G0rz_DSpinbox.setValue(0)
    ANGELMain.version_Label = QtWidgets.QLabel("Program Version: " + ANGELMain.version)

    ANGELMain.multi_Checkbox = QtWidgets.QCheckBox("Calculate multiple data sets")
    # ANGELMain.antares_Label.resize(200,100)
    # ANGELMain.antares_Label.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)

    ANGELMain.instrument_Combo.currentIndexChanged.connect(ANGELMain.update_para)
    ANGELMain.full_per_Combo.currentIndexChanged.connect(ANGELMain.update_para)

    ANGELMain.img_per_step_Label = QtWidgets.QLabel("Images per Step:")
    ANGELMain.img_per_step_Spinbox = QtWidgets.QSpinBox()
    ANGELMain.img_per_step_Spinbox.setRange(1, 100)
    ANGELMain.img_per_step_Spinbox.setValue(1)

    ANGELMain.scanned_periods_Spinbox.valueChanged.connect(ANGELMain.update_para)
    ANGELMain.img_per_step_Spinbox.valueChanged.connect(ANGELMain.update_para)
    ANGELMain.rot_G0rz_DSpinbox.valueChanged.connect(ANGELMain.update_para)

    ANGELMain.multi_Checkbox.clicked.connect(ANGELMain.multi_handle)

    _start_tab_layout(ANGELMain)
    ANGELMain.tabWidget.addTab(ANGELMain.tab_Start, _fromUtf8("Start"))


def _start_tab_layout(ANGELMain):
    """
    _start_tab_layout: Called by _start_tab responsible for creation of its layout.
    """
    ANGELMain.horizontalLayout_main = QtWidgets.QHBoxLayout(ANGELMain.tab_Start)
    ANGELMain.horizontalLayout_sub1 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub2 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub3 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub4 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub5 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub6 = QtWidgets.QHBoxLayout()
    ANGELMain.verticalLayout = QtWidgets.QVBoxLayout()

    ANGELMain.hline1 = QtWidgets.QFrame()
    ANGELMain.hline1.setFrameStyle(QtWidgets.QFrame.HLine)
    ANGELMain.hline1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.antares_Label)
    # ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.frm2_Label)

    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.instrument_Label)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.instrument_Combo)

    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.scanned_periods_Label)
    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.scanned_periods_Spinbox)

    ANGELMain.horizontalLayout_sub4.addWidget(ANGELMain.full_per_Label)
    ANGELMain.horizontalLayout_sub4.addWidget(ANGELMain.full_per_Combo)
    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.rot_G0rz_Label)
    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.rot_G0rz_DSpinbox)

    ANGELMain.horizontalLayout_sub6.addWidget(ANGELMain.img_per_step_Label)
    ANGELMain.horizontalLayout_sub6.addWidget(ANGELMain.img_per_step_Spinbox)

    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub2)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub3)
    # ANGELMain.verticalLayout.addWidget(ANGELMain.hline1)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub4)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub5)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub6)
    ANGELMain.verticalLayout.addWidget(ANGELMain.multi_Checkbox)
    ANGELMain.verticalLayout.addStretch(0)
    ANGELMain.verticalLayout.addWidget(ANGELMain.version_Label)

    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.verticalLayout)
    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.horizontalLayout_sub1)


def _data_tab(ANGELMain):
    """
    _data_tab:  Second tab of the upper tab widget. Responsible for choosing and loading of the data images.
                Can also show a preview of the loaded images.

                Calls the _data_tab_layout function which sets up the layout of the tab
    """
    ANGELMain.tab_Data = QtWidgets.QWidget()

    ANGELMain.data_dir_Button = QtWidgets.QPushButton("Open data directory")
    ANGELMain.load_data_Button = QtWidgets.QPushButton("Load selected files")
    ANGELMain.load_data_Button.setEnabled(False)
    ANGELMain.preview_data_Button = QtWidgets.QPushButton("Preview")
    ANGELMain.preview_data_Button.setEnabled(False)
    ANGELMain.data_progressBar = QtWidgets.QProgressBar()
    ANGELMain.data_progressBar.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.first_data_file_Label = QtWidgets.QLabel("First data file:")
    ANGELMain.first_data_file_Combo = QtWidgets.QComboBox()

    ANGELMain.last_data_file_Label = QtWidgets.QLabel("Last data file:")
    ANGELMain.last_data_file_Combo = QtWidgets.QComboBox()

    ANGELMain.data_dir_Label = QtWidgets.QLabel("Data directory:")
    ANGELMain.data_dir_lineEdit = QtWidgets.QLineEdit()
    ANGELMain.data_dir_lineEdit.setEnabled(False)
    ANGELMain.data_dir_lineEdit.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.data_dir_Button.clicked.connect(ANGELMain.chose_directory)
    ANGELMain.load_data_Button.clicked.connect(ANGELMain.load_img_files)
    ANGELMain.preview_data_Button.clicked.connect(ANGELMain.preview_images)

    _data_tab_layout(ANGELMain)
    ANGELMain.tabWidget.addTab(ANGELMain.tab_Data, _fromUtf8("Data"))


def _data_tab_layout(ANGELMain):
    """
    _data_tab_layout: Called by _data_tab responsible for creation of its layout.
    """
    ANGELMain.horizontalLayout_main = QtWidgets.QHBoxLayout(ANGELMain.tab_Data)
    ANGELMain.horizontalLayout_sub1 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub2 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub3 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub4 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub5 = QtWidgets.QHBoxLayout()
    ANGELMain.verticalLayout = QtWidgets.QVBoxLayout()

    ANGELMain.hline1 = QtWidgets.QFrame()
    ANGELMain.hline1.setFrameStyle(QtWidgets.QFrame.HLine)
    ANGELMain.hline1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.data_dir_Label)
    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.data_dir_lineEdit)

    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.first_data_file_Label)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.first_data_file_Combo)

    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.last_data_file_Label)
    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.last_data_file_Combo)

    ANGELMain.horizontalLayout_sub4.addWidget(ANGELMain.data_dir_Button)
    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.load_data_Button)
    ANGELMain.horizontalLayout_sub4.addWidget(ANGELMain.data_progressBar)

    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.preview_data_Button)

    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub1)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub2)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub3)
    ANGELMain.verticalLayout.addWidget(ANGELMain.hline1)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub4)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub5)
    ANGELMain.verticalLayout.addStretch(0)
    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.verticalLayout)


def _ob_tab(ANGELMain):
    """
    _ob_tab:    Third tab of the upper tab widget. Responsible for choosing and loading of the ob images.
                Can also show a preview of the loaded images.

                Calls the _ob_tab_layout function which sets up the layout of the tab
    """

    ANGELMain.tab_OB = QtWidgets.QWidget()

    ANGELMain.ob_dir_Button = QtWidgets.QPushButton("Open OB directory")
    ANGELMain.load_ob_Button = QtWidgets.QPushButton("Load selected files")
    ANGELMain.load_ob_Button.setEnabled(False)
    ANGELMain.preview_ob_Button = QtWidgets.QPushButton("Preview")
    ANGELMain.preview_ob_Button.setEnabled(False)
    ANGELMain.ob_progressBar = QtWidgets.QProgressBar()
    ANGELMain.ob_progressBar.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.first_ob_file_Label = QtWidgets.QLabel("First Open Beam file:")
    ANGELMain.first_ob_file_Combo = QtWidgets.QComboBox()

    ANGELMain.last_ob_file_Label = QtWidgets.QLabel("Last Open Beam file:")
    ANGELMain.last_ob_file_Combo = QtWidgets.QComboBox()

    ANGELMain.ob_dir_Label = QtWidgets.QLabel("Open Beam directory:")
    ANGELMain.ob_dir_lineEdit = QtWidgets.QLineEdit()
    ANGELMain.ob_dir_lineEdit.setEnabled(False)
    ANGELMain.ob_dir_lineEdit.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.ob_dir_Button.clicked.connect(ANGELMain.chose_directory)
    ANGELMain.load_ob_Button.clicked.connect(ANGELMain.load_img_files)
    ANGELMain.preview_ob_Button.clicked.connect(ANGELMain.preview_images)

    _ob_tab_layout(ANGELMain)
    ANGELMain.tabWidget.addTab(ANGELMain.tab_OB, _fromUtf8("Open Beam"))


def _ob_tab_layout(ANGELMain):
    """
    _ob_tab_layout: Called by _ob_tab responsible for creation of its layout.
    """
    ANGELMain.horizontalLayout_main = QtWidgets.QHBoxLayout(ANGELMain.tab_OB)
    ANGELMain.horizontalLayout_sub1 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub2 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub3 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub4 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub5 = QtWidgets.QHBoxLayout()
    ANGELMain.verticalLayout = QtWidgets.QVBoxLayout()

    ANGELMain.hline1 = QtWidgets.QFrame()
    ANGELMain.hline1.setFrameStyle(QtWidgets.QFrame.HLine)
    ANGELMain.hline1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.ob_dir_Label)
    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.ob_dir_lineEdit)

    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.first_ob_file_Label)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.first_ob_file_Combo)

    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.last_ob_file_Label)
    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.last_ob_file_Combo)

    ANGELMain.horizontalLayout_sub4.addWidget(ANGELMain.ob_dir_Button)
    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.load_ob_Button)
    ANGELMain.horizontalLayout_sub4.addWidget(ANGELMain.ob_progressBar)

    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.preview_ob_Button)

    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub1)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub2)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub3)
    ANGELMain.verticalLayout.addWidget(ANGELMain.hline1)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub4)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub5)
    ANGELMain.verticalLayout.addStretch(0)
    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.verticalLayout)


def _dc_tab(ANGELMain):
    """
    _dc_tab:    Fourth tab of the upper tab widget. Responsible for choosing and loading of the dc images.
                Can also show a preview of the loaded images.

                Calls the _dc_tab_layout function which sets up the layout of the tab
    """
    ANGELMain.tab_DC = QtWidgets.QWidget()

    ANGELMain.dc_dir_Button = QtWidgets.QPushButton("Open DI directory")
    ANGELMain.load_dc_Button = QtWidgets.QPushButton("Load selected files")
    ANGELMain.load_dc_Button.setToolTip(
            "Behaviour for DI's: \n When loading one DI no filter is used.\n When loading two DI the minimum of the two images will be used. \n When loading three or more Di's a stack median is used.")
    ANGELMain.load_dc_Button.setEnabled(False)
    ANGELMain.preview_dc_Button = QtWidgets.QPushButton("Preview")
    ANGELMain.preview_dc_Button.setEnabled(False)
    ANGELMain.dc_progressBar = QtWidgets.QProgressBar()
    ANGELMain.dc_progressBar.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.first_dc_file_Label = QtWidgets.QLabel("First Dark Image file:")
    ANGELMain.first_dc_file_Combo = QtWidgets.QComboBox()

    ANGELMain.last_dc_file_Label = QtWidgets.QLabel("Last Dark Image file:")
    ANGELMain.last_dc_file_Combo = QtWidgets.QComboBox()

    ANGELMain.dc_dir_Label = QtWidgets.QLabel("Dark Image directory:")
    ANGELMain.dc_dir_lineEdit = QtWidgets.QLineEdit()
    ANGELMain.dc_dir_lineEdit.setEnabled(False)
    ANGELMain.dc_dir_lineEdit.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    ANGELMain.dc_median_Label = QtWidgets.QLabel("Radius of the median filter used on the DC Images:")
    ANGELMain.dc_median_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.dc_median_SpinBox.setRange(1, 21)
    ANGELMain.dc_median_SpinBox.setSingleStep(2)

    ANGELMain.dc_dir_Button.clicked.connect(ANGELMain.chose_directory)
    ANGELMain.load_dc_Button.clicked.connect(ANGELMain.load_img_files)
    ANGELMain.preview_dc_Button.clicked.connect(ANGELMain.preview_images)

    _dc_tab_layout(ANGELMain)
    ANGELMain.tabWidget.addTab(ANGELMain.tab_DC, _fromUtf8("Dark Image"))


def _dc_tab_layout(ANGELMain):
    """
    _dc_tab_layout: Called by _dc_tab responsible for creation of its layout.
    """
    ANGELMain.horizontalLayout_main = QtWidgets.QHBoxLayout(ANGELMain.tab_DC)
    ANGELMain.horizontalLayout_sub1 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub2 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub3 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub4 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub5 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub6 = QtWidgets.QHBoxLayout()
    ANGELMain.verticalLayout = QtWidgets.QVBoxLayout()

    ANGELMain.hline1 = QtWidgets.QFrame()
    ANGELMain.hline1.setFrameStyle(QtWidgets.QFrame.HLine)
    ANGELMain.hline1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.dc_dir_Label)
    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.dc_dir_lineEdit)

    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.first_dc_file_Label)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.first_dc_file_Combo)

    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.last_dc_file_Label)
    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.last_dc_file_Combo)

    # ANGELMain.horizontalLayout_sub4.addWidget(ANGELMain.dc_median_Label)
    # ANGELMain.horizontalLayout_sub4.addWidget(ANGELMain.dc_median_SpinBox)

    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.dc_dir_Button)
    ANGELMain.horizontalLayout_sub6.addWidget(ANGELMain.load_dc_Button)
    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.dc_progressBar)

    ANGELMain.horizontalLayout_sub6.addWidget(ANGELMain.preview_dc_Button)

    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub1)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub2)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub3)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub4)
    ANGELMain.verticalLayout.addWidget(ANGELMain.hline1)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub5)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub6)
    ANGELMain.verticalLayout.addStretch(0)
    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.verticalLayout)


def _img_pro_tab(ANGELMain):
    """
    _img_pro_tab:   Fifth tab of the upper tab widget. Responsible for applying filters to the images as
                    well as choosing the ngi fitting method.
                    Can also show a preview of the filtered images.

                Calls the _img_pro_tab_layout function which sets up the layout of the tab
    """
    ANGELMain.tab_img_pro = QtWidgets.QWidget()

    ANGELMain.preview_filter_Button = QtWidgets.QPushButton("Test filter")
    ANGELMain.preview_filter_Button.setEnabled(False)

    ANGELMain.roi_Button = QtWidgets.QPushButton("Select ROI")
    ANGELMain.nroi_CheckBox = QtWidgets.QCheckBox("Use Normalization ROI")
    ANGELMain.img_pro_Label = QtWidgets.QLabel("Image used to test the filters:")
    # ANGELMain.typeCombo = QtWidgets.QComboBox()

    ANGELMain.img_type_pro_Combo = QtWidgets.QComboBox()
    ANGELMain.img_type_pro_Combo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    ANGELMain.img_type_pro_Combo.addItems(["Data Images", "OB Images", "DI Images"])
    ANGELMain.img_pro_Combo = QtWidgets.QComboBox()
    ANGELMain.img_pro_Combo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    ANGELMain.bin_CheckBox = QtWidgets.QCheckBox("Image Binning")
    ANGELMain.bin_Label = QtWidgets.QLabel("Binned Pixels:")
    ANGELMain.bin_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.bin_SpinBox.setValue(1)

    ANGELMain.median_CheckBox = QtWidgets.QCheckBox("Median Filter only for DC")
    # ANGELMain.median_Label=QtWidgets.QLabel("Median filtering of the Image:")

    ANGELMain.median_Label = QtWidgets.QLabel("Radius of the Median Filter for DC:")
    ANGELMain.median_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.median_SpinBox.setValue(1)
    ANGELMain.median_SpinBox.setSingleStep(2)

    ANGELMain.median2_CheckBox = QtWidgets.QCheckBox("Median Filter for all images")
    # ANGELMain.median_Label=QtWidgets.QLabel("Median filtering of the Image:")

    ANGELMain.median2_Label = QtWidgets.QLabel("Radius of the Median Filter for all images:")
    ANGELMain.median2_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.median2_SpinBox.setValue(1)
    ANGELMain.median2_SpinBox.setSingleStep(2)

    ANGELMain.choose_fit_Label = QtWidgets.QLabel("Fit procedure:")
    ANGELMain.choose_fit_Combo = QtWidgets.QComboBox()
    ANGELMain.choose_fit_Combo.addItems(["Matrix Fit", "Matrix Fit Advanced", "EM Fit", "Sinus Fit", "FFT Fit"])

    ANGELMain.grail_filt_dat_CheckBox = QtWidgets.QCheckBox("Gamma Filter for Data/OB")
    ANGELMain.grail_filt_dat_CheckBox.setToolTip("Also known as Michis Holy Grail")
    ANGELMain.grail_filt_dat_thr1_Label = QtWidgets.QLabel("Threshold 1:")
    ANGELMain.grail_filt_dat_thr1_Label.setToolTip("Threshold for 3x3 Median Filter")
    ANGELMain.grail_filt_dat_thr1_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.grail_filt_dat_thr1_SpinBox.setRange(0, 10000)
    ANGELMain.grail_filt_dat_thr1_SpinBox.setValue(80)

    ANGELMain.grail_filt_dat_thr2_Label = QtWidgets.QLabel("Threshold 2:")
    ANGELMain.grail_filt_dat_thr2_Label.setToolTip("Threshold for 5x5 Median Filter")
    ANGELMain.grail_filt_dat_thr2_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.grail_filt_dat_thr2_SpinBox.setRange(0, 10000)
    ANGELMain.grail_filt_dat_thr2_SpinBox.setValue(100)

    ANGELMain.grail_filt_dat_thr3_Label = QtWidgets.QLabel("Threshold 3:")
    ANGELMain.grail_filt_dat_thr3_Label.setToolTip("Threshold for 7x7 Median Filter")
    ANGELMain.grail_filt_dat_thr3_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.grail_filt_dat_thr3_SpinBox.setRange(0, 10000)
    ANGELMain.grail_filt_dat_thr3_SpinBox.setValue(200)

    ANGELMain.grail_filt_dat_sigma_Label = QtWidgets.QLabel("Sigma for LoG")
    ANGELMain.grail_filt_dat_sigma_Label.setToolTip("Sigma for the Laplacian of Gaussian which detects the gamma spots")
    ANGELMain.grail_filt_dat_sigma_DSpinBox = QtWidgets.QDoubleSpinBox()
    ANGELMain.grail_filt_dat_sigma_DSpinBox.setRange(0, 10000)
    ANGELMain.grail_filt_dat_sigma_DSpinBox.setSingleStep(0.1)
    ANGELMain.grail_filt_dat_sigma_DSpinBox.setValue(0.8)

    ANGELMain.grail_filt_dc_CheckBox = QtWidgets.QCheckBox("Gamma Filter for DI")
    ANGELMain.grail_filt_dc_CheckBox.setToolTip("Also known as Michis Holy Grail")
    ANGELMain.grail_filt_dc_thr1_Label = QtWidgets.QLabel("Threshold 1:")
    ANGELMain.grail_filt_dc_thr1_Label.setToolTip("Threshold for 3x3 Median Filter")
    ANGELMain.grail_filt_dc_thr1_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.grail_filt_dc_thr1_SpinBox.setRange(0, 10000)
    ANGELMain.grail_filt_dc_thr1_SpinBox.setValue(20)

    ANGELMain.grail_filt_dc_thr2_Label = QtWidgets.QLabel("Threshold 2:")
    ANGELMain.grail_filt_dc_thr2_Label.setToolTip("Threshold for 5x5 Median Filter")
    ANGELMain.grail_filt_dc_thr2_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.grail_filt_dc_thr2_SpinBox.setRange(0, 10000)
    ANGELMain.grail_filt_dc_thr2_SpinBox.setValue(40)

    ANGELMain.grail_filt_dc_thr3_Label = QtWidgets.QLabel("Threshold 3:")
    ANGELMain.grail_filt_dc_thr3_Label.setToolTip("Threshold for 7x7 Median Filter")
    ANGELMain.grail_filt_dc_thr3_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.grail_filt_dc_thr3_SpinBox.setRange(0, 10000)
    ANGELMain.grail_filt_dc_thr3_SpinBox.setValue(100)

    ANGELMain.grail_filt_dc_sigma_Label = QtWidgets.QLabel("Sigma for LoG")
    ANGELMain.grail_filt_dc_sigma_Label.setToolTip("Sigma for the Laplacian of Gaussian which detects the gamma spots")
    ANGELMain.grail_filt_dc_sigma_DSpinBox = QtWidgets.QDoubleSpinBox()
    ANGELMain.grail_filt_dc_sigma_DSpinBox.setRange(0, 10000)
    ANGELMain.grail_filt_dc_sigma_DSpinBox.setSingleStep(0.1)
    ANGELMain.grail_filt_dc_sigma_DSpinBox.setValue(0.8)

    ANGELMain.epithermal_corr_CheckBox = QtWidgets.QCheckBox("Outlier removal in epithermal DC")
    ANGELMain.epithermal_corr_Label = QtWidgets.QLabel("Threshold for epithermal Correction")
    ANGELMain.epithermal_corr_Label.setToolTip(
            "Threshold to remove outliers still in the epithermal DC Image, after normal filtering. Given as a factor of the Median value of the DC image. The Correction is performed on the filtered and combined DC images")
    ANGELMain.epithermal_corr_DSpinBox = QtWidgets.QDoubleSpinBox()
    ANGELMain.epithermal_corr_DSpinBox.setRange(0.1, 10)
    ANGELMain.epithermal_corr_DSpinBox.setSingleStep(0.1)
    ANGELMain.epithermal_corr_DSpinBox.setValue(1.5)

    ANGELMain.choose_fit_Combo.currentIndexChanged.connect(ANGELMain.update_para)

    ANGELMain.grail_filt_dat_CheckBox.stateChanged.connect(ANGELMain.update_para)
    ANGELMain.grail_filt_dat_thr1_SpinBox.valueChanged.connect(ANGELMain.update_para)
    ANGELMain.grail_filt_dat_thr2_SpinBox.valueChanged.connect(ANGELMain.update_para)
    ANGELMain.grail_filt_dat_thr3_SpinBox.valueChanged.connect(ANGELMain.update_para)
    ANGELMain.grail_filt_dat_sigma_DSpinBox.valueChanged.connect(ANGELMain.update_para)

    ANGELMain.grail_filt_dc_CheckBox.stateChanged.connect(ANGELMain.update_para)
    # ANGELMain.grail_filt_dc_CheckBox.
    ANGELMain.grail_filt_dc_thr1_SpinBox.valueChanged.connect(ANGELMain.update_para)
    ANGELMain.grail_filt_dc_thr2_SpinBox.valueChanged.connect(ANGELMain.update_para)
    ANGELMain.grail_filt_dc_thr3_SpinBox.valueChanged.connect(ANGELMain.update_para)
    ANGELMain.grail_filt_dc_sigma_DSpinBox.valueChanged.connect(ANGELMain.update_para)
    ANGELMain.img_type_pro_Combo.currentIndexChanged.connect(ANGELMain.choose_test_image)
    ANGELMain.bin_CheckBox.stateChanged.connect(ANGELMain.update_para)
    ANGELMain.bin_SpinBox.valueChanged.connect(ANGELMain.update_para)

    ANGELMain.epithermal_corr_CheckBox.stateChanged.connect(ANGELMain.update_para)
    ANGELMain.epithermal_corr_DSpinBox.valueChanged.connect(ANGELMain.update_para)
    # Not yet implemented in the para tab#
    ANGELMain.preview_filter_Button.clicked.connect(ANGELMain.test_filter)
    ANGELMain.roi_Button.clicked.connect(ANGELMain.set_roi)

    _img_pro_tab_layout(ANGELMain)
    ANGELMain.tabWidget.addTab(ANGELMain.tab_img_pro, _fromUtf8("Image Processing"))


def _img_pro_tab_layout(ANGELMain):
    """
    _img_pro_tab_layout: Called by _img_pro_tab responsible for creation of its layout.
    """
    ANGELMain.horizontalLayout_main = QtWidgets.QHBoxLayout(ANGELMain.tab_img_pro)
    ANGELMain.horizontalLayout_sub = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub1 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub2 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub3 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub4 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub5 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub6 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub7 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub8 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub9 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub10 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub11 = QtWidgets.QHBoxLayout()
    ANGELMain.verticalLayout = QtWidgets.QVBoxLayout()
    ANGELMain.verticalLayout2 = QtWidgets.QVBoxLayout()
    ANGELMain.verticalLayout3 = QtWidgets.QVBoxLayout()
    ANGELMain.verticalLayout4 = QtWidgets.QVBoxLayout()
    # ANGELMain.formLayout_1=QtWidgets.QFormLayout()
    # ANGELMain.verticalLayout2.stretch(10)
    ANGELMain.formLayout_2 = QtWidgets.QFormLayout()

    ANGELMain.hline1 = QtWidgets.QFrame()
    ANGELMain.hline1.setFrameStyle(QtWidgets.QFrame.HLine)
    ANGELMain.hline1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.hline2 = QtWidgets.QFrame()
    ANGELMain.hline2.setFrameStyle(QtWidgets.QFrame.HLine)
    ANGELMain.hline2.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.hline3 = QtWidgets.QFrame()
    ANGELMain.hline3.setFrameStyle(QtWidgets.QFrame.HLine)
    ANGELMain.hline3.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.hline4 = QtWidgets.QFrame()
    ANGELMain.hline4.setFrameStyle(QtWidgets.QFrame.HLine)
    ANGELMain.hline4.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.vline1 = QtWidgets.QFrame()
    ANGELMain.vline1.setFrameStyle(QtWidgets.QFrame.VLine)
    ANGELMain.vline1.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

    ANGELMain.vline2 = QtWidgets.QFrame()
    ANGELMain.vline2.setFrameStyle(QtWidgets.QFrame.VLine)
    # ANGELMain.vline2.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Expanding)

    ANGELMain.horizontalLayout_sub.addWidget(ANGELMain.roi_Button)
    ANGELMain.horizontalLayout_sub.addWidget(ANGELMain.nroi_CheckBox)
    # ANGELMain.horizontalLayout_sub.addWidget(ANGELMain.load_Button)
    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.choose_fit_Label)
    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.choose_fit_Combo)

    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.bin_CheckBox)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.bin_Label)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.bin_SpinBox)
    # ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.choose_fit_Combo)
    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.median2_CheckBox)
    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.median2_Label)
    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.median2_SpinBox)

    ANGELMain.horizontalLayout_sub4.addWidget(ANGELMain.grail_filt_dat_CheckBox)
    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.grail_filt_dat_thr1_Label)
    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.grail_filt_dat_thr1_SpinBox)
    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.grail_filt_dat_thr2_Label)
    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.grail_filt_dat_thr2_SpinBox)
    ANGELMain.horizontalLayout_sub6.addWidget(ANGELMain.grail_filt_dat_thr3_Label)
    ANGELMain.horizontalLayout_sub6.addWidget(ANGELMain.grail_filt_dat_thr3_SpinBox)
    ANGELMain.horizontalLayout_sub6.addWidget(ANGELMain.grail_filt_dat_sigma_Label)
    ANGELMain.horizontalLayout_sub6.addWidget(ANGELMain.grail_filt_dat_sigma_DSpinBox)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub4)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub5)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub6)

    ANGELMain.horizontalLayout_sub7.addWidget(ANGELMain.grail_filt_dc_CheckBox)
    ANGELMain.horizontalLayout_sub8.addWidget(ANGELMain.grail_filt_dc_thr1_Label)
    ANGELMain.horizontalLayout_sub8.addWidget(ANGELMain.grail_filt_dc_thr1_SpinBox)
    ANGELMain.horizontalLayout_sub8.addWidget(ANGELMain.grail_filt_dc_thr2_Label)
    ANGELMain.horizontalLayout_sub8.addWidget(ANGELMain.grail_filt_dc_thr2_SpinBox)
    ANGELMain.horizontalLayout_sub9.addWidget(ANGELMain.grail_filt_dc_thr3_Label)
    ANGELMain.horizontalLayout_sub9.addWidget(ANGELMain.grail_filt_dc_thr3_SpinBox)
    ANGELMain.horizontalLayout_sub9.addWidget(ANGELMain.grail_filt_dc_sigma_Label)
    ANGELMain.horizontalLayout_sub9.addWidget(ANGELMain.grail_filt_dc_sigma_DSpinBox)
    ANGELMain.verticalLayout3.addLayout(ANGELMain.horizontalLayout_sub7)
    ANGELMain.verticalLayout3.addLayout(ANGELMain.horizontalLayout_sub8)
    ANGELMain.verticalLayout3.addLayout(ANGELMain.horizontalLayout_sub9)

    ANGELMain.horizontalLayout_sub11.addWidget(ANGELMain.epithermal_corr_CheckBox)
    ANGELMain.horizontalLayout_sub11.addWidget(ANGELMain.epithermal_corr_Label)
    ANGELMain.horizontalLayout_sub11.addWidget(ANGELMain.epithermal_corr_DSpinBox)

    ANGELMain.horizontalLayout_sub10.addLayout(ANGELMain.verticalLayout2)
    ANGELMain.horizontalLayout_sub10.addWidget(ANGELMain.vline2)
    ANGELMain.horizontalLayout_sub10.addLayout(ANGELMain.verticalLayout3)

    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub)
    ANGELMain.verticalLayout.addWidget(ANGELMain.hline1)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub10)
    ANGELMain.verticalLayout.addWidget(ANGELMain.hline2)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub2)
    ANGELMain.verticalLayout.addWidget(ANGELMain.hline3)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub3)
    ANGELMain.verticalLayout.addWidget(ANGELMain.hline4)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub1)

    # ANGELMain.verticalLayout.addWidget(ANGELMain.hline4)
    # ANGELMain.verticalLayout.addLayout()

    # ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub5)
    ANGELMain.formLayout_2.addRow(ANGELMain.horizontalLayout_sub11)
    ANGELMain.formLayout_2.addRow(ANGELMain.hline4)
    ANGELMain.formLayout_2.addRow(ANGELMain.img_pro_Label)
    # ANGELMain.formLayout_2.addRow(ANGELMain.typeCombo)
    ANGELMain.formLayout_2.addRow(ANGELMain.img_type_pro_Combo)
    ANGELMain.formLayout_2.addRow(ANGELMain.img_pro_Combo)
    ANGELMain.formLayout_2.addRow(ANGELMain.preview_filter_Button)
    # ANGELMain.formLayout_2.addRow(ANGELMain.comment_plainText)

    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.verticalLayout)
    ANGELMain.horizontalLayout_main.addWidget(ANGELMain.vline1)

    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.formLayout_2)


def _result_tab(ANGELMain):
    """
    _result_tab:    Sixth tab of the upper tab widget. Responsible for choosing the saving directory as well as providing
                    a file id, sample information, used environment and comments which will be saved in the log file.
                    Can also load the parameters of a previous session.

                Calls the _result_tab_layout function which sets up the layout of the tab
    """
    ANGELMain.tab_Result = QtWidgets.QWidget()

    ANGELMain.result_dir_Button = QtWidgets.QPushButton("Choose result directory")
    # ANGELMain.result_dir_Button.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Minimum)
    ANGELMain.load_Button = QtWidgets.QPushButton("Load previous Session")
    ANGELMain.load_Button.setToolTip("Loads all the parameters of a previous session")
    ANGELMain.save_Button = QtWidgets.QPushButton("Save Results")
    ANGELMain.save_Button.setToolTip("Saves all the parameters and results of the current session")

    ANGELMain.result_dir_Label = QtWidgets.QLabel("Results directory:")
    ANGELMain.result_dir_lineEdit = QtWidgets.QLineEdit()
    # ANGELMain.result_dir_lineEdit.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
    ANGELMain.file_id_Label = QtWidgets.QLabel("File ID:")
    ANGELMain.file_id_lineEdit = QtWidgets.QLineEdit()
    ANGELMain.file_id_lineEdit.setToolTip(
            "Addition to the file names to better differentiate between different sessions")
    ANGELMain.file_id_Label.setToolTip("Addition to the file names to better differentiate between different sessions")
    # validator=QtWidgets.QRegExpValidator(QtCore.QRegExp("[A-Za-z0-9_]{0,255}"))
    ANGELMain.file_id_lineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[A-Za-z0-9_]{0,255}")))

    ANGELMain.sample_Label = QtWidgets.QLabel("Sample information:")
    ANGELMain.sample_lineEdit = QtWidgets.QLineEdit()
    ANGELMain.sample_lineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[A-Za-z0-9_: :]{0,255}")))
    # ANGELMain.sample_lineEdit.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)

    ANGELMain.environment_Label = QtWidgets.QLabel("Used environment:")
    ANGELMain.environment_lineEdit = QtWidgets.QLineEdit()
    ANGELMain.environment_lineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[A-Za-z0-9_]{0,255}")))
    # ANGELMain.environment_lineEdit.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)

    ANGELMain.comment_Label = QtWidgets.QLabel("Comments:")
    ANGELMain.comment_plainText = QtWidgets.QPlainTextEdit()
    # ANGELMain.comment_plainText.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
    # ANGELMain.comment_plainText.setMaximumWidth(0.45*QMainWindow.width(ANGELMain))
    ANGELMain.result_dir_Button.clicked.connect(ANGELMain.chose_directory)
    ANGELMain.save_Button.clicked.connect(ANGELMain.save_ngi_files_handling)
    ANGELMain.load_Button.clicked.connect(ANGELMain.load_files_handling)

    _result_tab_layout(ANGELMain)
    ANGELMain.tabWidget.addTab(ANGELMain.tab_Result, _fromUtf8("Results"))


def _result_tab_layout(ANGELMain):
    """
    _result_tab_layout: Called by _result_tab responsible for creation of its layout.
    """
    ANGELMain.horizontalLayout_main = QtWidgets.QHBoxLayout(ANGELMain.tab_Result)
    ANGELMain.horizontalLayout_sub = QtWidgets.QHBoxLayout()
    ANGELMain.formLayout_1 = QtWidgets.QFormLayout()
    ANGELMain.formLayout_2 = QtWidgets.QFormLayout()

    ANGELMain.hline1 = QtWidgets.QFrame()
    ANGELMain.hline1.setFrameStyle(QtWidgets.QFrame.HLine)
    ANGELMain.hline1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.vline1 = QtWidgets.QFrame()
    ANGELMain.vline1.setFrameStyle(QtWidgets.QFrame.VLine)
    ANGELMain.vline1.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

    ANGELMain.horizontalLayout_sub.addWidget(ANGELMain.save_Button)
    ANGELMain.horizontalLayout_sub.addWidget(ANGELMain.load_Button)

    ANGELMain.formLayout_1.addRow(ANGELMain.result_dir_Label, ANGELMain.result_dir_lineEdit)
    ANGELMain.formLayout_1.addRow(ANGELMain.file_id_Label, ANGELMain.file_id_lineEdit)
    ANGELMain.formLayout_1.addRow(ANGELMain.sample_Label, ANGELMain.sample_lineEdit)
    ANGELMain.formLayout_1.addRow(ANGELMain.environment_Label, ANGELMain.environment_lineEdit)
    ANGELMain.formLayout_1.addRow(ANGELMain.hline1)
    ANGELMain.formLayout_1.addRow(ANGELMain.result_dir_Button)
    ANGELMain.formLayout_1.addRow(ANGELMain.horizontalLayout_sub)

    ANGELMain.formLayout_2.addRow(ANGELMain.comment_Label)
    ANGELMain.formLayout_2.addRow(ANGELMain.comment_plainText)

    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.formLayout_1)
    ANGELMain.horizontalLayout_main.addWidget(ANGELMain.vline1)

    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.formLayout_2)


def _parameter_tab(ANGELMain):
    """
    _parameter_tab:     Seventh tab of the upper tab widget. Has all used parameters listed, which will be used by the calculation.
                        Parameters can be unlocked and changed there.

                        Calls the _parameter_tab_layout function which sets up the layout of the tab
    """
    ANGELMain.tab_Parameter = QtWidgets.QWidget()

    ANGELMain.para_Button = QtWidgets.QPushButton("Unlock Parameters")

    ANGELMain.im_num_Label = QtWidgets.QLabel("Number of Images:")
    ANGELMain.im_num_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.im_num_SpinBox.setEnabled(False)

    ANGELMain.par_img_per_step_Label = QtWidgets.QLabel("Number of Images per Step:")
    ANGELMain.par_img_per_step_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.par_img_per_step_SpinBox.setEnabled(False)

    ANGELMain.ob_num_Label = QtWidgets.QLabel("Number of  OB Images:")
    ANGELMain.ob_num_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.ob_num_SpinBox.setEnabled(False)

    ANGELMain.dc_num_Label = QtWidgets.QLabel("Number of  DC Images:")
    ANGELMain.dc_num_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.dc_num_SpinBox.setEnabled(False)

    ANGELMain.im_pat_Label = QtWidgets.QLabel("Path of Images:")
    ANGELMain.im_pat_LineEdit = QtWidgets.QLineEdit()
    ANGELMain.im_pat_LineEdit.setEnabled(False)

    ANGELMain.ob_pat_Label = QtWidgets.QLabel("Path of  OB Images:")
    ANGELMain.ob_pat_LineEdit = QtWidgets.QLineEdit()
    ANGELMain.ob_pat_LineEdit.setEnabled(False)

    ANGELMain.dc_pat_Label = QtWidgets.QLabel("Path of  DC Images:")
    ANGELMain.dc_pat_LineEdit = QtWidgets.QLineEdit()
    ANGELMain.dc_pat_LineEdit.setEnabled(False)

    ANGELMain.im_first_Label = QtWidgets.QLabel("First Image:")
    ANGELMain.im_first_LineEdit = QtWidgets.QLineEdit()
    ANGELMain.im_first_LineEdit.setEnabled(False)

    ANGELMain.ob_first_Label = QtWidgets.QLabel("First OB Image:")
    ANGELMain.ob_first_LineEdit = QtWidgets.QLineEdit()
    ANGELMain.ob_first_LineEdit.setEnabled(False)

    ANGELMain.dc_first_Label = QtWidgets.QLabel("First DC Image:")
    ANGELMain.dc_first_LineEdit = QtWidgets.QLineEdit()
    ANGELMain.dc_first_LineEdit.setEnabled(False)

    ANGELMain.im_last_Label = QtWidgets.QLabel("Last Image:")
    ANGELMain.im_last_LineEdit = QtWidgets.QLineEdit()
    ANGELMain.im_last_LineEdit.setEnabled(False)

    ANGELMain.ob_last_Label = QtWidgets.QLabel("Last OB Image:")
    ANGELMain.ob_last_LineEdit = QtWidgets.QLineEdit()
    ANGELMain.ob_last_LineEdit.setEnabled(False)

    ANGELMain.dc_last_Label = QtWidgets.QLabel("Last DC Image:")
    ANGELMain.dc_last_LineEdit = QtWidgets.QLineEdit()
    ANGELMain.dc_last_LineEdit.setEnabled(False)

    ANGELMain.par_per_Label = QtWidgets.QLabel("Number of scanned periods:")
    ANGELMain.par_per_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.par_per_SpinBox.setEnabled(False)

    ANGELMain.par_full_per_Label = QtWidgets.QLabel("Full Period:")
    ANGELMain.par_full_per_Combo = QtWidgets.QComboBox()
    ANGELMain.par_full_per_Combo.addItems(["True", "False"])
    ANGELMain.par_full_per_Combo.setEnabled(False)

    ANGELMain.par_rot_G0rz_Label = QtWidgets.QLabel("Rotation of G0rz:")
    ANGELMain.par_rot_G0rz_DSpinBox = QtWidgets.QDoubleSpinBox()
    ANGELMain.par_rot_G0rz_DSpinBox.setRange(-360, 360)
    ANGELMain.par_rot_G0rz_DSpinBox.setValue(0)
    ANGELMain.par_rot_G0rz_DSpinBox.setSingleStep(0.01)
    ANGELMain.par_rot_G0rz_DSpinBox.setEnabled(False)

    ANGELMain.fit_Label = QtWidgets.QLabel("Fit procedure:")
    ANGELMain.fit_Combo = QtWidgets.QLineEdit()
    ANGELMain.fit_Combo.setText(ANGELMain.choose_fit_Combo.currentText())
    ANGELMain.fit_Combo.setEnabled(False)

    ANGELMain.par_bin_Label = QtWidgets.QLabel("Binning of the Image:")
    ANGELMain.par_bin_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.par_bin_Combo = QtWidgets.QComboBox()
    ANGELMain.par_bin_Combo.addItems(["False", "True"])
    ANGELMain.par_bin2_Label = QtWidgets.QLabel("Number of binned Pixels")
    ANGELMain.par_bin_Combo.setEnabled(False)
    ANGELMain.par_bin_SpinBox.setEnabled(False)

    ANGELMain.par_grail_filt_dat_Label = QtWidgets.QLabel("Gamma Filter for Data/OB")
    ANGELMain.par_grail_filt_dat_Combo = QtWidgets.QComboBox()
    ANGELMain.par_grail_filt_dat_Combo.addItems(["False", "True"])
    ANGELMain.par_grail_filt_dat_Combo.setEnabled(False)

    # ANGELMain.par_grail_filt_dat_CheckBox.setToolTip("Also known as Michis Holy Grail")
    ANGELMain.par_grail_filt_dat_thr1_Label = QtWidgets.QLabel("Threshold 3x3:")
    ANGELMain.par_grail_filt_dat_thr1_Label.setToolTip("Threshold for 3x3 Median Filter")
    ANGELMain.par_grail_filt_dat_thr1_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.par_grail_filt_dat_thr1_SpinBox.setRange(0, 10000)
    ANGELMain.par_grail_filt_dat_thr1_SpinBox.setValue(80)
    ANGELMain.par_grail_filt_dat_thr1_SpinBox.setEnabled(False)

    ANGELMain.par_grail_filt_dat_thr2_Label = QtWidgets.QLabel("Threshold 5x5:")
    ANGELMain.par_grail_filt_dat_thr2_Label.setToolTip("Threshold for 5x5 Median Filter")
    ANGELMain.par_grail_filt_dat_thr2_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.par_grail_filt_dat_thr2_SpinBox.setRange(0, 10000)
    ANGELMain.par_grail_filt_dat_thr2_SpinBox.setValue(100)
    ANGELMain.par_grail_filt_dat_thr2_SpinBox.setEnabled(False)

    ANGELMain.par_grail_filt_dat_thr3_Label = QtWidgets.QLabel("Threshold 7x7:")
    ANGELMain.par_grail_filt_dat_thr3_Label.setToolTip("Threshold for 7x7 Median Filter")
    ANGELMain.par_grail_filt_dat_thr3_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.par_grail_filt_dat_thr3_SpinBox.setRange(0, 10000)
    ANGELMain.par_grail_filt_dat_thr3_SpinBox.setValue(200)
    ANGELMain.par_grail_filt_dat_thr3_SpinBox.setEnabled(False)

    ANGELMain.par_grail_filt_dat_sigma_Label = QtWidgets.QLabel("Sigma for LoG")
    # ANGELMain.par_grail_filt_dat_sigma_Label.setToolTip("Sigma for the Laplacian of Gaussian which detects the gamma spots")
    ANGELMain.par_grail_filt_dat_sigma_DSpinBox = QtWidgets.QDoubleSpinBox()
    ANGELMain.par_grail_filt_dat_sigma_DSpinBox.setRange(0, 10000)
    ANGELMain.par_grail_filt_dat_sigma_DSpinBox.setSingleStep(0.1)
    ANGELMain.par_grail_filt_dat_sigma_DSpinBox.setValue(0.8)
    ANGELMain.par_grail_filt_dat_sigma_DSpinBox.setEnabled(False)

    ANGELMain.par_grail_filt_dc_Label = QtWidgets.QLabel("Gamma Filter for DC")
    ANGELMain.par_grail_filt_dc_Combo = QtWidgets.QComboBox()
    ANGELMain.par_grail_filt_dc_Combo.addItems(["False", "True"])
    ANGELMain.par_grail_filt_dc_Combo.setEnabled(False)
    # ANGELMain.par_grail_filt_dc_CheckBox.setToolTip("Also known as Michis Holy Grail")
    ANGELMain.par_grail_filt_dc_thr1_Label = QtWidgets.QLabel("Threshold 3x3:")
    ANGELMain.par_grail_filt_dc_thr1_Label.setToolTip("Threshold for 3x3 Median Filter")
    ANGELMain.par_grail_filt_dc_thr1_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.par_grail_filt_dc_thr1_SpinBox.setRange(0, 10000)
    ANGELMain.par_grail_filt_dc_thr1_SpinBox.setValue(20)
    ANGELMain.par_grail_filt_dc_thr1_SpinBox.setEnabled(False)

    ANGELMain.par_grail_filt_dc_thr2_Label = QtWidgets.QLabel("Threshold 5x5:")
    ANGELMain.par_grail_filt_dc_thr2_Label.setToolTip("Threshold for 5x5 Median Filter")
    ANGELMain.par_grail_filt_dc_thr2_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.par_grail_filt_dc_thr2_SpinBox.setRange(0, 10000)
    ANGELMain.par_grail_filt_dc_thr2_SpinBox.setValue(40)
    ANGELMain.par_grail_filt_dc_thr2_SpinBox.setEnabled(False)

    ANGELMain.par_grail_filt_dc_thr3_Label = QtWidgets.QLabel("Threshold 7x7:")
    ANGELMain.par_grail_filt_dc_thr3_Label.setToolTip("Threshold for 7x7 Median Filter")
    ANGELMain.par_grail_filt_dc_thr3_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.par_grail_filt_dc_thr3_SpinBox.setRange(0, 10000)
    ANGELMain.par_grail_filt_dc_thr3_SpinBox.setValue(100)
    ANGELMain.par_grail_filt_dc_thr3_SpinBox.setEnabled(False)

    ANGELMain.par_grail_filt_dc_sigma_Label = QtWidgets.QLabel("Sigma for LoG")
    ANGELMain.par_grail_filt_dc_sigma_Label.setToolTip(
            "Sigma for the Laplacian of Gaussian which detects the gamma spots")
    ANGELMain.par_grail_filt_dc_sigma_DSpinBox = QtWidgets.QDoubleSpinBox()
    ANGELMain.par_grail_filt_dc_sigma_DSpinBox.setRange(0, 10000)
    ANGELMain.par_grail_filt_dc_sigma_DSpinBox.setSingleStep(0.1)
    ANGELMain.par_grail_filt_dc_sigma_DSpinBox.setValue(0.8)
    ANGELMain.par_grail_filt_dc_sigma_DSpinBox.setEnabled(False)

    ANGELMain.par_median_Label = QtWidgets.QLabel("Median Filter:")
    ANGELMain.par_median_SpinBox = QtWidgets.QSpinBox()
    ANGELMain.par_median_Combo = QtWidgets.QComboBox()
    ANGELMain.par_median_Combo.addItems(["False", "True"])
    ANGELMain.par_median2_Label = QtWidgets.QLabel("Radius of median filter")
    ANGELMain.par_median_Combo.setEnabled(False)
    ANGELMain.par_median_SpinBox.setEnabled(False)

    ANGELMain.roi_Label = QtWidgets.QLabel("Region of Interest ([y0,y1,x0,x1]):")
    ANGELMain.roi_LineEdit = QtWidgets.QLineEdit()
    ANGELMain.roi_LineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[0-9_\\[\\]\\,]{0,255}")))
    ANGELMain.roi_LineEdit.setEnabled(False)

    ANGELMain.norm_roi_Label = QtWidgets.QLabel(" Normalisation Region of Interest ([y0,y1,x0,x1]):")
    ANGELMain.norm_roi_LineEdit = QtWidgets.QLineEdit()
    ANGELMain.norm_roi_LineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[0-9_\\[\\]\\,]{0,255}")))
    ANGELMain.norm_roi_LineEdit.setEnabled(False)

    # ANGELMain.preview_img.roiSignal.connect( ANGELMain.update_roi )
    # ANGELMain.connect( ANGELMain.preview_img,QtCore.SIGNAL('roi'),ANGELMain.update_roi  )
    ANGELMain.preview_img.roiSignal.connect(ANGELMain.update_roi)
    # ANGELMain.connect( ANGELMain.preview_img,QtCore.SIGNAL('norm_roi'),ANGELMain.update_norm_roi  )
    ANGELMain.preview_img.normroiSignal.connect(ANGELMain.update_norm_roi)
    ANGELMain.para_Button.clicked.connect(ANGELMain.para_lock)

    # ANGELMain.result_dir_lineEdit.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
    ANGELMain.update_para()

    _parameter_tab_layout(ANGELMain)
    ANGELMain.tabWidget.addTab(ANGELMain.tab_Parameter, _fromUtf8("Parameter"))


def _parameter_tab_layout(ANGELMain):
    """
    _parameter_tab_layout: Called by _parameter_tab responsible for creation of its layout.
    """
    ANGELMain.horizontalLayout = QtWidgets.QHBoxLayout()
    ANGELMain.verticalLayout = QtWidgets.QVBoxLayout(ANGELMain.tab_Parameter)
    ANGELMain.formLayout_1 = QtWidgets.QFormLayout()
    ANGELMain.formLayout_2 = QtWidgets.QFormLayout()

    ANGELMain.varFrame = QtWidgets.QFrame()
    ANGELMain.varLayout = QtWidgets.QGridLayout()
    ANGELMain.varFrame.setLayout(ANGELMain.varLayout)
    ANGELMain.varFrame2 = QtWidgets.QScrollArea()
    ANGELMain.varFrame2.setWidget(ANGELMain.varFrame)
    ANGELMain.varFrame2.setWidgetResizable(True)
    # ANGELMain.varFrame2.setMaximumHeight(200)

    ANGELMain.hline1 = QtWidgets.QFrame()
    ANGELMain.hline1.setFrameStyle(QtWidgets.QFrame.HLine)
    ANGELMain.hline1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.vline1 = QtWidgets.QFrame()
    ANGELMain.vline1.setFrameStyle(QtWidgets.QFrame.VLine)
    ANGELMain.vline1.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

    ANGELMain.varLayout.addWidget(ANGELMain.im_pat_Label, 1, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.im_pat_LineEdit, 1, 2)
    ANGELMain.varLayout.addWidget(ANGELMain.im_first_Label, 2, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.im_first_LineEdit, 2, 2)
    ANGELMain.varLayout.addWidget(ANGELMain.im_last_Label, 3, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.im_last_LineEdit, 3, 2)
    ANGELMain.varLayout.addWidget(ANGELMain.im_num_Label, 4, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.im_num_SpinBox, 4, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.ob_pat_Label, 5, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.ob_pat_LineEdit, 5, 2)
    ANGELMain.varLayout.addWidget(ANGELMain.ob_first_Label, 6, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.ob_first_LineEdit, 6, 2)
    ANGELMain.varLayout.addWidget(ANGELMain.ob_last_Label, 7, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.ob_last_LineEdit, 7, 2)
    ANGELMain.varLayout.addWidget(ANGELMain.ob_num_Label, 8, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.ob_num_SpinBox, 8, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.dc_pat_Label, 9, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.dc_pat_LineEdit, 9, 2)
    ANGELMain.varLayout.addWidget(ANGELMain.dc_first_Label, 10, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.dc_first_LineEdit, 10, 2)
    ANGELMain.varLayout.addWidget(ANGELMain.dc_last_Label, 11, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.dc_last_LineEdit, 11, 2)
    ANGELMain.varLayout.addWidget(ANGELMain.dc_num_Label, 12, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.dc_num_SpinBox, 12, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.par_per_Label, 13, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_per_SpinBox, 13, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.par_full_per_Label, 14, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_full_per_Combo, 14, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.par_rot_G0rz_Label, 15, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_rot_G0rz_DSpinBox, 15, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dat_Label, 16, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dat_Combo, 16, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dat_thr1_Label, 17, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dat_thr1_SpinBox, 17, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dat_thr2_Label, 18, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dat_thr2_SpinBox, 18, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dat_thr3_Label, 19, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dat_thr3_SpinBox, 19, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dat_sigma_Label, 20, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dat_sigma_DSpinBox, 20, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dc_Label, 21, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dc_Combo, 21, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dc_thr1_Label, 22, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dc_thr1_SpinBox, 22, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dc_thr2_Label, 23, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dc_thr2_SpinBox, 23, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dc_thr3_Label, 24, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dc_thr3_SpinBox, 24, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dc_sigma_Label, 25, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_grail_filt_dc_sigma_DSpinBox, 25, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.par_median_Label, 26, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_median_Combo, 26, 2)
    ANGELMain.varLayout.addWidget(ANGELMain.par_median2_Label, 27, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_median_SpinBox, 27, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.par_bin_Label, 28, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_bin_Combo, 28, 2)
    ANGELMain.varLayout.addWidget(ANGELMain.par_bin2_Label, 29, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_bin_SpinBox, 29, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.fit_Label, 30, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.fit_Combo, 30, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.roi_Label, 31, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.roi_LineEdit, 31, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.norm_roi_Label, 32, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.norm_roi_LineEdit, 32, 2)

    ANGELMain.varLayout.addWidget(ANGELMain.par_img_per_step_Label, 33, 1)
    ANGELMain.varLayout.addWidget(ANGELMain.par_img_per_step_SpinBox, 33, 2)

    ANGELMain.horizontalLayout.addWidget(ANGELMain.para_Button)
    # ANGELMain.horizontalLayout.addWidget(ANGELMain.lockpara_Button)

    ANGELMain.verticalLayout.addWidget(ANGELMain.varFrame2)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout)
    # ANGELMain.horizontalLayout.addLayout(ANGELMain.verticalLayout_sub)

    # ANGELMain.horizontalLayout_main.addLayout(ANGELMain.formLayout_2)


def _multi_tab(ANGELMain):
    """
    _multi_tab:     Eighth tab of the upper tab widget. Used for calculating multiple datasets in one go.
                    Loads the excel files containing the parameters needed for the evaluation.

                    Calls the _multi_tab_layout function which sets up the layout of the tab
    """
    ANGELMain.tab_Multi = QtWidgets.QWidget()

    ANGELMain.load_excel_Button = QtWidgets.QPushButton("Load Excel File")
    ANGELMain.excel_dir_Label = QtWidgets.QLabel("Path of the Excel File:")
    ANGELMain.excel_dir_lineEdit = QtWidgets.QLineEdit()
    ANGELMain.excel_dir_lineEdit.setEnabled(False)
    # ANGELMain.excel_dir_lineEdit.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)

    ANGELMain.first_line_Label = QtWidgets.QLabel("Starting row in excel file:")
    ANGELMain.first_line_Combo = QtWidgets.QComboBox()

    ANGELMain.last_line_Label = QtWidgets.QLabel("Last row in excel file:")
    ANGELMain.last_line_Combo = QtWidgets.QComboBox()

    ANGELMain.multi_calc_Button = QtWidgets.QPushButton("Start Calculation")

    ANGELMain.multi_calc_progressBar = QtWidgets.QProgressBar()
    ANGELMain.multi_calc_progressBar.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.multi_igno_Checkbox = QtWidgets.QCheckBox("Ignore overwrite warning")
    ANGELMain.multi_igno_Checkbox.setChecked(False)

    ANGELMain.multi_stop_Button = QtWidgets.QPushButton("Stop Calculation")
    ANGELMain.row_Label = QtWidgets.QLabel()

    ANGELMain.load_excel_Button.clicked.connect(ANGELMain.choose_excel)
    ANGELMain.multi_calc_Button.clicked.connect(ANGELMain.multi_calc_thread)
    ANGELMain.multi_stop_Button.clicked.connect(ANGELMain.multi_stop)

    _multi_tab_layout(ANGELMain)
    ANGELMain.tabWidget.addTab(ANGELMain.tab_Multi, _fromUtf8("Multi Calculation"))


def _multi_tab_layout(ANGELMain):
    """
    _multi_tab_layout: Called by _multi_tab responsible for creation of its layout.
    """
    ANGELMain.horizontalLayout_main = QtWidgets.QHBoxLayout(ANGELMain.tab_Multi)
    ANGELMain.horizontalLayout_sub1 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub2 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub3 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub4 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub5 = QtWidgets.QHBoxLayout()
    ANGELMain.verticalLayout = QtWidgets.QVBoxLayout()

    ANGELMain.hline1 = QtWidgets.QFrame()
    ANGELMain.hline1.setFrameStyle(QtWidgets.QFrame.HLine)
    ANGELMain.hline1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.hline2 = QtWidgets.QFrame()
    ANGELMain.hline2.setFrameStyle(QtWidgets.QFrame.HLine)
    ANGELMain.hline2.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.excel_dir_Label)
    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.excel_dir_lineEdit)

    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.first_line_Label)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.first_line_Combo)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.last_line_Label)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.last_line_Combo)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.multi_igno_Checkbox)
    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.row_Label)
    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.multi_calc_progressBar)

    ANGELMain.verticalLayout.addWidget(ANGELMain.load_excel_Button)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub1)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub2)
    ANGELMain.verticalLayout.addWidget(ANGELMain.hline1)
    ANGELMain.verticalLayout.addWidget(ANGELMain.multi_calc_Button)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub3)
    ANGELMain.verticalLayout.addWidget(ANGELMain.hline2)
    ANGELMain.verticalLayout.addWidget(ANGELMain.multi_stop_Button)
    ANGELMain.verticalLayout.addStretch(0)
    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.verticalLayout)
    ANGELMain.horizontalLayout_main.addStretch(0)


def _info_tab(ANGELMain):
    """
    _info_tab:    Eigth tab of the upper tab widget. Responsible for choosing the saving directory as well as providing
                    a file id, sample information, used environment and comments which will be saved in the log file.
                    Can also load the parameters of a previous session.

                Calls the _result_tab_layout function which sets up the layout of the tab
    """
    ANGELMain.tab_Info = QtWidgets.QWidget()
    ANGELMain.reload_Button = QtWidgets.QPushButton("Refresh Log File")
    ANGELMain.log_Label = QtWidgets.QLabel("Info:")

    # ANGELMain.log.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    # logging.getLogger().addHandler(ANGELMain.log)
    # logging.getLogger().setLevel(logging.DEBUG)
    # ml.install_mp_handler()
    ANGELMain.queue = multiprocessing.Queue(-1)
    # print type(ANGELMain.queue)
    ANGELMain.listener = multiprocessing.Process(target=ml.listener_process,
                                                 args=(ANGELMain.queue, ml.listener_configurer))
    ANGELMain.listener.daemon = True
    ANGELMain.listener.start()
    # logging.info('something to remember')
    # ANGELMain.log=QPlainTextEditLogger(ANGELMain)
    ANGELMain.log = QtWidgets.QPlainTextEdit()
    ANGELMain.log.setReadOnly(True)
    # ANGELMain.log.start()
    h = ml.QueueHandler(ANGELMain.queue)  # Just the one handler needed
    # print "laola"
    root = logging.getLogger()
    root.addHandler(h)
    # send all messages, for demo; no other level or filter logic applied.
    root.setLevel(logging.DEBUG)
    ANGELMain.reload_Button.clicked.connect(ANGELMain.load_log_file)
    ANGELMain.tabWidget.currentChanged.connect(ANGELMain.load_log_file)
    _info_tab_layout(ANGELMain)
    ANGELMain.tabWidget.addTab(ANGELMain.tab_Info, _fromUtf8("Info"))


def _info_tab_layout(ANGELMain):
    """
    _info_tab_layout: Called by _info_tab responsible for creation of its layout.
    """
    ANGELMain.horizontalLayout_main = QtWidgets.QHBoxLayout(ANGELMain.tab_Info)
    ANGELMain.horizontalLayout_sub = QtWidgets.QHBoxLayout()
    ANGELMain.formLayout_1 = QtWidgets.QFormLayout()
    ANGELMain.formLayout_2 = QtWidgets.QFormLayout()

    ANGELMain.hline1 = QtWidgets.QFrame()
    ANGELMain.hline1.setFrameStyle(QtWidgets.QFrame.HLine)
    ANGELMain.hline1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.vline1 = QtWidgets.QFrame()
    ANGELMain.vline1.setFrameStyle(QtWidgets.QFrame.VLine)
    ANGELMain.vline1.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

    ANGELMain.formLayout_1.addRow(ANGELMain.log_Label, ANGELMain.reload_Button)
    ANGELMain.formLayout_1.addRow(ANGELMain.log)

    # ANGELMain.formLayout_2.addRow(ANGELMain.err_Label)
    # ANGELMain.formLayout_2.addRow(ANGELMain.logging_err)

    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.formLayout_1)
    ANGELMain.horizontalLayout_main.addWidget(ANGELMain.vline1)

    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.formLayout_2)


def _calc_tab(ANGELMain):
    """
    _clc_tab:     First tab of the lower tab widget. Used to start the calculation, showing the progress
                    and giving a preview of the results.

                    Calls the _calc_tab_layout function which sets up the layout of the tab
    """
    ANGELMain.tab_Calc = QtWidgets.QWidget()

    # ANGELMain.data_dir_Button = QtWidgets.QPushButton("Open data directory")
    # ANGELMain.load_data_Button = QtWidgets.QPushButton("Load selected files")
    # ANGELMain.load_data_Button.setEnabled(False)
    ANGELMain.calc_Button = QtWidgets.QPushButton("Calculate")
    # ANGELMain.calc_Button.setEnabled(False)

    # ANGELMain.calc_Button.setEnabled(False)
    ANGELMain.calc_progressBar = QtWidgets.QProgressBar()
    # ANGELMain.calc_progressBar.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.mpl_ti_pre_widget = MatplotlibWidget(ANGELMain.tab_Calc, title="TI")
    # ANGELMain.mpl_ti_pre_widget.axes.imshow(test_image,cmap=plt.cm.gray)
    ANGELMain.mpl_ti_pre_widget.axes.set_title("TI")
    # ANGELMain.mpl_ti_widget.figure.colorbar(im)
    # ANGELMain.mpl_ti_widget.axes.

    ANGELMain.mpl_dpci_pre_widget = MatplotlibWidget(ANGELMain.tab_Calc, title="DPCI")

    # ANGELMain.mpl_dpci_pre_widget.axes.imshow(test_image,cmap=plt.cm.gray)
    ANGELMain.mpl_dpci_pre_widget.axes.set_title("DPCI")
    ANGELMain.mpl_dfi_pre_widget = MatplotlibWidget(ANGELMain.tab_Calc, title="DFI")
    # ANGELMain.mpl_dfi_pre_widget.axes.imshow(test_image,cmap=plt.cm.gray)
    ANGELMain.mpl_dfi_pre_widget.axes.set_title("DFI")
    # ANGELMain.mplwidget.setGeometry(QtCore.QRect(350, 20, 221, 271))
    ANGELMain.ax = ANGELMain.mpl_dfi_pre_widget.figure.add_subplot(111)
    # ax.imshow(test_image,cmap=plt.cm.gray)
    ANGELMain.calc_Button.clicked.connect(ANGELMain.calc_ngi_thread)
    # ANGELMain.calc_Button.clicked.connect(ANGELMain.calc_ngi)

    _calc_tab_layout(ANGELMain)
    ANGELMain.tabWidget2.addTab(ANGELMain.tab_Calc, _fromUtf8("Calculation"))


def _calc_tab_layout(ANGELMain):
    """
    _calc_tab_layout: Called by _multi_tab responsible for creation of its layout.
    """
    ANGELMain.horizontalLayout_main = QtWidgets.QHBoxLayout(ANGELMain.tab_Calc)
    ANGELMain.horizontalLayout_sub1 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub2 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub3 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub4 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub5 = QtWidgets.QHBoxLayout()
    ANGELMain.verticalLayout = QtWidgets.QVBoxLayout()

    ANGELMain.hline1 = QtWidgets.QFrame()
    ANGELMain.hline1.setFrameStyle(QtWidgets.QFrame.HLine)
    # ANGELMain.hline1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.calc_Button)
    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.calc_progressBar)

    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.mpl_ti_pre_widget)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.mpl_dpci_pre_widget)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.mpl_dfi_pre_widget)
    # ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.first_data_file_Combo)

    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub1)
    ANGELMain.verticalLayout.addStretch(0)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub2)

    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.verticalLayout)


def _vis_tab(ANGELMain):
    """
    _vis_tab:       Second tab of the lower tab widget. Used to show the data and ob visibility map.
                    Can also show the visibility in a specific region.

                    Calls the _vis_tab_layout function which sets up the layout of the tab
    """
    ANGELMain.tab_Vis = QtWidgets.QWidget()

    # ANGELMain.data_dir_Button = QtWidgets.QPushButton("Open data directory")
    # ANGELMain.load_data_Button = QtWidgets.QPushButton("Load selected files")
    # ANGELMain.load_data_Button.setEnabled(False)
    # ANGELMain.calc_Button = QtWidgets.QPushButton("Calculate")
    # ANGELMain.calc_Button.setEnabled(False)
    # ANGELMain.calc_progressBar = QtWidgets.QProgressBar()
    # ANGELMain.calc_progressBar.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)

    ANGELMain.mpl_vis_dat_widget = MatplotlibWidget(ANGELMain.tab_Vis, title="Visibility Data")
    # ANGELMain.mpl_ti_pre_widget.axes.imshow(test_image,cmap=plt.cm.gray)
    # ANGELMain.mpl_vis_dat_widget.axes.set_title("TI")
    # ANGELMain.mpl_ti_widget.figure.colorbar(im)
    # ANGELMain.mpl_ti_widget.axes.

    ANGELMain.mpl_vis_ob_widget = MatplotlibWidget(ANGELMain.tab_Vis, title="Visibility OB")

    ANGELMain.vis_roi_Button = QtWidgets.QPushButton("ROI")
    ANGELMain.vis_roi_Button.setCheckable(True)
    ANGELMain.vis_mean_ob_Label = QtWidgets.QLabel("Average Visibility OB")
    ANGELMain.vis_mean_dat_Label = QtWidgets.QLabel("Average Visibility Data")
    ANGELMain.vis_mean_dat_Box = QtWidgets.QLineEdit()
    ANGELMain.vis_mean_dat_Box.setReadOnly(True)
    ANGELMain.vis_mean_ob_Box = QtWidgets.QLineEdit()
    ANGELMain.vis_mean_ob_Box.setReadOnly(True)

    ANGELMain.vis_vminSpinBox = QtWidgets.QDoubleSpinBox()
    ANGELMain.vis_vminLabel = QtWidgets.QLabel("Min Visibility")
    ANGELMain.vis_vminSpinBox.setRange(0, 1)
    ANGELMain.vis_vminSpinBox.setValue(0)
    ANGELMain.vis_vminSpinBox.setSingleStep(0.01)

    ANGELMain.vis_vmaxSpinBox = QtWidgets.QDoubleSpinBox()
    ANGELMain.vis_vmaxLabel = QtWidgets.QLabel("Max Visibility")
    ANGELMain.vis_vmaxSpinBox.setRange(0, 1)
    ANGELMain.vis_vmaxSpinBox.setValue(0.5)
    ANGELMain.vis_vmaxSpinBox.setSingleStep(0.01)

    # ANGELMain.mpl_vis_ob_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    # ANGELMain.mpl_vis_dat_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    # ANGELMain.vis_roi_Button.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    # ANGELMain.vis_mean_ob_Label.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    # ANGELMain.vis_mean_dat_Label.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    # ANGELMain.vis_mean_dat_Box.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    # ANGELMain.vis_mean_ob_Box.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    # ANGELMain.vis_vminLabel.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    # ANGELMain.vis_vminSpinBox.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    # ANGELMain.vis_vmaxLabel.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    # ANGELMain.vis_vmaxSpinBox.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.vis_roi_Button.clicked.connect(ANGELMain.vis_roi_thread)

    ANGELMain.vis_vminSpinBox.valueChanged.connect(ANGELMain.replot_vis)
    ANGELMain.vis_vmaxSpinBox.valueChanged.connect(ANGELMain.replot_vis)

    _vis_tab_layout(ANGELMain)
    ANGELMain.tabWidget2.addTab(ANGELMain.tab_Vis, _fromUtf8("Visibility"))


def _vis_tab_layout(ANGELMain):
    ANGELMain.horizontalLayout_main = QtWidgets.QHBoxLayout(ANGELMain.tab_Vis)
    ANGELMain.horizontalLayout_sub1 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub2 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub3 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub4 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub5 = QtWidgets.QHBoxLayout()
    ANGELMain.verticalLayout = QtWidgets.QVBoxLayout()

    ANGELMain.horizontalLayout_main.addWidget(ANGELMain.mpl_vis_dat_widget)
    ANGELMain.horizontalLayout_main.addWidget(ANGELMain.mpl_vis_ob_widget)
    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.vis_vminLabel)
    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.vis_vminSpinBox)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.vis_vmaxLabel)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.vis_vmaxSpinBox)
    ANGELMain.verticalLayout.addStretch(0)
    ANGELMain.verticalLayout.addWidget(ANGELMain.vis_roi_Button)
    ANGELMain.verticalLayout.addWidget(ANGELMain.vis_mean_dat_Label)
    ANGELMain.verticalLayout.addWidget(ANGELMain.vis_mean_dat_Box)
    ANGELMain.verticalLayout.addWidget(ANGELMain.vis_mean_ob_Label)
    ANGELMain.verticalLayout.addWidget(ANGELMain.vis_mean_ob_Box)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub1)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub2)
    # ANGELMain.verticalLayout.addStretch(0)

    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.verticalLayout)


def _phase_tab(ANGELMain):
    """
    _phase_tab:     Third tab of the lower tab widget. Used to show the data and ob phase map.
                    Can also show the phase in a specific region.

                    Calls the _phase_tab_layout function which sets up the layout of the tab
    """
    ANGELMain.tab_Phase = QtWidgets.QWidget()

    # ANGELMain.data_dir_Button = QtWidgets.QPushButton("Open data directory")
    # ANGELMain.load_data_Button = QtWidgets.QPushButton("Load selected files")
    # ANGELMain.load_data_Button.setEnabled(False)
    # ANGELMain.calc_Button = QtWidgets.QPushButton("Calculate")
    # ANGELMain.calc_Button.setEnabled(False)
    # ANGELMain.calc_progressBar = QtWidgets.QProgressBar()
    # ANGELMain.calc_progressBar.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)

    ANGELMain.mpl_phase_dat_widget = MatplotlibWidget(ANGELMain.tab_Phase, title="Phase Data")
    # ANGELMain.mpl_ti_pre_widget.axes.imshow(test_image,cmap=plt.cm.gray)
    # ANGELMain.mpl_vis_dat_widget.axes.set_title("TI")
    # ANGELMain.mpl_ti_widget.figure.colorbar(im)
    # ANGELMain.mpl_ti_widget.axes.

    ANGELMain.mpl_phase_ob_widget = MatplotlibWidget(ANGELMain.tab_Phase, title="Phase OB")

    ANGELMain.phase_roi_Button = QtWidgets.QPushButton("ROI")
    ANGELMain.phase_roi_Button.setCheckable(True)
    ANGELMain.phase_mean_ob_Label = QtWidgets.QLabel("Average Phase OB")
    ANGELMain.phase_mean_dat_Label = QtWidgets.QLabel("Average Phase Data")
    ANGELMain.phase_mean_dat_Box = QtWidgets.QLineEdit()
    ANGELMain.phase_mean_dat_Box.setReadOnly(True)
    ANGELMain.phase_mean_ob_Box = QtWidgets.QLineEdit()
    ANGELMain.phase_mean_ob_Box.setReadOnly(True)

    ANGELMain.phase_vminSpinBox = QtWidgets.QDoubleSpinBox()
    ANGELMain.phase_vminLabel = QtWidgets.QLabel("Min Phase")
    ANGELMain.phase_vminSpinBox.setRange(-10, 10)
    ANGELMain.phase_vminSpinBox.setValue(-np.pi)
    ANGELMain.phase_vminSpinBox.setSingleStep(0.01)

    ANGELMain.phase_vmaxSpinBox = QtWidgets.QDoubleSpinBox()
    ANGELMain.phase_vmaxLabel = QtWidgets.QLabel("Max Phase")
    ANGELMain.phase_vmaxSpinBox.setRange(-10, 10)
    ANGELMain.phase_vmaxSpinBox.setValue(np.pi)
    ANGELMain.phase_vmaxSpinBox.setSingleStep(0.01)

    # ANGELMain.mpl_phase_ob_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    # ANGELMain.mpl_phase_dat_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    ANGELMain.phase_roi_Button.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    ANGELMain.phase_mean_ob_Label.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    ANGELMain.phase_mean_dat_Label.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    ANGELMain.phase_mean_dat_Box.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    ANGELMain.phase_mean_ob_Box.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    ANGELMain.phase_vminLabel.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    ANGELMain.phase_vminSpinBox.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    ANGELMain.phase_vmaxLabel.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    ANGELMain.phase_vmaxSpinBox.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

    ANGELMain.phase_roi_Button.clicked.connect(ANGELMain.phase_roi_thread)

    ANGELMain.phase_vminSpinBox.valueChanged.connect(ANGELMain.replot_phase)
    ANGELMain.phase_vmaxSpinBox.valueChanged.connect(ANGELMain.replot_phase)
    # ANGELMain.mpl_dpci_pre_widget.axes.imshow(test_image,cmap=plt.cm.gray)
    # ANGELMain.mpl_vis_ob_widget.axes.set_title("DPCI")

    _phase_tab_layout(ANGELMain)
    ANGELMain.tabWidget2.addTab(ANGELMain.tab_Phase, _fromUtf8("Phase"))


def _phase_tab_layout(ANGELMain):
    ANGELMain.horizontalLayout_main = QtWidgets.QHBoxLayout(ANGELMain.tab_Phase)
    ANGELMain.horizontalLayout_sub1 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub2 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub3 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub4 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub5 = QtWidgets.QHBoxLayout()
    ANGELMain.verticalLayout = QtWidgets.QVBoxLayout()

    ANGELMain.horizontalLayout_main.addWidget(ANGELMain.mpl_phase_dat_widget)
    ANGELMain.horizontalLayout_main.addWidget(ANGELMain.mpl_phase_ob_widget)
    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.phase_vminLabel)
    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.phase_vminSpinBox)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.phase_vmaxLabel)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.phase_vmaxSpinBox)
    ANGELMain.verticalLayout.addStretch(0)
    ANGELMain.verticalLayout.addWidget(ANGELMain.phase_roi_Button)
    ANGELMain.verticalLayout.addWidget(ANGELMain.phase_mean_dat_Label)
    ANGELMain.verticalLayout.addWidget(ANGELMain.phase_mean_dat_Box)
    ANGELMain.verticalLayout.addWidget(ANGELMain.phase_mean_ob_Label)
    ANGELMain.verticalLayout.addWidget(ANGELMain.phase_mean_ob_Box)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub1)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub2)
    # ANGELMain.verticalLayout.addStretch(0)

    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.verticalLayout)


def _ti_tab(ANGELMain):
    """
    _ti_tab:        Fourth tab of the lower tab widget. Used to show the TI image and additional information.
                    On the left side the TI is shown, in the upper right is the oscillation of a choosen pixel.
                    In the lower right corner either a data image or a histogramm of the TI is shown.
                    In the middle between these matplotlibwidgets is the control area, where one can choose to zoom into the
                    TI, choose a pixel in the TI, change the colormap, change the grayvalue limits and unzoom and switch
                    between the data images and the histogramm.
                    It is also possible to save the shown oscillation and save a preliminary TI.


                    Calls the _ti_tab_layout function which sets up the layout of the tab
    """

    ANGELMain.tab_Ti = QtWidgets.QWidget()

    ANGELMain.mpl_ti_widget = MatplotlibWidget(ANGELMain.tab_Ti, title="TI", width=5, height=5)
    ANGELMain.mpl_ti_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    # ANGELMain.ti_toolbar = NavigationToolbar(ANGELMain.mpl_ti_widget, ANGELMain)
    # ANGELMain.toolbar = NavigationToolbar(ANGELMain.ti_canvas, ANGELMain)
    # ANGELMain.toolbar.hide()
    # ANGELMain.mpl_ti_widget.axes.imshow(test_image,cmap=plt.cm.gray)
    ANGELMain.mpl_ti_widget.axes.set_title("TI")

    ANGELMain.mpl_ti_osc_dat_widget = MatplotlibWidget(ANGELMain.tab_Ti, title="Oscillation Data", width=5, height=5)
    # ANGELMain.mpl_ti_osc_dat_widget.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)
    ANGELMain.mpl_ti_osc_dat_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    ANGELMain.mpl_ti_osc_dat_widget.figure.set_tight_layout(True)
    ANGELMain.mpl_ti_osc_dat_widget.axes.set_xlabel("Number of Image")
    ANGELMain.mpl_ti_osc_dat_widget.axes.set_ylabel("Intensity")

    ANGELMain.mpl_ti_line_widget = MatplotlibWidget(ANGELMain.tab_Ti, title="Line Profile", width=5, height=5)
    # ANGELMain.mpl_ti_osc_dat_widget.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)
    ANGELMain.mpl_ti_line_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    ANGELMain.mpl_ti_line_widget.figure.set_tight_layout(True)
    ANGELMain.mpl_ti_line_widget.axes.set_xlabel("Distance")
    ANGELMain.mpl_ti_line_widget.axes.set_ylabel("TI Signal")
    # ANGELMain.mpl_ti_osc_ob_widget = MatplotlibWidget(ANGELMain.tab_Ti,title="Oscillation OB",width=5,height=5)
    ANGELMain.mpl_ti_img_dat_widget = MatplotlibWidget(ANGELMain.tab_Ti, title="Data", width=3, height=3)
    ANGELMain.mpl_ti_img_dat_widget.figure.set_tight_layout(True)
    # ANGELMain.mpl_ti_img_dat_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
    # ANGELMain.mpl_ti_img_dat_widget.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
    # ANGELMain.mpl_ti_img_ob_widget = MatplotlibWidget(ANGELMain.tab_Ti,title="OB",width=5,height=5)
    ANGELMain.ti_vminSpinBox = QtWidgets.QDoubleSpinBox()
    ANGELMain.ti_vminLabel = QtWidgets.QLabel("Min Grayvalue")
    ANGELMain.ti_vminSpinBox.setRange(-50, 50)
    ANGELMain.ti_vminSpinBox.setValue(0.5)
    ANGELMain.ti_vminSpinBox.setSingleStep(0.01)

    ANGELMain.ti_vmaxSpinBox = QtWidgets.QDoubleSpinBox()
    ANGELMain.ti_vmaxLabel = QtWidgets.QLabel("Max Grayvalue")
    ANGELMain.ti_vmaxSpinBox.setRange(-50, 50)
    ANGELMain.ti_vmaxSpinBox.setValue(1)
    ANGELMain.ti_vmaxSpinBox.setSingleStep(0.01)

    ANGELMain.ti_pixel_Button = QtWidgets.QPushButton("Choose Pixel")
    # ANGELMain.ti_zoom_Button.setToolTip("Check to create a ROI in the image. Uncheck to fix the ROI")
    ANGELMain.ti_pixel_Button.setCheckable(True)

    ANGELMain.ti_line_Button = QtWidgets.QPushButton("Plot Profile")
    # ANGELMain.ti_zoom_Button.setToolTip("Check to create a ROI in the image. Uncheck to fix the ROI")
    ANGELMain.ti_line_Button.setCheckable(True)
    # ANGELMain.ti_pixel_Button.setChecked(True)
    ANGELMain.ti_zoom_Button = QtWidgets.QPushButton("Zoom")
    # ANGELMain.ti_zoom_Button.setToolTip("Check to create a ROI in the image. Uncheck to fix the ROI")
    ANGELMain.ti_zoom_Button.setCheckable(True)
    ANGELMain.ti_unzoom_Button = QtWidgets.QPushButton("Unzoom")
    ANGELMain.ti_color_Label = QtWidgets.QLabel("Colormap")
    ANGELMain.ti_color_Combo = QtWidgets.QComboBox()
    ANGELMain.ti_color_Combo.addItems(['gray', 'magma', 'inferno', 'plasma', 'viridis', 'parcula'])
    ANGELMain.mpl_ti_hist_widget = MatplotlibWidget(ANGELMain.tab_Ti, title="Histogram of Ti", width=3, height=3)
    # ANGELMain.mpl_ti_hist_widget.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
    ANGELMain.mpl_ti_hist_widget.figure.set_tight_layout(True)
    ANGELMain.mpl_ti_hist_widget.axes.set_xlabel("Grayvalue")
    ANGELMain.mpl_ti_hist_widget.axes.set_ylabel("Number of Pixels")
    ANGELMain.ti_hist_dat_Button = QtWidgets.QPushButton("Show Histogram")
    ANGELMain.ti_osc_line_Button = QtWidgets.QPushButton("Show Line Profile")
    ANGELMain.ti_cbar = None
    ANGELMain.ti_save_Button = QtWidgets.QPushButton("Save Oscillation")

    ANGELMain.ti_save_Button2 = QtWidgets.QPushButton("Save TI")
    # ANGELMain.ti_save_Button2.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
    ANGELMain.ti_line_save_Button = QtWidgets.QPushButton("Save TI Line Profile")

    ANGELMain.ti_vminSpinBox.valueChanged.connect(ANGELMain.replot_img)
    ANGELMain.ti_vmaxSpinBox.valueChanged.connect(ANGELMain.replot_img)
    ANGELMain.ti_zoom_Button.clicked.connect(ANGELMain.zoom_handling)
    ANGELMain.ti_unzoom_Button.clicked.connect(ANGELMain.unzoom_handling)
    ANGELMain.ti_pixel_Button.clicked.connect(ANGELMain.pixel_handling)
    ANGELMain.ti_line_Button.clicked.connect(ANGELMain.line_handling)
    ANGELMain.ti_color_Combo.currentIndexChanged.connect(ANGELMain.replot_img)
    ANGELMain.ti_hist_dat_Button.clicked.connect(ANGELMain.data_hist_switch)
    ANGELMain.ti_osc_line_Button.clicked.connect(ANGELMain.osc_line_switch)
    ANGELMain.ti_save_Button.clicked.connect(ANGELMain.save_oscillation_handling)
    ANGELMain.ti_save_Button2.clicked.connect(ANGELMain.save_img_handling)
    ANGELMain.ti_line_save_Button.clicked.connect(ANGELMain.save_line_handling)

    _ti_tab_layout(ANGELMain)
    ANGELMain.tabWidget2.addTab(ANGELMain.tab_Ti, _fromUtf8("TI"))


def _ti_tab_layout(ANGELMain):
    ANGELMain.horizontalLayout_main = QtWidgets.QHBoxLayout(ANGELMain.tab_Ti)
    ANGELMain.horizontalLayout_sub1 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub2 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub2_1 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub3 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub4 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub5 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub6 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub7 = QtWidgets.QHBoxLayout()
    ANGELMain.gridLayout = QtWidgets.QGridLayout()
    ANGELMain.verticalLayout = QtWidgets.QVBoxLayout()
    ANGELMain.verticalLayout2 = QtWidgets.QVBoxLayout()

    # ANGELMain.hline1=QtWidgets.QFrame()
    # ANGELMain.hline1.setFrameStyle(QtWidgets.QFrame.HLine)
    # ANGELMain.hline1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Minimum)

    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.ti_pixel_Button)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.ti_line_Button)
    ANGELMain.horizontalLayout_sub2_1.addWidget(ANGELMain.ti_zoom_Button)

    ANGELMain.horizontalLayout_sub2_1.addWidget(ANGELMain.ti_unzoom_Button)
    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.ti_osc_line_Button)
    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.ti_hist_dat_Button)
    ANGELMain.horizontalLayout_sub4.addWidget(ANGELMain.ti_vminLabel)
    ANGELMain.horizontalLayout_sub4.addWidget(ANGELMain.ti_vminSpinBox)
    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.ti_vmaxLabel)
    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.ti_vmaxSpinBox)
    ANGELMain.horizontalLayout_sub6.addWidget(ANGELMain.ti_color_Label)
    ANGELMain.horizontalLayout_sub6.addWidget(ANGELMain.ti_color_Combo)

    ANGELMain.horizontalLayout_sub7.addWidget(ANGELMain.ti_save_Button)
    ANGELMain.horizontalLayout_sub7.addWidget(ANGELMain.ti_line_save_Button)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub2)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub2_1)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub3)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub4)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub5)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub6)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub7)
    ANGELMain.verticalLayout2.addWidget(ANGELMain.ti_save_Button2)
    # ANGELMain.verticalLayout2.addWidget(ANGELMain.mpl_ti_hist_widget)
    # ANGELMain.verticalLayout2.addStretch(0)
    # ANGELMain.gridLayout.addLayout(ANGELMain.verticalLayout2,2,1)
    # ANGELMain.gridLayout.addWidget(ANGELMain.mpl_ti_img_dat_widget,2,2)
    # ANGELMain.gridLayout.addWidget(ANGELMain.mpl_ti_img_ob_widget,2,2)
    # ANGELMain.gridLayout.addWidget(ANGELMain.mpl_ti_osc_dat_widget,1,1)
    # ANGELMain.gridLayout.addWidget(ANGELMain.mpl_ti_osc_ob_widget,2,1)
    # ANGELMain.horizontalLayout_sub2.addLayout(ANGELMain.gridLayout)

    ANGELMain.horizontalLayout_sub1.addLayout(ANGELMain.verticalLayout2)
    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.mpl_ti_img_dat_widget)
    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.mpl_ti_hist_widget)
    ANGELMain.mpl_ti_hist_widget.hide()

    ANGELMain.verticalLayout.addWidget(ANGELMain.mpl_ti_osc_dat_widget)
    ANGELMain.verticalLayout.addWidget(ANGELMain.mpl_ti_line_widget)
    ANGELMain.mpl_ti_line_widget.hide()
    # ANGELMain.verticalLayout.addStretch(0)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub1)

    ANGELMain.horizontalLayout_main.addWidget(ANGELMain.mpl_ti_widget)
    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.verticalLayout)


def _dpci_tab(ANGELMain):
    """
    _dpci_tab:          Fifth tab of the lower tab widget. Used to show the DPCI image and additional information.
                        Similar to _ti_tab


                        Calls the _ti_tab_layout function which sets up the layout of the tab
    """
    ANGELMain.tab_Dpci = QtWidgets.QWidget()

    ANGELMain.mpl_dpci_widget = MatplotlibWidget(ANGELMain.tab_Dpci, title="DPCI", width=5, height=5)
    # ANGELMain.dpci_toolbar = NavigationToolbar(ANGELMain.mpl_dpci_widget, ANGELMain)
    ANGELMain.mpl_dpci_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)

    # ANGELMain.toolbar = NavigationToolbar(ANGELMain.ti_canvas, ANGELMain)
    # ANGELMain.toolbar.hide()
    # ANGELMain.mpl_ti_widget.axes.imshow(test_image,cmap=plt.cm.gray)
    ANGELMain.mpl_dpci_widget.axes.set_title("DPCI")

    ANGELMain.mpl_dpci_osc_dat_widget = MatplotlibWidget(ANGELMain.tab_Dpci, title="Oscillation Data", width=5,
                                                         height=5)
    ANGELMain.mpl_dpci_osc_dat_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    ANGELMain.mpl_dpci_osc_dat_widget.figure.set_tight_layout(True)
    ANGELMain.mpl_dpci_osc_dat_widget.axes.set_xlabel("Number of Image")
    ANGELMain.mpl_dpci_osc_dat_widget.axes.set_ylabel("Intensity")

    ANGELMain.mpl_dpci_line_widget = MatplotlibWidget(ANGELMain.tab_Dpci, title="Line Profile", width=5, height=5)
    # ANGELMain.mpl_ti_osc_dat_widget.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)
    ANGELMain.mpl_dpci_line_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    ANGELMain.mpl_dpci_line_widget.figure.set_tight_layout(True)
    ANGELMain.mpl_dpci_line_widget.axes.set_xlabel("Distance")
    ANGELMain.mpl_dpci_line_widget.axes.set_ylabel("DPCI Signal")

    # ANGELMain.mpl_ti_osc_ob_widget = MatplotlibWidget(ANGELMain.tab_Ti,title="Oscillation OB",width=5,height=5)
    ANGELMain.mpl_dpci_img_dat_widget = MatplotlibWidget(ANGELMain.tab_Dpci, title="Data", width=3, height=3)
    ANGELMain.mpl_dpci_img_dat_widget.figure.set_tight_layout(True)
    # ANGELMain.mpl_dpci_img_dat_widget.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
    # ANGELMain.mpl_ti_img_ob_widget = MatplotlibWidget(ANGELMain.tab_Ti,title="OB",width=5,height=5)
    ANGELMain.dpci_vminSpinBox = QtWidgets.QDoubleSpinBox()
    ANGELMain.dpci_vminLabel = QtWidgets.QLabel("Min Grayvalue")
    ANGELMain.dpci_vminSpinBox.setRange(-50, 50)
    ANGELMain.dpci_vminSpinBox.setValue(-np.pi)
    ANGELMain.dpci_vminSpinBox.setSingleStep(0.01)

    ANGELMain.dpci_vmaxSpinBox = QtWidgets.QDoubleSpinBox()
    ANGELMain.dpci_vmaxLabel = QtWidgets.QLabel("Max Grayvalue")
    ANGELMain.dpci_vmaxSpinBox.setRange(-50, 50)
    ANGELMain.dpci_vmaxSpinBox.setValue(np.pi)
    ANGELMain.dpci_vmaxSpinBox.setSingleStep(0.01)

    ANGELMain.dpci_pixel_Button = QtWidgets.QPushButton("Choose Pixel")
    # ANGELMain.ti_zoom_Button.setToolTip("Check to create a ROI in the image. Uncheck to fix the ROI")
    ANGELMain.dpci_pixel_Button.setCheckable(True)

    ANGELMain.dpci_line_Button = QtWidgets.QPushButton("Plot Profile")
    # ANGELMain.ti_zoom_Button.setToolTip("Check to create a ROI in the image. Uncheck to fix the ROI")
    ANGELMain.dpci_line_Button.setCheckable(True)
    # ANGELMain.ti_pixel_Button.setChecked(True)
    ANGELMain.dpci_zoom_Button = QtWidgets.QPushButton("Zoom")
    # ANGELMain.ti_zoom_Button.setToolTip("Check to create a ROI in the image. Uncheck to fix the ROI")
    ANGELMain.dpci_zoom_Button.setCheckable(True)
    ANGELMain.dpci_unzoom_Button = QtWidgets.QPushButton("Unzoom")
    ANGELMain.dpci_color_Label = QtWidgets.QLabel("Colormap")
    ANGELMain.dpci_color_Combo = QtWidgets.QComboBox()
    ANGELMain.dpci_color_Combo.addItems(['gray', 'magma', 'inferno', 'plasma', 'viridis', 'parcula'])
    ANGELMain.mpl_dpci_hist_widget = MatplotlibWidget(ANGELMain.tab_Ti, title="Histogram of DPCI", width=3, height=3)
    # ANGELMain.mpl_dpci_hist_widget.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
    ANGELMain.mpl_dpci_hist_widget.figure.set_tight_layout(True)
    ANGELMain.mpl_dpci_hist_widget.axes.set_xlabel("Grayvalue")
    ANGELMain.mpl_dpci_hist_widget.axes.set_ylabel("Number of Pixels")
    ANGELMain.dpci_hist_dat_Button = QtWidgets.QPushButton("Show Histogram")
    ANGELMain.dpci_osc_line_Button = QtWidgets.QPushButton("Show Line Profile")
    ANGELMain.dpci_cbar = None
    ANGELMain.dpci_save_Button = QtWidgets.QPushButton("Save Oscillation")

    ANGELMain.dpci_save_Button2 = QtWidgets.QPushButton("Save DPCI")
    # ANGELMain.dpci_save_Button2.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
    ANGELMain.dpci_line_save_Button = QtWidgets.QPushButton("Save DPCI Line Profile")

    ANGELMain.dpci_vminSpinBox.valueChanged.connect(ANGELMain.replot_img)
    ANGELMain.dpci_vmaxSpinBox.valueChanged.connect(ANGELMain.replot_img)
    ANGELMain.dpci_zoom_Button.clicked.connect(ANGELMain.zoom_handling)
    ANGELMain.dpci_unzoom_Button.clicked.connect(ANGELMain.unzoom_handling)
    ANGELMain.dpci_pixel_Button.clicked.connect(ANGELMain.pixel_handling)
    ANGELMain.dpci_line_Button.clicked.connect(ANGELMain.line_handling)
    ANGELMain.dpci_color_Combo.currentIndexChanged.connect(ANGELMain.replot_img)
    ANGELMain.dpci_hist_dat_Button.clicked.connect(ANGELMain.data_hist_switch)
    ANGELMain.dpci_osc_line_Button.clicked.connect(ANGELMain.osc_line_switch)
    ANGELMain.dpci_save_Button.clicked.connect(ANGELMain.save_oscillation_handling)
    ANGELMain.dpci_save_Button2.clicked.connect(ANGELMain.save_img_handling)
    ANGELMain.dpci_line_save_Button.clicked.connect(ANGELMain.save_line_handling)

    _dpci_tab_layout(ANGELMain)
    ANGELMain.tabWidget2.addTab(ANGELMain.tab_Dpci, _fromUtf8("DPCI"))


def _dpci_tab_layout(ANGELMain):
    ANGELMain.horizontalLayout_main = QtWidgets.QHBoxLayout(ANGELMain.tab_Dpci)
    ANGELMain.horizontalLayout_sub1 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub2 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub2_1 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub3 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub4 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub5 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub6 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub7 = QtWidgets.QHBoxLayout()
    ANGELMain.gridLayout = QtWidgets.QGridLayout()
    ANGELMain.verticalLayout = QtWidgets.QVBoxLayout()
    ANGELMain.verticalLayout2 = QtWidgets.QVBoxLayout()

    # ANGELMain.hline1=QtWidgets.QFrame()
    # ANGELMain.hline1.setFrameStyle(QtWidgets.QFrame.HLine)
    # ANGELMain.hline1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Minimum)

    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.dpci_pixel_Button)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.dpci_line_Button)
    ANGELMain.horizontalLayout_sub2_1.addWidget(ANGELMain.dpci_zoom_Button)

    ANGELMain.horizontalLayout_sub2_1.addWidget(ANGELMain.dpci_unzoom_Button)
    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.dpci_osc_line_Button)
    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.dpci_hist_dat_Button)
    ANGELMain.horizontalLayout_sub4.addWidget(ANGELMain.dpci_vminLabel)
    ANGELMain.horizontalLayout_sub4.addWidget(ANGELMain.dpci_vminSpinBox)
    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.dpci_vmaxLabel)
    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.dpci_vmaxSpinBox)
    ANGELMain.horizontalLayout_sub6.addWidget(ANGELMain.dpci_color_Label)
    ANGELMain.horizontalLayout_sub6.addWidget(ANGELMain.dpci_color_Combo)

    ANGELMain.horizontalLayout_sub7.addWidget(ANGELMain.dpci_save_Button)
    ANGELMain.horizontalLayout_sub7.addWidget(ANGELMain.dpci_line_save_Button)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub2)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub2_1)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub3)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub4)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub5)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub6)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub7)
    ANGELMain.verticalLayout2.addWidget(ANGELMain.dpci_save_Button2)
    # ANGELMain.verticalLayout2.addWidget(ANGELMain.mpl_ti_hist_widget)
    # ANGELMain.verticalLayout2.addStretch(0)
    # ANGELMain.gridLayout.addLayout(ANGELMain.verticalLayout2,2,1)
    # ANGELMain.gridLayout.addWidget(ANGELMain.mpl_ti_img_dat_widget,2,2)
    # ANGELMain.gridLayout.addWidget(ANGELMain.mpl_ti_img_ob_widget,2,2)
    # ANGELMain.gridLayout.addWidget(ANGELMain.mpl_ti_osc_dat_widget,1,1)
    # ANGELMain.gridLayout.addWidget(ANGELMain.mpl_ti_osc_ob_widget,2,1)
    # ANGELMain.horizontalLayout_sub2.addLayout(ANGELMain.gridLayout)

    ANGELMain.horizontalLayout_sub1.addLayout(ANGELMain.verticalLayout2)
    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.mpl_dpci_img_dat_widget)
    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.mpl_dpci_hist_widget)
    ANGELMain.mpl_dpci_hist_widget.hide()

    ANGELMain.verticalLayout.addWidget(ANGELMain.mpl_dpci_osc_dat_widget)
    ANGELMain.verticalLayout.addWidget(ANGELMain.mpl_dpci_line_widget)
    ANGELMain.mpl_dpci_line_widget.hide()
    # ANGELMain.verticalLayout.addStretch(0)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub1)

    ANGELMain.horizontalLayout_main.addWidget(ANGELMain.mpl_dpci_widget)
    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.verticalLayout)


def _dfi_tab(ANGELMain):
    """
    _dfi_tab:           Sixth tab of the lower tab widget. Used to show the DFI image and additional information.
                        Similar to _ti_tab


                        Calls the _dfi_tab_layout function which sets up the layout of the tab
    """
    ANGELMain.tab_Dfi = QtWidgets.QWidget()

    ANGELMain.mpl_dfi_widget = MatplotlibWidget(ANGELMain.tab_Dfi, title="DFI", width=5, height=5)
    ANGELMain.mpl_dfi_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)

    # ANGELMain.dfi_toolbar = NavigationToolbar(ANGELMain.mpl_dfi_widget, ANGELMain)
    # ANGELMain.toolbar = NavigationToolbar(ANGELMain.ti_canvas, ANGELMain)
    # ANGELMain.toolbar.hide()
    # ANGELMain.mpl_ti_widget.axes.imshow(test_image,cmap=plt.cm.gray)
    ANGELMain.mpl_dfi_widget.axes.set_title("DFI")

    ANGELMain.mpl_dfi_osc_dat_widget = MatplotlibWidget(ANGELMain.tab_Dfi, title="Oscillation Data", width=5, height=5)
    ANGELMain.mpl_dfi_osc_dat_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    ANGELMain.mpl_dfi_osc_dat_widget.figure.set_tight_layout(True)
    ANGELMain.mpl_dfi_osc_dat_widget.axes.set_xlabel("Number of Image")
    ANGELMain.mpl_dfi_osc_dat_widget.axes.set_ylabel("Intensity")

    ANGELMain.mpl_dfi_line_widget = MatplotlibWidget(ANGELMain.tab_Dfi, title="Line Profile", width=5, height=5)
    # ANGELMain.mpl_ti_osc_dat_widget.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)
    ANGELMain.mpl_dfi_line_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    ANGELMain.mpl_dfi_line_widget.figure.set_tight_layout(True)
    ANGELMain.mpl_dfi_line_widget.axes.set_xlabel("Distance")
    ANGELMain.mpl_dfi_line_widget.axes.set_ylabel("DFI Signal")
    # ANGELMain.mpl_ti_osc_ob_widget = MatplotlibWidget(ANGELMain.tab_Ti,title="Oscillation OB",width=5,height=5)
    ANGELMain.mpl_dfi_img_dat_widget = MatplotlibWidget(ANGELMain.tab_Dfi, title="Data", width=3, height=3)
    ANGELMain.mpl_dfi_img_dat_widget.figure.set_tight_layout(True)
    # ANGELMain.mpl_dfi_img_dat_widget.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
    # ANGELMain.mpl_ti_img_ob_widget = MatplotlibWidget(ANGELMain.tab_Ti,title="OB",width=5,height=5)
    ANGELMain.dfi_vminSpinBox = QtWidgets.QDoubleSpinBox()
    ANGELMain.dfi_vminLabel = QtWidgets.QLabel("Min Grayvalue")
    ANGELMain.dfi_vminSpinBox.setRange(-50, 50)
    ANGELMain.dfi_vminSpinBox.setValue(0.5)
    ANGELMain.dfi_vminSpinBox.setSingleStep(0.01)

    ANGELMain.dfi_vmaxSpinBox = QtWidgets.QDoubleSpinBox()
    ANGELMain.dfi_vmaxLabel = QtWidgets.QLabel("Max Grayvalue")
    ANGELMain.dfi_vmaxSpinBox.setRange(-50, 50)
    ANGELMain.dfi_vmaxSpinBox.setValue(1)
    ANGELMain.dfi_vmaxSpinBox.setSingleStep(0.01)

    ANGELMain.dfi_pixel_Button = QtWidgets.QPushButton("Choose Pixel")
    # ANGELMain.ti_zoom_Button.setToolTip("Check to create a ROI in the image. Uncheck to fix the ROI")
    ANGELMain.dfi_pixel_Button.setCheckable(True)
    # ANGELMain.ti_pixel_Button.setChecked(True)
    ANGELMain.dfi_line_Button = QtWidgets.QPushButton("Plot Profile")
    # ANGELMain.ti_zoom_Button.setToolTip("Check to create a ROI in the image. Uncheck to fix the ROI")
    ANGELMain.dfi_line_Button.setCheckable(True)

    ANGELMain.dfi_zoom_Button = QtWidgets.QPushButton("Zoom")
    # ANGELMain.ti_zoom_Button.setToolTip("Check to create a ROI in the image. Uncheck to fix the ROI")
    ANGELMain.dfi_zoom_Button.setCheckable(True)
    ANGELMain.dfi_unzoom_Button = QtWidgets.QPushButton("Unzoom")
    ANGELMain.dfi_color_Label = QtWidgets.QLabel("Colormap")
    ANGELMain.dfi_color_Combo = QtWidgets.QComboBox()
    ANGELMain.dfi_color_Combo.addItems(['gray', 'magma', 'inferno', 'plasma', 'viridis', 'parcula'])
    ANGELMain.mpl_dfi_hist_widget = MatplotlibWidget(ANGELMain.tab_Ti, title="Histogram of DFI", width=3, height=3)
    # ANGELMain.mpl_dfi_hist_widget.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
    ANGELMain.mpl_dfi_hist_widget.figure.set_tight_layout(True)
    ANGELMain.mpl_dfi_hist_widget.axes.set_xlabel("Grayvalue")
    ANGELMain.mpl_dfi_hist_widget.axes.set_ylabel("Number of Pixels")
    ANGELMain.dfi_hist_dat_Button = QtWidgets.QPushButton("Show Histogram")
    ANGELMain.dfi_osc_line_Button = QtWidgets.QPushButton("Show Line Profile")
    ANGELMain.dfi_cbar = None
    ANGELMain.dfi_save_Button = QtWidgets.QPushButton("Save Oscillation")

    ANGELMain.dfi_save_Button2 = QtWidgets.QPushButton("Save DFI")
    # ANGELMain.dfi_save_Button2.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
    ANGELMain.dfi_line_save_Button = QtWidgets.QPushButton("Save DFI Line Profile")

    ANGELMain.dfi_vminSpinBox.valueChanged.connect(ANGELMain.replot_img)
    ANGELMain.dfi_vmaxSpinBox.valueChanged.connect(ANGELMain.replot_img)
    ANGELMain.dfi_zoom_Button.clicked.connect(ANGELMain.zoom_handling)
    ANGELMain.dfi_unzoom_Button.clicked.connect(ANGELMain.unzoom_handling)
    ANGELMain.dfi_pixel_Button.clicked.connect(ANGELMain.pixel_handling)
    ANGELMain.dfi_line_Button.clicked.connect(ANGELMain.line_handling)
    ANGELMain.dfi_color_Combo.currentIndexChanged.connect(ANGELMain.replot_img)
    ANGELMain.dfi_hist_dat_Button.clicked.connect(ANGELMain.data_hist_switch)
    ANGELMain.dfi_osc_line_Button.clicked.connect(ANGELMain.osc_line_switch)
    ANGELMain.dfi_save_Button.clicked.connect(ANGELMain.save_oscillation_handling)
    ANGELMain.dfi_save_Button2.clicked.connect(ANGELMain.save_img_handling)
    ANGELMain.dfi_line_save_Button.clicked.connect(ANGELMain.save_line_handling)

    _dfi_tab_layout(ANGELMain)
    ANGELMain.tabWidget2.addTab(ANGELMain.tab_Dfi, _fromUtf8("DFI"))


def _dfi_tab_layout(ANGELMain):
    ANGELMain.horizontalLayout_main = QtWidgets.QHBoxLayout(ANGELMain.tab_Dfi)
    ANGELMain.horizontalLayout_sub1 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub2 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub2_1 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub3 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub4 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub5 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub6 = QtWidgets.QHBoxLayout()
    ANGELMain.horizontalLayout_sub7 = QtWidgets.QHBoxLayout()
    ANGELMain.gridLayout = QtWidgets.QGridLayout()
    ANGELMain.verticalLayout = QtWidgets.QVBoxLayout()
    ANGELMain.verticalLayout2 = QtWidgets.QVBoxLayout()

    # ANGELMain.hline1=QtWidgets.QFrame()
    # ANGELMain.hline1.setFrameStyle(QtWidgets.QFrame.HLine)
    # ANGELMain.hline1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Minimum)

    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.dfi_pixel_Button)
    ANGELMain.horizontalLayout_sub2.addWidget(ANGELMain.dfi_line_Button)
    ANGELMain.horizontalLayout_sub2_1.addWidget(ANGELMain.dfi_zoom_Button)

    ANGELMain.horizontalLayout_sub2_1.addWidget(ANGELMain.dfi_unzoom_Button)
    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.dfi_osc_line_Button)
    ANGELMain.horizontalLayout_sub3.addWidget(ANGELMain.dfi_hist_dat_Button)
    ANGELMain.horizontalLayout_sub4.addWidget(ANGELMain.dfi_vminLabel)
    ANGELMain.horizontalLayout_sub4.addWidget(ANGELMain.dfi_vminSpinBox)
    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.dfi_vmaxLabel)
    ANGELMain.horizontalLayout_sub5.addWidget(ANGELMain.dfi_vmaxSpinBox)
    ANGELMain.horizontalLayout_sub6.addWidget(ANGELMain.dfi_color_Label)
    ANGELMain.horizontalLayout_sub6.addWidget(ANGELMain.dfi_color_Combo)

    ANGELMain.horizontalLayout_sub7.addWidget(ANGELMain.dfi_save_Button)
    ANGELMain.horizontalLayout_sub7.addWidget(ANGELMain.dfi_line_save_Button)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub2)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub2_1)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub3)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub4)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub5)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub6)
    ANGELMain.verticalLayout2.addLayout(ANGELMain.horizontalLayout_sub7)
    ANGELMain.verticalLayout2.addWidget(ANGELMain.dfi_save_Button2)
    # ANGELMain.verticalLayout2.addWidget(ANGELMain.mpl_ti_hist_widget)
    # ANGELMain.verticalLayout2.addStretch(0)
    # ANGELMain.gridLayout.addLayout(ANGELMain.verticalLayout2,2,1)
    # ANGELMain.gridLayout.addWidget(ANGELMain.mpl_ti_img_dat_widget,2,2)
    # ANGELMain.gridLayout.addWidget(ANGELMain.mpl_ti_img_ob_widget,2,2)
    # ANGELMain.gridLayout.addWidget(ANGELMain.mpl_ti_osc_dat_widget,1,1)
    # ANGELMain.gridLayout.addWidget(ANGELMain.mpl_ti_osc_ob_widget,2,1)
    # ANGELMain.horizontalLayout_sub2.addLayout(ANGELMain.gridLayout)

    ANGELMain.horizontalLayout_sub1.addLayout(ANGELMain.verticalLayout2)
    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.mpl_dfi_img_dat_widget)
    ANGELMain.horizontalLayout_sub1.addWidget(ANGELMain.mpl_dfi_hist_widget)
    ANGELMain.mpl_dfi_hist_widget.hide()

    ANGELMain.verticalLayout.addWidget(ANGELMain.mpl_dfi_osc_dat_widget)
    ANGELMain.verticalLayout.addWidget(ANGELMain.mpl_dfi_line_widget)
    ANGELMain.mpl_dfi_line_widget.hide()
    # ANGELMain.verticalLayout.addStretch(0)
    ANGELMain.verticalLayout.addLayout(ANGELMain.horizontalLayout_sub1)

    ANGELMain.horizontalLayout_main.addWidget(ANGELMain.mpl_dfi_widget)
    ANGELMain.horizontalLayout_main.addLayout(ANGELMain.verticalLayout)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
