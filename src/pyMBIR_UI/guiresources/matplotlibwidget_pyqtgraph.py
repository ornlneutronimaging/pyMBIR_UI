# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 10:18:04 2015

@author: tneuwirt
"""
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtCore import QSize
from PyQt4 import QtCore, QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import os
from matplotlib import rcParams
from matplotlib.patches import Rectangle
import numpy as np
import pyqtgraph as pg

rcParams['font.size'] = 9


class MatplotlibWidget(FigureCanvas):
    """
    MatplotlibWidget inherits PyQt4.QtGui.QWidget
    and matplotlib.backend_bases.FigureCanvasBase

    Options: option_name (default_value)
    -------
    parent (None): parent widget
    title (''): figure title
    xlabel (''): X-axis label
    ylabel (''): Y-axis label
    xlim (None): X-axis limits ([min, max])
    ylim (None): Y-axis limits ([min, max])
    xscale ('linear'): X-axis scale
    yscale ('linear'): Y-axis scale
    width (4): width in inches
    height (3): height in inches
    dpi (100): resolution in dpi
    hold (False): if False, figure will be cleared each time plot is called

    Widget attributes:
    -----------------
    figure: instance of matplotlib.figure.Figure
    axes: figure axes

    Example:
    -------
    self.widget = MatplotlibWidget(self, yscale='log', hold=True)
    from numpy import linspace
    x = linspace(-10, 10)
    self.widget.axes.plot(x, x**2)
    self.wdiget.axes.plot(x, x**3)
    """
    def __init__(self, parent=None, title='', xlabel='', ylabel='',
                 xlim=None, ylim=None, xscale='linear', yscale='linear',
                 width=3, height=3, dpi=100, hold=False):
        self.figure = Figure(figsize=(width, height), dpi=dpi)



        self.axes = self.figure.add_subplot(111)
        self.axes.set_title(title)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        if xscale is not None:
            self.axes.set_xscale(xscale)
        if yscale is not None:
            self.axes.set_yscale(yscale)
        if xlim is not None:
            self.axes.set_xlim(*xlim)
        if ylim is not None:
            self.axes.set_ylim(*ylim)
        self.axes.hold(hold)

        self.canvas=FigureCanvas.__init__(self, self.figure)


        self.setParent(parent)

        #Canvas.setSizePolicy(self, QSizePolicy.Preferred, QSizePolicy.Preferred)
        policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        policy.setHeightForWidth(True)
        FigureCanvas.setSizePolicy(self,policy)
        FigureCanvas.updateGeometry(self)
    def heightForWidth(self,width):
        return width
    def widthForHeight(self,height):
        return height
    def sizeHint(self):
        w, h = self.get_width_height()
        return QSize(w, h)

    def minimumSizeHint(self):
        return QSize(10, 10)
class Preview(QtGui.QWidget):
    #roiSignal = QtCore.pyqtSignal()
    def __init__(self,name):
        QtGui.QWidget.__init__(self)
        QtGui.QWidget.resize(self,700,700)
        QtGui.QWidget.setWindowTitle(self,name)
        self.data_list=[]
        self.ob_list=[]
        self.dc_list=[]
        self.filter_list=[]
        self.load_filter_list=[]
        self.img_filter_list=[]
        # a figure instance to plot on
        self.figure = pg.ImageView()
        self.figure.show()


        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        #self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        #self.toolbar = NavigationToolbar(self.figure, self)
        self.roi_Button=QtGui.QPushButton("ROI")
        self.roi_Button.setToolTip("Check to create a ROI in the image. Uncheck to fix the ROI")
        self.roi_Button.setCheckable(True)
        self.norm_roi_Button=QtGui.QPushButton("Norm ROI")
        self.norm_roi_Button.setToolTip("Check to create a normalization ROI in the image. Uncheck to fix the ROI")
        self.norm_roi_Button.setCheckable(True)
        self.oscillation_Button=QtGui.QPushButton("Oscillation")
        self.oscillation_Button.setEnabled(False)
        self.oscillation_Button.setToolTip("Plots the oscillation of the Data images and the OB images in the chosen ROI")
        self.reset_Button=QtGui.QPushButton("ROI Reset")
        self.reset_Button.setToolTip("Resets the ROI")
        #self.toolbar.addWidget(self.roi_Button)
        #self.toolbar.addWidget(self.norm_roi_Button)
        #self.toolbar.addWidget(self.reset_Button)
        #self.toolbar.addWidget(self.oscillation_Button)


        self.vminSpinBox=QtGui.QSpinBox()
        self.vminLabel=QtGui.QLabel("Min Grayvalue")
        self.vminSpinBox.setRange(0,64000)
        self.vminSpinBox.setSingleStep(500)

        self.vmaxSpinBox=QtGui.QSpinBox()
        self.vmaxLabel=QtGui.QLabel("Max Grayvalue")
        self.vmaxSpinBox.setRange(0,64000)
        self.vmaxSpinBox.setValue(32000)
        self.vmaxSpinBox.setSingleStep(500)




        # Just some button connected to `plot` method
        self.typeCombo = QtGui.QComboBox()

        self.imgCombo = QtGui.QComboBox()



        #self.roi_Button.clicked.connect(self.roi)
        #self.norm_roi_Button.clicked.connect(self.norm_roi)
        #self.oscillation_Button.clicked.connect(self.oscillation)
        #self.reset_Button.clicked.connect(self.roi_reset)


        self.typeCombo.currentIndexChanged.connect(self.choose_type)
        self.imgCombo.currentIndexChanged.connect(self.choose_img)
        #self.vminSpinBox.valueChanged.connect(self.change_limit)
        #self.vmaxSpinBox.valueChanged.connect(self.change_limit)
        #self.ax = self.figure.axes

        # set the layout
        layout = QtGui.QVBoxLayout()
        layout2 = QtGui.QHBoxLayout()
        layout3 = QtGui.QHBoxLayout()
        #layout.addWidget(self.toolbar)
        layout.addWidget(self.figure)

        layout2.addWidget(self.typeCombo)
        layout2.addWidget(self.imgCombo)
        layout3.addWidget(self.vminLabel)
        layout3.addWidget(self.vminSpinBox)
        layout3.addWidget(self.vmaxLabel)
        layout3.addWidget(self.vmaxSpinBox)
        layout.addLayout(layout3)
        layout.addLayout(layout2)
        self.setLayout(layout)
    """
    def roi_reset(self):
        self.ax.hold(False)
        if self.typeCombo.currentText() == "Data Images":
            self.figure.setImage(self.data_list[1][self.data_list[0].index(str(self.imgCombo.currentText()))])

        elif self.typeCombo.currentText() == "OB Images":
            self.figure.setImage(self.ob_list[1][self.ob_list[0].index(str(self.imgCombo.currentText()))])

        elif self.typeCombo.currentText() == "DC Images":
            self.figure.setImage(self.dc_list[1][self.dc_list[0].index(str(self.imgCombo.currentText()))])
        roi_y1,roi_x1 = self.data_list[1][0].shape
        region_data = np.array(self.data_list[1][0][0:roi_y1, 0:roi_x1])
        #print region_data
        #print np.median(region_data), type(np.median(region_data))
        self.roi_list=[0,roi_y1,0,roi_x1]
        self.vmaxSpinBox.setValue(int(1.2 *int(np.max(region_data))))

        #self.roiSignal.emit(roi_list)
        self.emit(QtCore.SIGNAL('roi'),self.roi_list)

    def roi(self):

        self.oscillation_Button.setEnabled(False)

        if self.roi_Button.isChecked() == True:
            #ax = self.figure.add_subplot(111)
            #plt.set_cmap('gray')
            #self.ax.hold(False)
            if self.typeCombo.currentText() == "Data Images":
                self.img=self.ax.imshow(self.data_list[1][self.data_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

            elif self.typeCombo.currentText() == "OB Images":
                self.img=self.ax.imshow(self.ob_list[1][self.ob_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

            elif self.typeCombo.currentText() == "DC Images":
                self.img=self.ax.imshow(self.dc_list[1][self.dc_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

            self.roi_create=ROI(self.ax)
            self.typeCombo.setEnabled(False)
            self.imgCombo.setEnabled(False)

        else:
            roi_x0,roi_x1,roi_y0,roi_y1=self.roi_create._exit()
            len_data_l=len(self.data_list)
            len_ob_l=len(self.ob_list)
            roi_size=roi_x1-roi_x0
            if len_data_l is not 0 and len_ob_l is not 0 and roi_size is not 0 and self.roi_Button.isChecked() == False:
                self.oscillation_Button.setEnabled(True)
            region_data = np.array(self.data_list[1][0][roi_y0:roi_y1, roi_x0:roi_x1])
            #print region_data
            #print np.median(region_data), type(np.median(region_data))
            self.roi_list=[roi_y0,roi_y1,roi_x0,roi_x1]
            self.vmaxSpinBox.setValue(int(1.2 *int(np.max(region_data))))

            #self.roiSignal.emit(roi_list)
            self.emit(QtCore.SIGNAL('roi'),self.roi_list)
            self.choose_img()
            self.typeCombo.setEnabled(True)
            self.imgCombo.setEnabled(True)
    def norm_roi(self):

        #self.oscillation_Button.setEnabled(False)

        if self.norm_roi_Button.isChecked() == True:
            #ax = self.figure.add_subplot(111)
            #plt.set_cmap('gray')
            self.ax.hold(False)
            if self.typeCombo.currentText() == "Data Images":
                self.img=self.ax.imshow(self.data_list[1][self.data_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

            elif self.typeCombo.currentText() == "OB Images":
                self.img=self.ax.imshow(self.ob_list[1][self.ob_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

            elif self.typeCombo.currentText() == "DC Images":
                self.img=self.ax.imshow(self.dc_list[1][self.dc_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

            self.norm_roi_create=ROI(self.ax,color="blue")
            #self.connect(self.norm_roi_create,QtCore.SIGNAL('zoom'),self.choose_img)
            self.typeCombo.setEnabled(False)
            self.imgCombo.setEnabled(False)

        else:
            norm_roi_x0,norm_roi_x1,norm_roi_y0,norm_roi_y1=self.norm_roi_create._exit()
            len_data_l=len(self.data_list)
            len_ob_l=len(self.ob_list)
            norm_roi_size=norm_roi_x1-norm_roi_x0

            norm_region_data = np.array(self.data_list[1][0][norm_roi_y0:norm_roi_y1, norm_roi_x0:norm_roi_x1])
            #print region_data
            #print np.median(region_data), type(np.median(region_data))
            self.norm_roi_list=[norm_roi_y0,norm_roi_y1,norm_roi_x0,norm_roi_x1]
            #self.vmaxSpinBox.setValue(int(1.2 *int(np.max(norm_region_data))))

            #self.roiSignal.emit(roi_list)
            self.emit(QtCore.SIGNAL('norm_roi'),self.norm_roi_list)
            self.choose_img()
            self.typeCombo.setEnabled(True)
            self.imgCombo.setEnabled(True)
    def oscillation(self):

        len_data_l=len(self.data_list)
        len_ob_l=len(self.ob_list)
        file_number=0
        oscillation_list=[[],[],[]]
        if len_data_l is not 0 and len_ob_l is not 0:
            len_data=len(self.data_list[1])
            len_ob=len(self.ob_list[1])
            while   (file_number < len_data):
                if (file_number<len_data):
                    region_data = np.array(self.data_list[1][file_number][self.roi_list[0]:self.roi_list[1], self.roi_list[2]:self.roi_list[3]])
                    region_ob = np.array(self.ob_list[1][file_number][self.roi_list[0]:self.roi_list[1], self.roi_list[2]:self.roi_list[3]])
                    av_counts_data = np.median(region_data)
                    av_counts_ob = np.median(region_ob)
                    oscillation_list[0].append(file_number)
                    oscillation_list[1].append(av_counts_data)
                    oscillation_list[2].append(av_counts_ob)
                    file_number+=1
            #print oscillation_list
            rcParams['toolbar']='None'
            ax1 = plt.figure("Oscillation")
            ax2 = ax1.add_subplot(111)
            #ax2.hold(False)
            ax2.plot(oscillation_list[0],oscillation_list[1],'r*-',label='Data oscillation')
            ax2.plot(oscillation_list[0],oscillation_list[2],'b*-',label='OB oscillation')
            ax2.legend()
            #self.canvas.draw()
            ax1.show()

            ax1.canvas.manager.window.activateWindow()
            ax1.canvas.manager.window.raise_()
            #plt.close(ax1)
            #rcParams['toolbar']='None'
        else:
            self.dialog = QMessageBox(self)
            self.dialog.setStandardButtons(QMessageBox.Ok)
            self.dialog.setIcon(QMessageBox.Warning)
            self.dialog.setText("Pleas load both data files and OB files to plot the oscillation")
            self.dialog.exec_()
"""
    def choose_type(self):

        if self.typeCombo.currentText() == "Data Images":
            self.imgCombo.clear()
            self.imgCombo.addItems(self.data_list[0])

        elif self.typeCombo.currentText() == "OB Images":
            self.imgCombo.clear()
            self.imgCombo.addItems(self.ob_list[0])
        elif self.typeCombo.currentText() == "DC Images":
            self.imgCombo.clear()
            self.imgCombo.addItems(self.dc_list[0])
        elif self.typeCombo.currentText() == "Filtered Images":
            self.imgCombo.clear()
            self.imgCombo.addItems(self.filter_list[0])

        self.choose_img()
        len_data_l=len(self.data_list)
        len_ob_l=len(self.ob_list)

        #roi_size=roi_x1-roi_x0
        if len_data_l is not 0 and len_ob_l is not 0  and self.roi_Button.isChecked() == False:
            self.oscillation_Button.setEnabled(True)
        #self.figure.draw()

    def choose_img(self):
        #print "bla"
        #self.ax = self.figure.add_subplot(111)
        #self.ax.figure.canvas.set_cmap('gray')
        try:
            #self.ax.hold(False)

            if self.typeCombo.currentText() == "Data Images":
                self.figure.setImage(self.data_list[1][self.data_list[0].index(str(self.imgCombo.currentText()))])
                #print "blub"
            elif self.typeCombo.currentText() == "OB Images":
                self.figure.setImage(self.ob_list[1][self.ob_list[0].index(str(self.imgCombo.currentText()))])

            elif self.typeCombo.currentText() == "DC Images":
                self.figure.setImage(self.dc_list[1][self.dc_list[0].index(str(self.imgCombo.currentText()))])

            elif self.typeCombo.currentText() == "Filtered Images":
                self.figure.setImage(self.filter_list[1][self.filter_list[0].index(str(self.imgCombo.currentText()))])

            #self.figure.draw()
        except:
            #self.figure.draw()
            pass
    """
    def change_limit(self):
        self.img.set_clim(vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value())
        #self.ax2.set_clim(vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value())





        # refresh canvas
        self.figure.draw()
    """
    def add_data(self,load_data_list,data_img_list,roi_list):
        self.roi_list=roi_list
        self.imgCombo.clear()
        load_data_list_temp=[]
        for i in range (0,len(load_data_list)):
            temp_ind=load_data_list[i].rfind(str(os.path.sep))
            load_data_list_temp.append(load_data_list[i][temp_ind:])
        self.data_list=[load_data_list_temp,data_img_list]
        self.imgCombo.addItems(load_data_list_temp)
        self.typeCombo.removeItem(self.typeCombo.findText("Data Images"))
        self.typeCombo.addItem("Data Images")
        self.choose_type()
        self.vminSpinBox.setValue(0.75 *data_img_list[0].min())
        self.vmaxSpinBox.setValue(1.25 *data_img_list[0].max())

    def add_ob(self,load_ob_list,ob_img_list):
        self.imgCombo.clear()
        load_ob_list_temp=[]
        for i in range (0,len(load_ob_list)):
            temp_ind=load_ob_list[i].rfind(str(os.path.sep))
            load_ob_list_temp.append(load_ob_list[i][temp_ind:])
        self.ob_list=[load_ob_list_temp,ob_img_list]
        self.imgCombo.addItems(load_ob_list_temp)
        self.typeCombo.removeItem(self.typeCombo.findText("OB Images"))
        self.typeCombo.addItem("OB Images")
        self.choose_type()
    def add_dc(self,load_dc_list,dc_img_list,dc_median):
        self.imgCombo.clear()
        load_dc_list_temp=[]
        for i in range (0,len(load_dc_list)):
            temp_ind=load_dc_list[i].rfind(str(os.path.sep))
            load_dc_list_temp.append(load_dc_list[i][temp_ind:])
        if dc_median is not None:
            load_dc_list_temp.append("Median of DC")
            dc_img_list.append(dc_median)
        self.dc_list=[load_dc_list_temp,dc_img_list]
        self.imgCombo.addItems(load_dc_list_temp)
        self.typeCombo.removeItem(self.typeCombo.findText("DC Images"))
        self.typeCombo.addItem("DC Images")
        self.choose_type()

    def add_filtered(self,test_img,img):
        self.imgCombo.clear()
        temp_ind=test_img.rfind(str(os.path.sep))
        self.load_filter_list.append(test_img[temp_ind:])
        print self.load_filter_list
        self.img_filter_list.append(img)
        self.filter_list=[self.load_filter_list,self.img_filter_list]
        self.imgCombo.addItems(self.load_filter_list)
        self.typeCombo.removeItem(self.typeCombo.findText("Filtered Images"))
        self.typeCombo.addItem("Filtered Images")
        self.choose_type()




        # create an axis
        #ax = self.figure.add_subplot(111)




        # plot data


class ROI(QtCore.QObject):
    def __init__(self,ax1,ax2=None,ax3=None,fin_col=True,color="green"):
        super(ROI, self).__init__()
        #global roi_x0
        #global roi_x1
        #global roi_y0
        #global roi_y1
        self.ax1 = ax1
        self.ax2 = ax2
        self.ax3 = ax3
        self.fin_col=fin_col
        self.rect1 = Rectangle((0,0), 1, 1, facecolor='None', edgecolor=color)
        self.rect2 = Rectangle((0,0), 1, 1, facecolor='None', edgecolor=color)
        self.rect3 = Rectangle((0,0), 1, 1, facecolor='None', edgecolor=color)
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        #self.ax1=plt.gca()
        self.color=color
        self.ax1.add_patch(self.rect1)
        if self.ax2 != None:
            self.ax2.add_patch(self.rect2)
        if self.ax3 != None:
            self.ax3.add_patch(self.rect3)
        #self.is_pressed=True
        self.ax1_t1=self.ax1.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.ax1_t2=self.ax1.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.ax1_t3=self.ax1.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.ax1_t4=self.ax1.figure.canvas.mpl_connect('axes_enter_event',self.change_cursor)
        if self.ax2 != None:
            self.ax2_t1=self.ax2.figure.canvas.mpl_connect('button_press_event', self.on_press)
            self.ax2_t2=self.ax2.figure.canvas.mpl_connect('button_release_event', self.on_release)
            self.ax2_t3=self.ax2.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
            self.ax2_t4=self.ax2.figure.canvas.mpl_connect('axes_enter_event',self.change_cursor)
        if self.ax3 != None:
            self.ax3_t1=self.ax3.figure.canvas.mpl_connect('button_press_event', self.on_press)
            self.ax3_t2=self.ax3.figure.canvas.mpl_connect('button_release_event', self.on_release)
            self.ax3_t3=self.ax3.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
            self.ax3_t4=self.ax3.figure.canvas.mpl_connect('axes_enter_event',self.change_cursor)
        self.is_pressed=False
    def change_cursor(self,event):
        if self.ax1== event.inaxes:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
    def on_press(self, event):
        print 'press'
        print event
        self.x0 = event.xdata
        self.y0 = event.ydata
        self.x1 = event.xdata
        self.y1 = event.ydata
        self.rect1.set_width(self.x1 - self.x0)
        self.rect1.set_height(self.y1 - self.y0)
        self.rect1.set_xy((self.x0, self.y0))
        self.rect1.set_linestyle('dashed')
        self.rect1.set_edgecolor(self.color)
        self.ax1.figure.canvas.draw()
        if self.ax2 != None:
            self.rect2.set_width(self.x1 - self.x0)
            self.rect2.set_height(self.y1 - self.y0)
            self.rect2.set_xy((self.x0, self.y0))
            self.rect2.set_linestyle('dashed')
            self.rect2.set_edgecolor(self.color)
            self.ax2.figure.canvas.draw()
        if self.ax3 != None:
            self.rect3.set_width(self.x1 - self.x0)
            self.rect3.set_height(self.y1 - self.y0)
            self.rect3.set_xy((self.x0, self.y0))
            self.rect3.set_linestyle('dashed')
            self.rect3.set_edgecolor(self.color)
            self.ax3.figure.canvas.draw()

        self.is_pressed=True
    def on_motion(self,event):
        #if self.on_press is True:
            #return
        if self.is_pressed == True:
            self.x1 = event.xdata
            self.y1 = event.ydata
            self.rect1.set_width(self.x1 - self.x0)
            self.rect1.set_height(self.y1 - self.y0)
            self.rect1.set_xy((self.x0, self.y0))
            self.rect1.set_linestyle('dashed')
            self.ax1.figure.canvas.draw()
            if self.ax2 != None:
                self.rect2.set_width(self.x1 - self.x0)
                self.rect2.set_height(self.y1 - self.y0)
                self.rect2.set_xy((self.x0, self.y0))
                self.rect2.set_linestyle('dashed')
                self.ax2.figure.canvas.draw()
            if self.ax3 != None:
                self.rect3.set_width(self.x1 - self.x0)
                self.rect3.set_height(self.y1 - self.y0)
                self.rect3.set_xy((self.x0, self.y0))
                self.rect3.set_linestyle('dashed')
                self.ax3.figure.canvas.draw()
    def on_release(self, event):
        #global roi_x0
        #global roi_x1
        #global roi_y0
        #global roi_y1
        print 'release'
        self.x1 = event.xdata
        self.y1 = event.ydata
        self.rect1.set_width(self.x1 - self.x0)
        self.rect1.set_height(self.y1 - self.y0)
        self.rect1.set_xy((self.x0, self.y0))
        self.rect1.set_linestyle('solid')
        if self.fin_col == False:
            self.rect1.set_edgecolor('None')

        self.ax1.figure.canvas.draw()
        if self.ax2 != None:
            self.rect2.set_width(self.x1 - self.x0)
            self.rect2.set_height(self.y1 - self.y0)
            self.rect2.set_xy((self.x0, self.y0))
            self.rect2.set_linestyle('solid')
            self.ax2.figure.canvas.draw()
        if self.ax3 != None:
            self.rect3.set_width(self.x1 - self.x0)
            self.rect3.set_height(self.y1 - self.y0)
            self.rect3.set_xy((self.x0, self.y0))
            self.rect3.set_linestyle('solid')
            self.ax3.figure.canvas.draw()
        self.is_pressed=False

        roi_x0 =int(min(self.x0,self.x1))
        roi_x1 =int(max(self.x0,self.x1))
        roi_y0 =int(min(self.y0,self.y1))
        roi_y1 =int(max(self.y0,self.y1))
        zoom_list=[roi_y0,roi_y1,roi_x0,roi_x1]
        self.emit(QtCore.SIGNAL('zoom'),zoom_list)

        #self.ax1.figure.canvas.draw()


        #print self.x0,self.x1,self.y0,self.y1
        #return [self.x0,self.x1,self.y0,self.y1]
    def _exit(self):
        self.ax1.figure.canvas.mpl_disconnect(self.ax1_t1)
        self.ax1.figure.canvas.mpl_disconnect(self.ax1_t2)
        self.ax1.figure.canvas.mpl_disconnect(self.ax1_t3)
        self.ax1.figure.canvas.mpl_disconnect(self.ax1_t4)
        if self.ax2 != None:
            self.ax2.figure.canvas.mpl_disconnect(self.ax2_t1)
            self.ax2.figure.canvas.mpl_disconnect(self.ax2_t2)
            self.ax2.figure.canvas.mpl_disconnect(self.ax2_t3)
            self.ax2.figure.canvas.mpl_disconnect(self.ax2_t4)
        if self.ax3 != None:
            self.ax3.figure.canvas.mpl_disconnect(self.ax3_t1)
            self.ax3.figure.canvas.mpl_disconnect(self.ax3_t2)
            self.ax3.figure.canvas.mpl_disconnect(self.ax3_t3)
            self.ax3.figure.canvas.mpl_disconnect(self.ax3_t4)
        roi_x0 =int(min(self.x0,self.x1))
        roi_x1 =int(max(self.x0,self.x1))
        roi_y0 =int(min(self.y0,self.y1))
        roi_y1 =int(max(self.y0,self.y1))
        return roi_x0,roi_x1,roi_y0,roi_y1

class Filter_Preview(QtGui.QWidget):
    #roiSignal = QtCore.pyqtSignal()
    def __init__(self,name):
        QtGui.QWidget.__init__(self)
        QtGui.QWidget.resize(self,1000,600)
        QtGui.QWidget.setWindowTitle(self,name)
        self.data_list=[]
        self.ob_list=[]
        self.dc_list=[]
        #self.filter_list_raw=[]
        #self.filter_list_f=[]
        self.load_filter_list=[]
        self.img_filter_list_raw=[]
        self.img_filter_list_filt=[]
        # a figure instance to plot on
        self.raw_figure = MatplotlibWidget()

        self.fil_figure = MatplotlibWidget()
        self.dif_figure = MatplotlibWidget()
        self.raw_figure.figure.set_tight_layout(True)
        self.fil_figure.figure.set_tight_layout(True)
        self.dif_figure.figure.set_tight_layout(True)
        self.raw_figure.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        self.fil_figure.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        self.dif_figure.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)

        #self.raw_figure.set_tight_layout(True)
        #self.fil_figure.set_tight_layout(True)
        #self.dif_figure.set_tight_layout(True)
        #self.raw_figure.clear()
        #self.fil_figure.clear()
        #self.dif_figure.clear()

        self.raw_hist=MatplotlibWidget()
        self.fil_hist=MatplotlibWidget()
        self.dif_hist=MatplotlibWidget()
        self.raw_hist.figure.set_tight_layout(True)
        self.fil_hist.figure.set_tight_layout(True)
        self.dif_hist.figure.set_tight_layout(True)
        self.raw_hist.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Maximum)
        self.fil_hist.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Maximum)
        self.dif_hist.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Maximum)

        #self.raw_hist.tick_params(axis='x', colors='red')
        #self.raw_hist.tick_params(axis='y', colors='red')
        self.ax1 = self.raw_figure.axes
        self.ax2 = self.fil_figure.axes
        self.ax3 = self.dif_figure.axes
        self.zoom_Button=QtGui.QPushButton("Zoom")
        self.zoom_Button.setCheckable(True)
        self.unzoom_Button=QtGui.QPushButton("Unzoom")
        self.con1=self.raw_figure.axes.figure.canvas.mpl_connect('button_press_event', self.selected)
        self.con2=self.fil_figure.axes.figure.canvas.mpl_connect('button_press_event', self.selected)
        self.con3=self.dif_figure.axes.figure.canvas.mpl_connect('button_press_event', self.selected)

        #mpldatacursor.datacursor(self.ax1,formatter="X:{x:.2f}\nY{y:.2f}\nValue{z:.2f}".format)



        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        #self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        #self.toolbar = NavigationToolbar(self.figure, self)
        #self.roi_Button=QtGui.QPushButton("ROI")
        #self.roi_Button.setToolTip("Check to create a ROI in the image. Uncheck to fix the ROI")
        #self.roi_Button.setCheckable(True)
        #self.oscillation_Button=QtGui.QPushButton("Oscillation")
        #self.oscillation_Button.setEnabled(False)
        #self.oscillation_Button.setToolTip("Plots the oscillation of the Data images and the OB images in the chosen ROI")

        #self.toolbar.addWidget(self.roi_Button)
        #self.toolbar.addWidget(self.oscillation_Button)


        self.dat_vminSpinBox=QtGui.QSpinBox()
        self.dat_vminLabel=QtGui.QLabel("Min Grayvalue (Raw/Filtered)")
        self.dat_vminSpinBox.setRange(0,64000)
        self.dat_vminSpinBox.setSingleStep(500)

        self.dat_vmaxSpinBox=QtGui.QSpinBox()
        self.dat_vmaxLabel=QtGui.QLabel("Max Grayvalue (Raw/Filtered)")
        self.dat_vmaxSpinBox.setRange(0,64000)
        self.dat_vmaxSpinBox.setValue(32000)
        self.dat_vmaxSpinBox.setSingleStep(500)

        self.diff_vminSpinBox=QtGui.QSpinBox()
        self.diff_vminLabel=QtGui.QLabel("Min Grayvalue (Difference)")
        self.diff_vminSpinBox.setRange(0,64000)
        self.diff_vminSpinBox.setSingleStep(100)

        self.diff_vmaxSpinBox=QtGui.QSpinBox()
        self.diff_vmaxLabel=QtGui.QLabel("Max Grayvalue (Difference)")
        self.diff_vmaxSpinBox.setRange(0,64000)
        self.diff_vmaxSpinBox.setValue(200)
        self.diff_vmaxSpinBox.setSingleStep(100)




        # Just some button connected to `plot` method
        #self.typeCombo = QtGui.QComboBox()
        self.pixel_Label=QtGui.QLabel()
        self.raw_Label=QtGui.QLabel()
        self.fil_Label=QtGui.QLabel()
        self.dif_Label=QtGui.QLabel()
        self.imgCombo = QtGui.QComboBox()



        self.zoom_Button.clicked.connect(self.zoom_handling)
        self.unzoom_Button.clicked.connect(self.zoom_handling)

        #self.typeCombo.currentIndexChanged.connect(self.choose_type)
        self.imgCombo.currentIndexChanged.connect(self.choose_img)
        self.dat_vminSpinBox.valueChanged.connect(self.change_limit)
        self.dat_vmaxSpinBox.valueChanged.connect(self.change_limit)
        self.diff_vminSpinBox.valueChanged.connect(self.change_limit)
        self.diff_vmaxSpinBox.valueChanged.connect(self.change_limit)


        # set the layout
        layout = QtGui.QVBoxLayout()
        v_layout1=QtGui.QVBoxLayout()
        v_layout2=QtGui.QVBoxLayout()
        v_layout3=QtGui.QVBoxLayout()
        layout0 = QtGui.QHBoxLayout()
        layout1 = QtGui.QHBoxLayout()
        layout2 = QtGui.QHBoxLayout()
        layout3 = QtGui.QHBoxLayout()

        #layout.addWidget(self.toolbar)
        #layout.addWidget(self.canvas)

        #layout2.addWidget(self.typeCombo)
        layout0.addWidget(self.zoom_Button)
        layout0.addWidget(self.unzoom_Button)
        layout0.addWidget(self.pixel_Label)
        v_layout1.addWidget(self.raw_figure)
        v_layout1.addWidget(self.raw_Label)
        v_layout1.addWidget(self.raw_hist)
        v_layout2.addWidget(self.fil_figure)
        v_layout2.addWidget(self.fil_Label)
        v_layout2.addWidget(self.fil_hist)
        v_layout3.addWidget(self.dif_figure)
        v_layout3.addWidget(self.dif_Label)
        v_layout3.addWidget(self.dif_hist)

        layout1.addLayout(v_layout1)
        layout1.addLayout(v_layout2)
        layout1.addLayout(v_layout3)


        layout2.addWidget(self.imgCombo)
        layout3.addWidget(self.dat_vminLabel)
        layout3.addWidget(self.dat_vminSpinBox)
        layout3.addWidget(self.dat_vmaxLabel)
        layout3.addWidget(self.dat_vmaxSpinBox)
        layout3.addWidget(self.diff_vminLabel)
        layout3.addWidget(self.diff_vminSpinBox)
        layout3.addWidget(self.diff_vmaxLabel)
        layout3.addWidget(self.diff_vmaxSpinBox)
        layout.addLayout(layout0)
        layout.addLayout(layout1)
        layout.addLayout(layout3)
        layout.addLayout(layout2)
        self.setLayout(layout)
    def selected(self,event):
        img_raw=self.filter_list[1][self.filter_list[0].index(str(self.imgCombo.currentText()))]
        img_filtered=self.filter_list[2][self.filter_list[0].index(str(self.imgCombo.currentText()))]
        img_diff=img_raw-img_filtered
        if self.zoom_Button.isChecked()==False:
            self.x = np.around(event.xdata)
            self.y = np.around(event.ydata)
            self.raw_z=img_raw[self.y,self.x]
            self.fil_z=img_filtered[self.y,self.x]
            self.dif_z=img_diff[self.y,self.x]
            self.pixel_Label.setText("Choosen Pixel: ("+str(self.x)+","+str(self.y)+")")
            self.raw_Label.setText("Value of choosen Pixel: ("+str(self.raw_z)+")")
            self.fil_Label.setText("Value of choosen Pixel: ("+str(self.fil_z)+")")
            self.dif_Label.setText("Value of choosen Pixel: ("+str(self.dif_z)+")")


        #self.z =
    def zoom_handling_thread(self):
        self.genericThread = GenericThread(self.zoom_handling)
        self.genericThread.start()
    def zoom_handling(self):
        sender=self.sender()
        if sender==self.zoom_Button:
            if self.zoom_Button.isChecked() == True:
                self.zoom=ROI(self.ax1,ax2=self.ax2,ax3=self.ax3,fin_col=False)
                self.connect(self.zoom,QtCore.SIGNAL('zoom'),self.zoom_show)
            else :
                a,b,c,d=self.zoom._exit()
        else:
            self.choose_img()

    def zoom_show(self,zoom_list):
        img_raw=self.filter_list[1][self.filter_list[0].index(str(self.imgCombo.currentText()))]
        img_filtered=self.filter_list[2][self.filter_list[0].index(str(self.imgCombo.currentText()))]
        img_diff=img_raw-img_filtered
        self.ax1.set_xlim([zoom_list[2],zoom_list[3]])
        self.ax1.set_ylim([zoom_list[1],zoom_list[0]])
        self.raw_figure.draw()
        self.ax2.set_xlim([zoom_list[2],zoom_list[3]])
        self.ax2.set_ylim([zoom_list[1],zoom_list[0]])
        self.fil_figure.draw()
        self.ax3.set_xlim([zoom_list[2],zoom_list[3]])
        self.ax3.set_ylim([zoom_list[1],zoom_list[0]])
        self.dif_figure.draw()
        self.hist_update(self.raw_hist,img_raw[zoom_list[0]:zoom_list[1],zoom_list[2]:zoom_list[3]])
        self.hist_update(self.fil_hist,img_filtered[zoom_list[0]:zoom_list[1],zoom_list[2]:zoom_list[3]])
        self.hist_update(self.dif_hist,img_diff[zoom_list[0]:zoom_list[1],zoom_list[2]:zoom_list[3]])

    def change_limit(self):

        self.raw.set_clim(vmin=self.dat_vminSpinBox.value(),vmax=self.dat_vmaxSpinBox.value())
        self.filt.set_clim(vmin=self.dat_vminSpinBox.value(),vmax=self.dat_vmaxSpinBox.value())
        self.diff.set_clim(vmin=self.diff_vminSpinBox.value(),vmax=self.diff_vmaxSpinBox.value())
        self.raw_figure.draw()
        self.fil_figure.draw()
        self.dif_figure.draw()



    def choose_img(self):
        try:
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()
            img_raw=self.filter_list[1][self.filter_list[0].index(str(self.imgCombo.currentText()))]
            img_filtered=self.filter_list[2][self.filter_list[0].index(str(self.imgCombo.currentText()))]
            img_diff=img_raw-img_filtered

            self.raw=self.ax1.imshow(img_raw,vmin=self.dat_vminSpinBox.value(),vmax=self.dat_vmaxSpinBox.value(),cmap=plt.cm.gray,interpolation="none")
            self.ax1.set_title("Raw Image")
            self.ax1.set_xlabel("Pixel (x)")
            self.ax1.set_ylabel("Pixel (y)")
            self.filt=self.ax2.imshow(img_filtered,vmin=self.dat_vminSpinBox.value(),vmax=self.dat_vmaxSpinBox.value(),cmap=plt.cm.gray,interpolation="none")
            self.ax2.set_title("Filtered Image")
            self.ax2.set_xlabel("Pixel (x)")
            self.ax2.set_ylabel("Pixel (y)")
            self.diff=self.ax3.imshow(img_diff,vmin=self.diff_vminSpinBox.value(),vmax=self.diff_vmaxSpinBox.value(),cmap=plt.cm.gray,interpolation="none")
            self.ax3.set_title("Difference Image")
            self.ax3.set_xlabel("Pixel (x)")
            self.ax3.set_ylabel("Pixel (y)")
            self.raw_figure.draw()
            self.fil_figure.draw()
            self.dif_figure.draw()
            self.hist_update(self.raw_hist,img_raw)
            self.hist_update(self.fil_hist,img_filtered)
            self.hist_update(self.dif_hist,img_diff)


        except:
            pass
        """
        self.rect = Rectangle((0,0), 1, 1, facecolor='None', edgecolor='green')
        self.rect.set_width(self.roi_list[3] - self.roi_list[2])
        self.rect.set_height(self.roi_list[1] - self.roi_list[0])
        self.rect.set_xy((self.roi_list[2], self.roi_list[0]))
        self.rect.set_linestyle('solid')
        ax.add_patch(self.rect)
        """

    def hist_update(self,figure,image):
        histogram = np.histogram(image, bins=500, range=(0.1,np.amax(image)))
        #print histogram
        bins = histogram[1]
        central_bins = (bins[1:] + bins[:-1]) / 2.
        figure.axes.clear()
        figure.axes.fill_between(central_bins,0, histogram[0],color="blue")
        figure.axes.set_xlabel("Grayvalue")
        figure.axes.set_ylabel("Number of Pixels")
        figure.axes.set_ylim([0,max(histogram[0])])
        figure.axes.locator_params(axis='x',nbins=3)
        figure.axes.locator_params(axis='y',nbins=5)
        figure.draw()




        # refresh canvas
        #self.canvas.draw()


    def add_filtered(self,test_img,img_list):
        #self.filter_list=[]
        self.imgCombo.clear()
        test_img=str(test_img)
        temp_ind=test_img.rfind(str(os.path.sep))
        self.load_filter_list.append(test_img[temp_ind:])
        #print self.load_filter_list
        self.img_filter_list_raw.append(img_list[0])
        self.img_filter_list_filt.append(img_list[1])
        self.filter_list=[self.load_filter_list,self.img_filter_list_raw,self.img_filter_list_filt]
        self.imgCombo.addItems(self.load_filter_list)
        #self.typeCombo.removeItem(self.typeCombo.findText("Filtered Images"))
        #self.typeCombo.addItem("Filtered Images")
        #self.choose_type()



class GenericThread(QtCore.QThread):
    def __init__(self, function, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    def run(self):
        self.function(*self.args,**self.kwargs)
