# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 10:18:04 2015

@author: tneuwirt
"""

from PyQt5 import QtCore, QtGui,QtWidgets
import os
import ntpath
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg 
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from matplotlib import rcParams
from matplotlib.patches import Rectangle
import matplotlib.lines as ml

import multiprocessing
import numpy as np
import sys
import time

rcParams['font.size'] = 9
################################################
#Not needed anymore. Used toi solve a problem in matplotlib prior to 2.0.0
################################################
"""
class FigureCanvas(FigureCanvasQTAgg):
    def paintEvent(self, e):
       
        #Copy the image from the Agg canvas to the qt.drawable.
        #In Qt, all drawing should be done inside of here when a widget is
        #shown onscreen.
        
        # if the canvas does not have a renderer, then give up and wait for
        # FigureCanvasAgg.draw(self) to be called
        paintcolor = QtCore.Qt.black if not hasattr(self, "rectanglecolor") else self.rectanglecolor
        if not hasattr(self, 'renderer'):
            return

        #if DEBUG:
            #print('FigureCanvasQtAgg.paintEvent: ', self,
                  #self.get_width_height())

        if len(self.blitbox) == 0:
            # matplotlib is in rgba byte order.  QImage wants to put the bytes
            # into argb format and is in a 4 byte unsigned int.  Little endian
            # system is LSB first and expects the bytes in reverse order
            # (bgra).
            if QtCore.QSysInfo.ByteOrder == QtCore.QSysInfo.LittleEndian:
                stringBuffer = self.renderer._renderer.tostring_bgra()
            else:
                stringBuffer = self.renderer._renderer.tostring_argb()

            refcnt = sys.getrefcount(stringBuffer)

            # convert the Agg rendered image -> qImage
            qImage = QtWidgets.QImage(stringBuffer, self.renderer.width,
                                  self.renderer.height,
                                  QtWidgets.QImage.Format_ARGB32)
            if hasattr(qImage, 'setDevicePixelRatio'):
                # Not available on Qt4 or some older Qt5.
                qImage.setDevicePixelRatio(self._dpi_ratio)
            # get the rectangle for the image
            rect = qImage.rect()
            p = QtWidgets.QPainter(self)
            # reset the image area of the canvas to be the back-ground color
            p.eraseRect(rect)
            # draw the rendered image on to the canvas
            p.drawPixmap(QtCore.QPoint(0, 0), QtWidgets.QPixmap.fromImage(qImage))

            # draw the zoom rectangle to the QPainter
            if self._drawRect is not None:
                pen = QtWidgets.QPen(QtCore.Qt.black, 1 / self._dpi_ratio,
                                 QtCore.Qt.DotLine)
                p.setPen(pen)
                x, y, w, h = self._drawRect
                p.drawRect(x, y, w, h)
            p.end()

            # This works around a bug in PySide 1.1.2 on Python 3.x,
            # where the reference count of stringBuffer is incremented
            # but never decremented by QImage.
            # TODO: revert PR #1323 once the issue is fixed in PySide.
            del qImage
            if refcnt != sys.getrefcount(stringBuffer):
                _decref(stringBuffer)
        else:
            p = QtWidgets.QPainter(self)

            while len(self.blitbox):
                bbox = self.blitbox.pop()
                l, b, r, t = bbox.extents
                w = int(r) - int(l)
                h = int(t) - int(b)
                t = int(b) + h
                reg = self.copy_from_bbox(bbox)
                stringBuffer = reg.to_string_argb()
                qImage = QtWidgets.QImage(stringBuffer, w, h,
                                      QtWidgets.QImage.Format_ARGB32)
                if hasattr(qImage, 'setDevicePixelRatio'):
                    # Not available on Qt4 or some older Qt5.
                    qImage.setDevicePixelRatio(self._dpi_ratio)
                # Adjust the stringBuffer reference count to work
                # around a memory leak bug in QImage() under PySide on
                # Python 3.x
                if QT_API == 'PySide' and six.PY3:
                    ctypes.c_long.from_address(id(stringBuffer)).value = 1

                origin = QtCore.QPoint(l, self.renderer.height - t)
                pixmap = QtWidgets.QPixmap.fromImage(qImage)
                p.drawPixmap(origin / self._dpi_ratio, pixmap)

            # draw the zoom rectangle to the QPainter
            if self._drawRect is not None:
                pen = QtWidgets.QPen(paintcolor, 1 / self._dpi_ratio,
                                 QtCore.Qt.DotLine)
                p.setPen(pen)
                x, y, w, h = self._drawRect
                p.drawRect(x, y, w, h)

            p.end()
"""

class MatplotlibWidget(FigureCanvasQTAgg):
    """
    MatplotlibWidget inherits PyQt4.QtWidgets.QWidget
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
                 width=3, height=3, dpi=100,share=None):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.drawRect = False



        if share == None:
            self.axes = self.figure.add_subplot(111)
        else:
            self.axes = self.figure.add_subplot(111,sharex=share,sharey=share)
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
        

        self.canvas=FigureCanvasQTAgg.__init__(self, self.figure)



        self.setParent(parent)

        #Canvas.setSizePolicy(self, QSizePolicy.Preferred, QSizePolicy.Preferred)
        policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        policy.setHeightForWidth(True)
        FigureCanvasQTAgg.setSizePolicy(self,policy)
        FigureCanvasQTAgg.updateGeometry(self)
    def heightForWidth(self,width):
        return width
    def widthForHeight(self,height):
        return height
    def sizeHint(self):
        w, h = self.get_width_height()
        return QtCore.QSize(w, h)

    def minimumSizeHint(self):
        return QtCore.QSize(10, 10)
class Preview(QtWidgets.QDialog):
    roiSignal = QtCore.pyqtSignal(list)
    normroiSignal = QtCore.pyqtSignal(list)
    def __init__(self,name,parent=None):
        super(Preview,self).__init__(parent)
        Preview.resize(self,700,700)
        Preview.setWindowTitle(self,name)
        self.data_list=[]
        self.ob_list=[]
        self.dc_list=[]
        self.filter_list=[]
        self.load_filter_list=[]
        self.img_filter_list=[]
        self.parent=parent
        # a figure instance to plot on
        self.figure = MatplotlibWidget()
        

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        #self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.figure, self)
        self.roi_Button=QtWidgets.QPushButton("ROI")
        self.roi_Button.setToolTip("Check to create a ROI in the image. Uncheck to fix the ROI")
        self.roi_Button.setCheckable(True)
        self.norm_roi_Button=QtWidgets.QPushButton("Norm ROI")
        self.norm_roi_Button.setToolTip("Check to create a normalization ROI in the image. Uncheck to fix the ROI")
        self.norm_roi_Button.setCheckable(True)
        self.oscillation_Button=QtWidgets.QPushButton("Oscillation")
        self.oscillation_Button.setEnabled(False)
        self.oscillation_Button.setToolTip("Plots the oscillation of the Data images and the OB images in the chosen ROI")
        self.reset_Button=QtWidgets.QPushButton("ROI Reset")
        self.reset_Button.setToolTip("Resets the ROI")
        self.norm_reset_Button=QtWidgets.QPushButton("Norm ROI Reset")
        self.norm_reset_Button.setToolTip("Resets the Norm ROI")
        


        self.vminSpinBox=QtWidgets.QSpinBox()
        self.vminLabel=QtWidgets.QLabel("Min Grayvalue")
        self.vminSpinBox.setRange(0,64000)
        self.vminSpinBox.setSingleStep(500)

        self.vmaxSpinBox=QtWidgets.QSpinBox()
        self.vmaxLabel=QtWidgets.QLabel("Max Grayvalue")
        self.vmaxSpinBox.setRange(0,64000)
        self.vmaxSpinBox.setValue(32000)
        self.vmaxSpinBox.setSingleStep(500)




        # Just some button connected to `plot` method
        self.typeCombo = QtWidgets.QComboBox()

        self.imgCombo = QtWidgets.QComboBox()



        self.roi_Button.clicked.connect(self.roi)
        self.norm_roi_Button.clicked.connect(self.norm_roi)
        self.oscillation_Button.clicked.connect(self.oscillation)
        self.reset_Button.clicked.connect(self.roi_reset)
        self.norm_reset_Button.clicked.connect(self.norm_roi_reset)


        self.typeCombo.currentIndexChanged.connect(self.choose_type)
        self.imgCombo.currentIndexChanged.connect(self.choose_img)
        self.vminSpinBox.valueChanged.connect(self.change_limit)
        self.vmaxSpinBox.valueChanged.connect(self.change_limit)
        self.ax = self.figure.axes
        # Dummy Image
        self.img=self.ax.imshow(np.zeros((200,200)),vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

        # set the layout
        layout = QtWidgets.QVBoxLayout()
        layout2 = QtWidgets.QHBoxLayout()
        layout3 = QtWidgets.QHBoxLayout()
        roi_layout=QtWidgets.QHBoxLayout()
        roi_layout.addWidget(self.roi_Button)
        roi_layout.addWidget(self.norm_roi_Button)
        roi_layout.addWidget(self.reset_Button)
        roi_layout.addWidget(self.norm_reset_Button)
        roi_layout.addWidget(self.oscillation_Button)
        layout.addWidget(self.toolbar)
        #layout.addLayout(roi_layout)
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
    def roi_reset(self):
        
        if self.typeCombo.currentText() == "Data Images":
            self.img=self.ax.imshow(self.parent.data_img_list[self.data_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

        elif self.typeCombo.currentText() == "OB Images":
            self.img=self.ax.imshow(self.parent.ob_img_list[self.ob_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

        elif self.typeCombo.currentText() == "DC Images":
            self.img=self.ax.imshow(self.parent.dc_img_list[self.dc_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)
        roi_y1,roi_x1 = self.parent.data_img_list[0].shape
        region_data = np.array(self.parent.data_img_list[0][0:roi_y1, 0:roi_x1])
        #print region_data
        #print np.median(region_data), type(np.median(region_data))
        self.roi_list=[0,roi_y1,0,roi_x1]
        #self.vmaxSpinBox.setValue(int(0.75 *int(np.max(region_data))))

        self.roiSignal.emit(roi_list)
        self.choose_img()
        #self.emit(QtCore.SIGNAL('roi'),self.roi_list)
    def norm_roi_reset(self):
        
        if self.typeCombo.currentText() == "Data Images":
            self.img=self.ax.imshow(self.parent.data_img_list[self.data_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

        elif self.typeCombo.currentText() == "OB Images":
            self.img=self.ax.imshow(self.parent.ob_img_list[self.ob_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

        elif self.typeCombo.currentText() == "DC Images":
            self.img=self.ax.imshow(self.parent.dc_img_list[self.dc_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)
        norm_roi_y1,norm_roi_x1 = self.data_list[1][0].shape
        region_data = np.array(self.data_list[1][0][0:norm_roi_y1, 0:norm_roi_x1])
        #print region_data
        #print np.median(region_data), type(np.median(region_data))
        self.norm_roi_list=[0,norm_roi_y1,0,norm_roi_x1]
        #self.vmaxSpinBox.setValue(int(1.2 *int(np.max(region_data))))

        self.normroiSignal.emit(norm_roi_list)
        self.choose_img()
        #self.emit(QtCore.SIGNAL('norm_roi'),self.norm_roi_list)
    def roi(self):

        self.oscillation_Button.setEnabled(False)

        if self.roi_Button.isChecked() == True:
            #ax = self.figure.add_subplot(111)
            #plt.set_cmap('gray')
            
            if self.typeCombo.currentText() == "Data Images":
                self.img=self.ax.imshow(self.parent.data_img_list[self.data_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

            elif self.typeCombo.currentText() == "OB Images":
                self.img=self.ax.imshow(self.parent.ob_img_list[self.ob_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

            elif self.typeCombo.currentText() == "DC Images":
                self.img=self.ax.imshow(self.parent.dc_img_list[self.dc_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

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
            region_data = np.array(self.parent.data_img_list[0][roi_y0:roi_y1, roi_x0:roi_x1])
            #print region_data
            #print np.median(region_data), type(np.median(region_data))
            self.roi_list=[roi_y0,roi_y1,roi_x0,roi_x1]
            self.vmaxSpinBox.setValue(int(0.75 *int(np.max(region_data))))

            self.roiSignal.emit(self.roi_list)
            #self.emit(QtCore.SIGNAL('roi'),self.roi_list)
            self.choose_img()
            self.typeCombo.setEnabled(True)
            self.imgCombo.setEnabled(True)
    def norm_roi(self):

        #self.oscillation_Button.setEnabled(False)

        if self.norm_roi_Button.isChecked() == True:
            #ax = self.figure.add_subplot(111)
            #plt.set_cmap('gray')
            
            if self.typeCombo.currentText() == "Data Images":
                self.img=self.ax.imshow(self.parent.data_img_list[self.data_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

            elif self.typeCombo.currentText() == "OB Images":
                self.img=self.ax.imshow(self.parent.ob_img_list[self.ob_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

            elif self.typeCombo.currentText() == "DC Images":
                self.img=self.ax.imshow(self.parent.dc_img_list[self.dc_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

            self.norm_roi_create=ROI(self.ax,color="blue")
            #self.connect(self.norm_roi_create,QtCore.SIGNAL('zoom'),self.choose_img)
            self.typeCombo.setEnabled(False)
            self.imgCombo.setEnabled(False)

        else:
            norm_roi_x0,norm_roi_x1,norm_roi_y0,norm_roi_y1=self.norm_roi_create._exit()
            len_data_l=len(self.data_list)
            len_ob_l=len(self.ob_list)
            norm_roi_size=norm_roi_x1-norm_roi_x0

            norm_region_data = np.array(self.parent.data_img_list[0][norm_roi_y0:norm_roi_y1, norm_roi_x0:norm_roi_x1])
            #print region_data
            #print np.median(region_data), type(np.median(region_data))
            self.norm_roi_list=[norm_roi_y0,norm_roi_y1,norm_roi_x0,norm_roi_x1]
            #self.vmaxSpinBox.setValue(int(1.2 *int(np.max(norm_region_data))))

            self.normroiSignal.emit(self.normroi_list)
            #self.emit(QtCore.SIGNAL('norm_roi'),self.norm_roi_list)
            self.choose_img()
            self.typeCombo.setEnabled(True)
            self.imgCombo.setEnabled(True)
    def oscillation(self):

        len_data_l=len(self.data_list)
        len_ob_l=len(self.ob_list)
        file_number=0
        oscillation_list=[[],[],[]]
        if len_data_l is not 0 and len_ob_l is not 0:
            len_data=len(self.parent.data_img_list)
            len_ob=len(self.parent.data_img_list)
            while   (file_number < len_data):
                if (file_number<len_data):
                    region_data = np.array(self.parent.data_img_list[file_number][self.roi_list[0]:self.roi_list[1], self.roi_list[2]:self.roi_list[3]])
                    region_ob = np.array(self.parent.ob_img_list[file_number][self.roi_list[0]:self.roi_list[1], self.roi_list[2]:self.roi_list[3]])
                    av_counts_data = np.median(region_data)
                    av_counts_ob = np.median(region_ob)
                    oscillation_list[0].append(file_number)
                    oscillation_list[1].append(av_counts_data)
                    oscillation_list[2].append(av_counts_ob)
                    file_number+=1
            #print oscillation_list
            rcParams['toolbar']='None'
            osc_widget=MatplotlibWidget(parent=None,title="Oscillation Preview",width=5,height=5)
            ax=osc_widget.axes
            
            
            ax.plot(oscillation_list[0],oscillation_list[1],'r*-',label='Data oscillation')
            ax.plot(oscillation_list[0],oscillation_list[2],'b*-',label='OB oscillation')
            ax.legend()
            #self.canvas
            osc_widget.draw()
            osc_widget.show()

            #osc_widget.canvas.manager.window.activateWindow()
            #osc_widget.canvas.manager.window.raise_()
            #plt.close(ax1)
            #rcParams['toolbar']='None'
        else:
            self.dialog = QMessageBox(self)
            self.dialog.setStandardButtons(QMessageBox.Ok)
            self.dialog.setIcon(QMessageBox.Warning)
            self.dialog.setText("Please load both data files and OB files to plot the oscillation")
            self.dialog.exec_()

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
        self.figure.draw()

    def choose_img(self):
        #print "bla"
        #self.ax = self.figure.add_subplot(111)
        #self.ax.figure.canvas.set_cmap('gray')
        try:
            

            if self.typeCombo.currentText() == "Data Images":
                self.img=self.ax.imshow(self.parent.data_img_list[self.data_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)
                #print "blub"
            elif self.typeCombo.currentText() == "OB Images":
                self.img=self.ax.imshow(self.parent.ob_img_list[self.ob_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

            elif self.typeCombo.currentText() == "DC Images":
                self.img=self.ax.imshow(self.parent.dc_img_list[self.dc_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)

            elif self.typeCombo.currentText() == "Filtered Images":
                self.img=self.ax.imshow(self.filter_list[1][self.filter_list[0].index(str(self.imgCombo.currentText()))],vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value(),cmap=plt.cm.gray)
            self.rect = Rectangle((0,0), 1, 1, facecolor='None', edgecolor='green')
            self.rect.set_width(self.roi_list[3] - self.roi_list[2])
            self.rect.set_height(self.roi_list[1] - self.roi_list[0])
            self.rect.set_xy((self.roi_list[2], self.roi_list[0]))
            self.rect.set_linestyle('solid')
            self.ax.add_patch(self.rect)
            self.norm_rect = Rectangle((0,0), 1, 1, facecolor='None', edgecolor='blue')
            self.norm_rect.set_width(self.norm_roi_list[3] - self.norm_roi_list[2])
            self.norm_rect.set_height(self.norm_roi_list[1] - self.norm_roi_list[0])
            self.norm_rect.set_xy((self.norm_roi_list[2], self.norm_roi_list[0]))
            self.norm_rect.set_linestyle('solid')
            self.ax.add_patch(self.norm_rect)

            self.figure.draw()
        except:
            self.figure.draw()

    def change_limit(self):
        self.img.set_clim(vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value())
        #self.ax2.set_clim(vmin=self.vminSpinBox.value(),vmax=self.vmaxSpinBox.value())





        # refresh canvas
        self.figure.draw()
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
        self.vminSpinBox.setValue(1.25 *self.parent.data_img_list[0].min())
        self.vmaxSpinBox.setValue(0.75 *self.parent.data_img_list[0].max())

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
            #dc_img_list.append(dc_median)
        self.dc_list=[load_dc_list_temp,dc_img_list]
        self.imgCombo.addItems(load_dc_list_temp)
        self.typeCombo.removeItem(self.typeCombo.findText("DC Images"))
        self.typeCombo.addItem("DC Images")
        self.choose_type()

    def add_filtered(self,test_img,img):
        self.imgCombo.clear()
        temp_ind=test_img.rfind(str(os.path.sep))
        self.load_filter_list.append(test_img[temp_ind:])
        #print self.load_filter_list
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
    zoomSignal = QtCore.pyqtSignal(list)
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
            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
    def on_press(self, event):
        #print 'press'
        #print event
        self.x0 = event.xdata
        self.y0 = event.ydata
        self.x1 = event.xdata
        self.y1 = event.ydata
        self.rect1.set_width(self.x1 - self.x0)
        self.rect1.set_height(self.y1 - self.y0)
        self.rect1.set_xy((self.x0, self.y0))
        self.rect1.set_linestyle('dashed')
        self.rect1.set_edgecolor(self.color)
        if event.inaxes == self.ax1:
            self.ax1.figure.canvas.draw()

        if self.ax2 != None:
            self.rect2.set_width(self.x1 - self.x0)
            self.rect2.set_height(self.y1 - self.y0)
            self.rect2.set_xy((self.x0, self.y0))
            self.rect2.set_linestyle('dashed')
            self.rect2.set_edgecolor(self.color)
            if event.inaxes == self.ax2:
                self.ax2.figure.canvas.draw()
        if self.ax3 != None:
            self.rect3.set_width(self.x1 - self.x0)
            self.rect3.set_height(self.y1 - self.y0)
            self.rect3.set_xy((self.x0, self.y0))
            self.rect3.set_linestyle('dashed')
            self.rect3.set_edgecolor(self.color)
            if event.inaxes == self.ax3:
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
            if event.inaxes == self.ax1:
                self.ax1.figure.canvas.draw()

            if self.ax2 != None:
                self.rect2.set_width(self.x1 - self.x0)
                self.rect2.set_height(self.y1 - self.y0)
                self.rect2.set_xy((self.x0, self.y0))
                self.rect2.set_linestyle('dashed')
                if event.inaxes == self.ax2:
                    self.ax2.figure.canvas.draw()
            if self.ax3 != None:
                self.rect3.set_width(self.x1 - self.x0)
                self.rect3.set_height(self.y1 - self.y0)
                self.rect3.set_xy((self.x0, self.y0))
                self.rect3.set_linestyle('dashed')
                if event.inaxes == self.ax3:
                    self.ax3.figure.canvas.draw()

    def on_release(self, event):
        #global roi_x0
        #global roi_x1
        #global roi_y0
        #global roi_y1
        #print 'release'
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
            if self.fin_col == False:
                self.rect2.set_edgecolor('None')
        
            self.ax2.figure.canvas.draw()
        if self.ax3 != None:
            self.rect3.set_width(self.x1 - self.x0)
            self.rect3.set_height(self.y1 - self.y0)
            self.rect3.set_xy((self.x0, self.y0))
            self.rect3.set_linestyle('solid')
            if self.fin_col == False:
                self.rect3.set_edgecolor('None')
            
            self.ax3.figure.canvas.draw()
        self.is_pressed=False

        roi_x0 =int(min(self.x0,self.x1))
        roi_x1 =int(max(self.x0,self.x1))
        roi_y0 =int(min(self.y0,self.y1))
        roi_y1 =int(max(self.y0,self.y1))
        zoom_list=[roi_y0,roi_y1,roi_x0,roi_x1]
        #self.emit(QtCore.SIGNAL('zoom'),zoom_list)
        self.zoomSignal.emit(zoom_list)
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
        
        
class LINE(QtCore.QObject):
    lineSignal = QtCore.pyqtSignal(list)
    def __init__(self,ax1,ax2=None,ax3=None,fin_col=True,color="red"):
        super(LINE, self).__init__()
        #global roi_x0
        #global roi_x1
        #global roi_y0
        #global roi_y1
        self.ax1 = ax1
        self.ax2 = ax2
        self.ax3 = ax3
        #self.rect1 = Rectangle((0,0), 1, 1, facecolor='None', edgecolor=color)
        self.line = ml.Line2D([0,0.001],[0,0.001], linewidth=1,color=color)
        self.line2 = ml.Line2D([0,0.001],[0,0.001], linewidth=1,color=color)
        self.line3 = ml.Line2D([0,0.001],[0,0.001], linewidth=1,color=color)
        self.line_curr=ml.Line2D([0,0.001],[0,0.001], linewidth=1,color=color)
        self.fin_col=fin_col
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        #self.ax1=plt.gca()
        self.color=color
        self.ax1.add_line(self.line)
        if self.ax2 != None:
            self.ax2.add_line(self.line2)
        if self.ax3 != None:
            self.ax3.add_line(self.line3)
       
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
        
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
    def on_press(self, event):
        
        self.x0 = event.xdata
        self.y0 = event.ydata
        self.x1 = event.xdata
        self.y1 = event.ydata
        self.curr_ax=event.inaxes
        #self.curr_ax.add_line(self.line_curr)
        self.line_curr.set_xdata(np.array([self.x0,self.x1]))
        self.line_curr.set_ydata(np.array([self.y0,self.y1]))
        self.curr_ax.figure.canvas.draw()
        self.is_pressed=True
    def on_motion(self,event):
        #if self.on_press is True:
            #return
        if self.is_pressed == True:
            self.x1 = event.xdata
            self.y1 = event.ydata
            x_range=np.linspace(self.x0,self.x1,1000)
            y_range=np.linspace(self.y0,self.y1,1000)
            self.line.set_xdata(x_range)
            self.line.set_ydata(y_range)
            self.line2.set_xdata(x_range)
            self.line2.set_ydata(y_range)
            self.line3.set_xdata(x_range)
            self.line3.set_ydata(y_range)
            
            self.curr_ax.figure.canvas.draw()

    def on_release(self, event):
        #global roi_x0
        #global roi_x1
        #global roi_y0
        #global roi_y1
        #print 'release'
        self.x1 = event.xdata
        self.y1 = event.ydata
        x_range=np.linspace(self.x0,self.x1,1000)
        y_range=np.linspace(self.y0,self.y1,1000)
        self.line.set_xdata(x_range)
        self.line.set_ydata(y_range)
        self.line2.set_xdata(x_range)
        self.line2.set_ydata(y_range)
        self.line3.set_xdata(x_range)
        self.line3.set_ydata(y_range)
        
        self.ax1.figure.canvas.draw()
        if self.ax2 != None:
            self.ax2.figure.canvas.draw()
        if self.ax3 != None:
            self.ax3.figure.canvas.draw()
            
        self.is_pressed=False

        
        line_list=[x_range,y_range,self.x0,self.x1,self.y0,self.y1]
        #self.emit(QtCore.SIGNAL('line'),line_list)
        self.lineSignal.emit(line_list)
        #self.ax1.figure.canvas.draw()


        #print self.x0,self.x1,self.y0,self.y1
        #return [self.x0,self.x1,self.y0,self.y1]
    def _exit(self):
        self.line_curr.set_alpha(0)
        self.line.set_alpha(0)
        self.line2.set_alpha(0)
        self.line3.set_alpha(0)
        self.ax1.figure.canvas.draw()
        self.ax2.figure.canvas.draw()
        self.ax3.figure.canvas.draw()
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
        
       
class Filter_Preview(QtWidgets.QWidget):
    #roiSignal = QtCore.pyqtSignal()
    def __init__(self,name,parent=None):
        QtWidgets.QWidget.__init__(self)
        QtWidgets.QWidget.resize(self,1300,700)
        QtWidgets.QWidget.setWindowTitle(self,name)
        
        self.data_list=[]
        self.ob_list=[]
        self.dc_list=[]
        self.zoom_list=None
        self.limitThread=None
        self.gray_value=None
        self.compare_para=ParameterWidget("Filter Parameter",parent=self)
        #self.mima=[0,0]
        #self.filter_list_raw=[]
        #self.filter_list_f=[]
        self.load_filter_list=[]
        self.img_filter_list_raw=[]
        self.img_filter_list_filt=[]
        # a figure instance to plot on
        #plt.ion()
        self.raw_figure = MatplotlibWidget()
        self.raw_figure.figure.set_tight_layout(True)
        #self.raw_figure.axes.hold(True)
        self.ax1 = self.raw_figure.axes
        self.ax1.set_adjustable('box')
        self.raw_figure.axes.figure.canvas.rectanglecolor=QtCore.Qt.green


        self.fil_figure = MatplotlibWidget(share=self.ax1)
        self.fil_figure.axes.figure.canvas.rectanglecolor=QtCore.Qt.green
        #self.fil_figure.axes.hold(True)
        self.ax2 = self.fil_figure.axes
        self.ax2.set_adjustable('box')
        self.dif_figure = MatplotlibWidget(share=self.ax1)
        self.dif_figure.axes.figure.canvas.rectanglecolor=QtCore.Qt.green
        self.ax3 = self.dif_figure.axes
        self.ax3.set_adjustable('box')

        self.fil_figure.figure.set_tight_layout(True)
        self.dif_figure.figure.set_tight_layout(True)
        self.raw_figure.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.MinimumExpanding)
        self.fil_figure.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.MinimumExpanding)
        self.dif_figure.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.MinimumExpanding)
        #self.toolbar=NavigationToolbar(self.raw_figure,self)
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
        self.raw_hist.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.Maximum)
        self.fil_hist.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.Maximum)
        self.dif_hist.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.Maximum)
        #self.raw_hist.axes.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        self.raw_hist.axes.ticklabel_format(style='sci', axis='y', scilimits=(1,1))
        #self.fil_hist.axes.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        self.fil_hist.axes.ticklabel_format(style='sci', axis='y', scilimits=(1,1))
        #self.dif_hist.axes.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        self.dif_hist.axes.ticklabel_format(style='sci', axis='y', scilimits=(1,1))

        #self.raw_hist.tick_params(axis='x', colors='red')
        #self.raw_hist.tick_params(axis='y', colors='red')



        #self.ax2.figure(sharex(self.ax1))
        self.zoom_Button=QtWidgets.QPushButton("Zoom")
        self.zoom_Button.setCheckable(True)
        self.unzoom_Button=QtWidgets.QPushButton("Unzoom")
        self.para_Button=QtWidgets.QPushButton("Show Filter Values")
        self.con1=self.raw_figure.axes.figure.canvas.mpl_connect('button_press_event', self.selected)
        self.con2=self.fil_figure.axes.figure.canvas.mpl_connect('button_press_event', self.selected)
        self.con3=self.dif_figure.axes.figure.canvas.mpl_connect('button_press_event', self.selected)


        #self.draw2 = self.fil_figure.axes.figure.canvas.mpl_connect('draw_event', self.ondraw)
        #self.draw3 = self.dif_figure.axes.figure.canvas.mpl_connect('draw_event', self.ondraw)

        #mpldatacursor.datacursor(self.ax1,formatter="X:{x:.2f}\nY{y:.2f}\nValue{z:.2f}".format)



        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        #self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar1 = NavigationToolbar(self.raw_figure,None)
        self.toolbar2 = NavigationToolbar(self.fil_figure,None)
        self.toolbar3 = NavigationToolbar(self.dif_figure,None)
        #self.roi_Button=QtWidgets.QPushButton("ROI")
        #self.roi_Button.setToolTip("Check to create a ROI in the image. Uncheck to fix the ROI")
        #self.roi_Button.setCheckable(True)
        #self.oscillation_Button=QtWidgets.QPushButton("Oscillation")
        #self.oscillation_Button.setEnabled(False)
        #self.oscillation_Button.setToolTip("Plots the oscillation of the Data images and the OB images in the chosen ROI")

        #self.toolbar.addWidget(self.roi_Button)
        #self.toolbar.addWidget(self.oscillation_Button)


        self.dat_vminSpinBox=QtWidgets.QSpinBox()
        self.dat_vminLabel=QtWidgets.QLabel("Min Grayvalue (Raw/Filtered)")
        self.dat_vminSpinBox.setRange(0,64000)
        self.dat_vminSpinBox.setSingleStep(500)
        self.dat_vminSpinBox.setEnabled(False)

        self.dat_vmaxSpinBox=QtWidgets.QSpinBox()
        self.dat_vmaxLabel=QtWidgets.QLabel("Max Grayvalue (Raw/Filtered)")
        self.dat_vmaxSpinBox.setRange(0,64000)
        self.dat_vmaxSpinBox.setValue(32000)
        self.dat_vmaxSpinBox.setSingleStep(500)
        self.dat_vmaxSpinBox.setEnabled(False)

        self.diff_vminSpinBox=QtWidgets.QSpinBox()
        self.diff_vminLabel=QtWidgets.QLabel("Min Grayvalue (Difference)")
        self.diff_vminSpinBox.setRange(0,64000)
        self.diff_vminSpinBox.setSingleStep(100)
        self.diff_vminSpinBox.setEnabled(False)

        self.diff_vmaxSpinBox=QtWidgets.QSpinBox()
        self.diff_vmaxLabel=QtWidgets.QLabel("Max Grayvalue (Difference)")
        self.diff_vmaxSpinBox.setRange(0,64000)
        self.diff_vmaxSpinBox.setValue(200)
        self.diff_vmaxSpinBox.setSingleStep(100)
        self.diff_vmaxSpinBox.setEnabled(False)




        # Just some button connected to `plot` method
        #self.typeCombo = QtWidgets.QComboBox()
        self.pixel_Label=QtWidgets.QLabel()
        self.raw_Label=QtWidgets.QLabel()
        self.fil_Label=QtWidgets.QLabel()
        self.dif_Label=QtWidgets.QLabel()
        self.imgCombo = QtWidgets.QComboBox()



        self.zoom_Button.clicked.connect(self.zoom_handling)
        self.unzoom_Button.clicked.connect(self.unzoom_handling)
        self.para_Button.clicked.connect(self.para_handling)

        #self.typeCombo.currentIndexChanged.connect(self.choose_type)
        self.imgCombo.currentIndexChanged.connect(self.choose_img)
        #self.dat_vminSpinBox.valueChanged.connect(self.change_limit)
        #self.dat_vmaxSpinBox.valueChanged.connect(self.change_limit)
        #self.diff_vminSpinBox.valueChanged.connect(self.change_limit)
        #self.diff_vmaxSpinBox.valueChanged.connect(self.change_limit)


        # set the layout
        layout = QtWidgets.QVBoxLayout()
        v_layout1=QtWidgets.QVBoxLayout()
        v_layout2=QtWidgets.QVBoxLayout()
        v_layout3=QtWidgets.QVBoxLayout()
        layout0 = QtWidgets.QHBoxLayout()
        layout1 = QtWidgets.QHBoxLayout()
        layout2 = QtWidgets.QHBoxLayout()
        layout3 = QtWidgets.QHBoxLayout()

        #layout0.addWidget(self.toolbar)
        #layout.addWidget(self.canvas)

        #layout2.addWidget(self.typeCombo)
        layout0.addWidget(self.zoom_Button)
        layout0.addWidget(self.unzoom_Button)
        layout0.addWidget(self.para_Button)
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

        if self.zoom_Button.isChecked()==False:
            self.x = int(np.around(event.xdata))
            self.y = int(np.around(event.ydata))
            self.raw_z=self.img_raw[self.y,self.x]
            self.fil_z=self.img_filtered[self.y,self.x]
            self.dif_z=self.img_diff[self.y,self.x]
            self.pixel_Label.setText("Choosen Pixel: ("+str(self.x)+","+str(self.y)+")")
            self.raw_Label.setText("Value of choosen Pixel: ("+str(self.raw_z)+")")
            self.fil_Label.setText("Value of choosen Pixel: ("+str(self.fil_z)+")")
            self.dif_Label.setText("Value of choosen Pixel: ("+str(self.dif_z)+")")


        #self.z =
    #def para_handling()
    def zoom_thread(self):
        self.zoomThread = GenericThread(self.zoom_handling)
        self.zoomThread.start()

    def zoom_handling(self):
        self.draw1 = self.raw_figure.axes.figure.canvas.mpl_connect('draw_event', self.ondraw)
        self.toolbar1.zoom()
        self.toolbar2.zoom()
        self.toolbar3.zoom()

    def unzoom_handling(self):
        self.img_raw=self.filter_list[1][self.filter_list[0].index(str(self.imgCombo.currentText()))]
        h,w=self.img_raw.shape
        self.ax1.set_xlim([0,w])
        self.ax1.set_ylim([h,0])
        self.raw_figure.draw()
        self.ax2.set_xlim([0,w])
        self.ax2.set_ylim([h,0])
        self.fil_figure.draw()
        self.ax3.set_xlim([0,w])
        self.ax3.set_ylim([h,0])
        self.dif_figure.draw()
        self.ax1.figure.canvas.mpl_disconnect(self.draw1)
        if self.zoom_Button.isChecked():
            self.toolbar1.zoom()
            self.toolbar2.zoom()
            self.toolbar3.zoom()

            self.zoom_Button.setChecked(False)

    def ondraw(self,event):
        #ax=event.canvas
        

        x0,x1=self.ax2.get_xlim()
        
        y0,y1=self.ax2.get_ylim()
        
        self.zoom_list=[y1,y0,x0,x1]


        self.hist_update(self.raw_hist,self.img_raw[int(y1):int(y0),int(x0):int(x1)])
        self.hist_update(self.fil_hist,self.img_filtered[int(y1):int(y0),int(x0):int(x1)])
        self.hist_update(self.dif_hist,self.img_diff[int(y1):int(y0),int(x0):int(x1)])




    """
    def zoom_show(self,zoom_list):
        img_raw=self.filter_list[1][self.filter_list[0].index(str(self.imgCombo.currentText()))]
        img_filtered=self.filter_list[2][self.filter_list[0].index(str(self.imgCombo.currentText()))]
        img_diff=img_raw-img_filtered
        self.zoom_list=zoom_list
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
    """
    def figures_thread(self):
            self.limitThread = GenericThread(self.draw_figures)
            self.limitThread.start()


    def change_limit(self,hist):
        if hist[2]==self.raw_hist.axes:
            self.dat_vminSpinBox.setValue(hist[0])
            self.dat_vmaxSpinBox.setValue(hist[1])
        if hist[2]==self.dif_hist.axes:
            self.diff_vminSpinBox.setValue(hist[0])
            self.diff_vmaxSpinBox.setValue(hist[1])

        self.hist_update(self.raw_hist,self.img_raw)
        self.hist_update(self.fil_hist,self.img_filtered)
        self.hist_update(self.dif_hist,self.img_diff)

    def draw_figures(self):
        while True:
            v_min,v_max=self.raw.get_clim()
            v_min_2,v_max_2=self.diff.get_clim()

            if v_min != self.dat_vminSpinBox.value() or v_max != self.dat_vmaxSpinBox.value():
                self.raw.set_clim(vmin=self.dat_vminSpinBox.value(),vmax=self.dat_vmaxSpinBox.value())
                self.filt.set_clim(vmin=self.dat_vminSpinBox.value(),vmax=self.dat_vmaxSpinBox.value())
                self.raw_figure.draw()
                self.fil_figure.draw()
            if v_min_2 != self.diff_vminSpinBox.value() or v_max_2!= self.diff_vmaxSpinBox.value():
                
                self.diff.set_clim(vmin=self.diff_vminSpinBox.value(),vmax=self.diff_vmaxSpinBox.value())
                self.dif_figure.draw()
                
            time.sleep(0.1)






    def choose_img(self):
        
        try:
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()
            index=self.filter_list[0].index(str(self.imgCombo.currentText()))
            self.img_raw=self.filter_list[1][index]
            self.img_filtered=self.filter_list[2][index]
            self.img_diff=self.img_raw-self.img_filtered
           
            h,w=self.img_raw.shape
            if self.gray_value == None:
                self.dat_vminSpinBox.setValue(0)
                self.dat_vmaxSpinBox.setValue(1.1*np.median(self.img_filtered))
                self.gray_value=[self.dat_vminSpinBox.value(),self.dat_vmaxSpinBox.value()]
            
            

            self.raw=self.ax1.imshow(self.img_raw,vmin=self.dat_vminSpinBox.value(),vmax=self.dat_vmaxSpinBox.value(),cmap=plt.cm.gray,interpolation="none")
            self.ax1.set_title("Raw Image")
            self.ax1.set_xlabel("Pixel (x)")
            self.ax1.set_ylabel("Pixel (y)")
            self.ax1.locator_params(axis="x",nbins=4)
            self.ax1.locator_params(axis="y",nbins=4)
            #self.ax1.set_xlim([0,w])
            #self.ax1.set_ylim([h,0])
            self.filt=self.ax2.imshow(self.img_filtered,vmin=self.dat_vminSpinBox.value(),vmax=self.dat_vmaxSpinBox.value(),cmap=plt.cm.gray,interpolation="none")
            self.ax2.set_title("Filtered Image")
            self.ax2.set_xlabel("Pixel (x)")
            self.ax2.set_ylabel("Pixel (y)")
            self.ax2.locator_params(axis="x",nbins=4)
            self.ax2.locator_params(axis="y",nbins=4)
            self.diff=self.ax3.imshow(self.img_diff,vmin=self.diff_vminSpinBox.value(),vmax=self.diff_vmaxSpinBox.value(),cmap=plt.cm.gray,interpolation="none")
            self.ax3.set_title("Difference Image")
            self.ax3.set_xlabel("Pixel (x)")
            self.ax3.set_ylabel("Pixel (y)")
            self.ax3.locator_params(axis="x",nbins=4)
            self.ax3.locator_params(axis="y",nbins=4)
            #self.zoom_show([1,h-1,1,w-1])
            if self.zoom_list != None:
                self.ax1.set_xlim([self.zoom_list[2],self.zoom_list[3]])
                self.ax1.set_ylim([self.zoom_list[1],self.zoom_list[0]])
                self.ax2.set_xlim([self.zoom_list[2],self.zoom_list[3]])
                self.ax2.set_ylim([self.zoom_list[1],self.zoom_list[0]])
                self.ax3.set_xlim([self.zoom_list[2],self.zoom_list[3]])
                self.ax3.set_ylim([self.zoom_list[1],self.zoom_list[0]])
            self.raw_figure.draw()
            self.fil_figure.draw()
            self.dif_figure.draw()
            self.figures_thread()
            
            self.hist_update(self.raw_hist,self.img_raw)
            self.hist_update(self.fil_hist,self.img_filtered)
            self.hist_update(self.dif_hist,self.img_diff)
            
            self.compare_para.set_para(self.load_filter_list,self.para_list,index)


        except Exception as e :
            print(e)
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
        histogram = np.histogram(image, bins=500, range=(0.1,np.amax(image)+1))
        
        bins = histogram[1]
        central_bins = (bins[1:] + bins[:-1]) / 2.
        figure.axes.clear()
        figure.axes.fill_between(central_bins,0, histogram[0],color="blue")
        figure.axes.set_xlabel("Grayvalue")
        figure.axes.set_ylabel("Pixels")
        figure.axes.set_ylim([0,max(histogram[0])+1])
        figure.axes.locator_params(axis="x",nbins=3)
        figure.axes.locator_params(axis="y",nbins=4)
        #figure.axes.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        figure.axes.ticklabel_format(style='sci', axis='y', scilimits=(1,1))
        if figure==self.raw_hist or figure==self.fil_hist:
            figure.axes.axvline(self.dat_vminSpinBox.value(), color='r')
            figure.axes.axvline(self.dat_vmaxSpinBox.value(), color='r')
        else:
            figure.axes.axvline(self.diff_vminSpinBox.value(), color='r')
            figure.axes.axvline(self.diff_vmaxSpinBox.value(), color='r')
        figure.draw()
        self.data_gray=Gray_ROI(self.raw_hist.axes,ax2=self.fil_hist.axes)
        self.data_gray.hist_update.connect(self.change_limit)
        self.dif_gray=Gray_ROI(self.dif_hist.axes)
        self.dif_gray.hist_update.connect(self.change_limit)


    def add_filtered(self,test_img,raw_list,img_list,para_list):
        #self.filter_list=[]
        self.imgCombo.clear()
        #test_img=str(test_img)
        #temp_ind=test_img.rfind(str(os.path.sep))
        self.load_filter_list=test_img
        
        self.img_filter_list_raw=raw_list
        self.img_filter_list_filt=img_list
        self.para_list=para_list
        self.filter_list=[self.load_filter_list,self.img_filter_list_raw,self.img_filter_list_filt,self.para_list]
        self.imgCombo.addItems(self.load_filter_list)
        
        self.imgCombo.setCurrentIndex(self.imgCombo.count() - 1)
        
        
        #self.typeCombo.removeItem(self.typeCombo.findText("Filtered Images"))
        #self.typeCombo.addItem("Filtered Images")
        #self.choose_type()+
    
    def clear(self):
        self.load_filter_list=[]
        self.img_filter_list_raw=[]
        self.img_filter_list_filt=[]
        self.filter=[]
        self.imgCombo.clear()
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
    def para_handling(self):
        self.compare_para.show()
        
class ParameterWidget(QtWidgets.QDialog):
    
    def __init__(self,name,parent=None):
        super(ParameterWidget,self).__init__(parent)
        ParameterWidget.resize(self,300,450)
        ParameterWidget.setWindowTitle(self,name)
        
        self.ref_name_Label=QtWidgets.QLabel("Current Image:")
        self.ref_name_LineEdit=QtWidgets.QLineEdit()
        self.ref_name_LineEdit.setEnabled(False)
        
        self.ref_3x3_Threshold_Label=QtWidgets.QLabel("Threshold 3x3:")
        self.ref_3x3_Threshold_LineEdit=QtWidgets.QLineEdit()
        self.ref_3x3_Threshold_LineEdit.setEnabled(False)
        
        self.ref_5x5_Threshold_Label=QtWidgets.QLabel("Threshold 5x5:")
        self.ref_5x5_Threshold_LineEdit=QtWidgets.QLineEdit()
        self.ref_5x5_Threshold_LineEdit.setEnabled(False)
        
        self.ref_7x7_Threshold_Label=QtWidgets.QLabel("Threshold 7x7:")
        self.ref_7x7_Threshold_LineEdit=QtWidgets.QLineEdit()
        self.ref_7x7_Threshold_LineEdit.setEnabled(False)
        
        self.ref_log_Threshold_Label=QtWidgets.QLabel("Sigma for LoG:")
        self.ref_log_Threshold_LineEdit=QtWidgets.QLineEdit()
        self.ref_log_Threshold_LineEdit.setEnabled(False)
        
        self.ref_3x3_Pixel_Label=QtWidgets.QLabel("Pixels filtered by 3x3:")
        self.ref_3x3_Pixel_LineEdit=QtWidgets.QLineEdit()
        self.ref_3x3_Pixel_LineEdit.setEnabled(False)
        
        self.ref_5x5_Pixel_Label=QtWidgets.QLabel("Pixels filtered by 5x5:")
        self.ref_5x5_Pixel_LineEdit=QtWidgets.QLineEdit()
        self.ref_5x5_Pixel_LineEdit.setEnabled(False)
        
        self.ref_7x7_Pixel_Label=QtWidgets.QLabel("Pixels filtered by 7x7:")
        self.ref_7x7_Pixel_LineEdit=QtWidgets.QLineEdit()
        self.ref_7x7_Pixel_LineEdit.setEnabled(False)
        
        self.ref_filter_time_Label=QtWidgets.QLabel("Filter Time:")
        self.ref_filter_time_LineEdit=QtWidgets.QLineEdit()
        self.ref_filter_time_LineEdit.setEnabled(False)
        
        self.ref_processing_time_Label=QtWidgets.QLabel("Stack processing time:")
        self.ref_processing_time_LineEdit=QtWidgets.QLineEdit()
        self.ref_processing_time_LineEdit.setEnabled(False)
        #self.ref_filter_time_LineEdit.setSuffix("s")

        self.roi_size_Label=QtWidgets.QLabel("Chosen ROI ([x0,x1,y0,y1]):")
        self.roi_size_LineEdit=QtWidgets.QLineEdit()
        self.roi_size_LineEdit.setEnabled(False)

        self.bin_Label=QtWidgets.QLabel("Binning of image:")
        self.bin_LineEdit=QtWidgets.QLineEdit()
        self.bin_LineEdit.setEnabled(False)

        self.bin_size_Label=QtWidgets.QLabel("Image size after binning (x,y):")
        self.bin_size_LineEdit=QtWidgets.QLineEdit()
        self.bin_size_LineEdit.setEnabled(False)

        self.median_Label=QtWidgets.QLabel("Blurring of image:")
        self.median_LineEdit=QtWidgets.QLineEdit()
        self.median_LineEdit.setEnabled(False)
        
        self.comp_name_Label=QtWidgets.QLabel("Comparison Image:")
        self.comp_name_ComboBox=QtWidgets.QComboBox()
        
        self.comp_3x3_Threshold_Label=QtWidgets.QLabel("Threshold 3x3:")
        self.comp_3x3_Threshold_LineEdit=QtWidgets.QLineEdit()
        self.comp_3x3_Threshold_LineEdit.setEnabled(False)
        
        self.comp_5x5_Threshold_Label=QtWidgets.QLabel("Threshold 5x5:")
        self.comp_5x5_Threshold_LineEdit=QtWidgets.QLineEdit()
        self.comp_5x5_Threshold_LineEdit.setEnabled(False)
        
        self.comp_7x7_Threshold_Label=QtWidgets.QLabel("Threshold 7x7:")
        self.comp_7x7_Threshold_LineEdit=QtWidgets.QLineEdit()
        self.comp_7x7_Threshold_LineEdit.setEnabled(False)
        
        self.comp_log_Threshold_Label=QtWidgets.QLabel("Sigma for LoG:")
        self.comp_log_Threshold_LineEdit=QtWidgets.QLineEdit()
        self.comp_log_Threshold_LineEdit.setEnabled(False)
        
        self.comp_3x3_Pixel_Label=QtWidgets.QLabel("Pixels filtered by 3x3:")
        self.comp_3x3_Pixel_LineEdit=QtWidgets.QLineEdit()
        self.comp_3x3_Pixel_LineEdit.setEnabled(False)
        
        self.comp_5x5_Pixel_Label=QtWidgets.QLabel("Pixels filtered by 5x5:")
        self.comp_5x5_Pixel_LineEdit=QtWidgets.QLineEdit()
        self.comp_5x5_Pixel_LineEdit.setEnabled(False)
        
        self.comp_7x7_Pixel_Label=QtWidgets.QLabel("Pixels filtered by 7x7:")
        self.comp_7x7_Pixel_LineEdit=QtWidgets.QLineEdit()
        self.comp_7x7_Pixel_LineEdit.setEnabled(False)
        
        self.comp_filter_time_Label=QtWidgets.QLabel("Filter Time:")
        self.comp_filter_time_LineEdit=QtWidgets.QLineEdit()
        self.comp_filter_time_LineEdit.setEnabled(False)
        #self.comp_filter_time_LineEdit.setSuffix("s")
        
        
        self.main_layout=QtWidgets.QHBoxLayout()
        self.grid_layout1=QtWidgets.QGridLayout()
        self.grid_layout2=QtWidgets.QGridLayout()
        self.vline1=QtWidgets.QFrame()
        self.vline1.setFrameStyle(QtWidgets.QFrame.VLine)
        self.vline1.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Expanding)
        
        self.grid_layout1.addWidget(self.ref_name_Label,1,1)
        self.grid_layout1.addWidget(self.ref_name_LineEdit,1,2)

        self.grid_layout1.addWidget(self.roi_size_Label,2,1)
        self.grid_layout1.addWidget(self.roi_size_LineEdit,2,2)
        
        self.grid_layout1.addWidget(self.ref_3x3_Threshold_Label,3,1)
        self.grid_layout1.addWidget(self.ref_3x3_Threshold_LineEdit,3,2)
        
        self.grid_layout1.addWidget(self.ref_5x5_Threshold_Label,4,1)
        self.grid_layout1.addWidget(self.ref_5x5_Threshold_LineEdit,4,2)
        
        self.grid_layout1.addWidget(self.ref_7x7_Threshold_Label,5,1)
        self.grid_layout1.addWidget(self.ref_7x7_Threshold_LineEdit,5,2)
        
        self.grid_layout1.addWidget(self.ref_log_Threshold_Label,6,1)
        self.grid_layout1.addWidget(self.ref_log_Threshold_LineEdit,6,2)
        
        self.grid_layout1.addWidget(self.ref_3x3_Pixel_Label,7,1)
        self.grid_layout1.addWidget(self.ref_3x3_Pixel_LineEdit,7,2)
        
        self.grid_layout1.addWidget(self.ref_5x5_Pixel_Label,8,1)
        self.grid_layout1.addWidget(self.ref_5x5_Pixel_LineEdit,8,2)
        
        self.grid_layout1.addWidget(self.ref_7x7_Pixel_Label,9,1)
        self.grid_layout1.addWidget(self.ref_7x7_Pixel_LineEdit,9,2)

        self.grid_layout1.addWidget(self.bin_Label,10,1)
        self.grid_layout1.addWidget(self.bin_LineEdit,10,2)

        self.grid_layout1.addWidget(self.bin_size_Label,11,1)
        self.grid_layout1.addWidget(self.bin_size_LineEdit,11,2)

        #self.grid_layout1.addWidget(self.median_Label,12,1)
        #self.grid_layout1.addWidget(self.median_LineEdit,12,2)
        
        self.grid_layout1.addWidget(self.ref_filter_time_Label,12,1)
        self.grid_layout1.addWidget(self.ref_filter_time_LineEdit,12,2)
        
        self.grid_layout1.addWidget(self.ref_processing_time_Label,13,1)
        self.grid_layout1.addWidget(self.ref_processing_time_LineEdit,13,2)
        
        
        self.grid_layout2.addWidget(self.comp_name_Label,1,1)
        self.grid_layout2.addWidget(self.comp_name_ComboBox,1,2)
        
        self.grid_layout2.addWidget(self.comp_3x3_Threshold_Label,2,1)
        self.grid_layout2.addWidget(self.comp_3x3_Threshold_LineEdit,2,2)
        
        self.grid_layout2.addWidget(self.comp_5x5_Threshold_Label,3,1)
        self.grid_layout2.addWidget(self.comp_5x5_Threshold_LineEdit,3,2)
        
        self.grid_layout2.addWidget(self.comp_7x7_Threshold_Label,4,1)
        self.grid_layout2.addWidget(self.comp_7x7_Threshold_LineEdit,4,2)
        
        self.grid_layout2.addWidget(self.comp_log_Threshold_Label,5,1)
        self.grid_layout2.addWidget(self.comp_log_Threshold_LineEdit,5,2)
        
        self.grid_layout2.addWidget(self.comp_3x3_Pixel_Label,6,1)
        self.grid_layout2.addWidget(self.comp_3x3_Pixel_LineEdit,6,2)
        
        self.grid_layout2.addWidget(self.comp_5x5_Pixel_Label,7,1)
        self.grid_layout2.addWidget(self.comp_5x5_Pixel_LineEdit,7,2)
        
        self.grid_layout2.addWidget(self.comp_7x7_Pixel_Label,8,1)
        self.grid_layout2.addWidget(self.comp_7x7_Pixel_LineEdit,8,2)
        
        self.grid_layout2.addWidget(self.comp_filter_time_Label,9,1)
        self.grid_layout2.addWidget(self.comp_filter_time_LineEdit,9,2)
        
        self.grid_layout2.addWidget(self.comp_name_Label,10,1)
        self.grid_layout2.addWidget(self.comp_name_ComboBox,10,2)
        
        
        self.main_layout.addLayout(self.grid_layout1)
        #self.main_layout.addWidget(self.vline1)
        #self.main_layout.addLayout(self.grid_layout2)
        self.setLayout(self.main_layout)
        
    def set_para(self,image_name_list,para_list,index):
        self.data_list=image_name_list
        self.para_list=para_list
        ref_img_name = path_leaf(str(self.data_list[index]))
        temp_ind=ref_img_name.find(".")
        test_time=(self.para_list[index][8]*self.para_list[index][9])/multiprocessing.cpu_count()
        test_text="%2i h %2i min %2.1f sec"  % (test_time/3600, (test_time%3600)/60, test_time % 60)
        
        self.ref_name_LineEdit.setText(str(ref_img_name[0:temp_ind]))
        self.ref_3x3_Threshold_LineEdit.setText(str(self.para_list[index][4]))
        self.ref_5x5_Threshold_LineEdit.setText(str(self.para_list[index][5]))
        self.ref_7x7_Threshold_LineEdit.setText(str(self.para_list[index][6]))
        self.ref_log_Threshold_LineEdit.setText(str(self.para_list[index][7]))
        
        self.ref_3x3_Pixel_LineEdit.setText(str(self.para_list[index][0])+" ("+str(np.around(float(100*self.para_list[index][0])/(self.para_list[index][11]*self.para_list[index][12]),3))+"%)")
        self.ref_5x5_Pixel_LineEdit.setText(str(self.para_list[index][1])+" ("+str(np.around(float(100*self.para_list[index][1])/(self.para_list[index][11]*self.para_list[index][12]),3))+"%)")
        self.ref_7x7_Pixel_LineEdit.setText(str(self.para_list[index][2])+" ("+str(np.around(float(100*self.para_list[index][2])/(self.para_list[index][11]*self.para_list[index][12]),3))+"%)")
        self.ref_filter_time_LineEdit.setText(str(np.around(self.para_list[index][3],2))+"s")
        self.ref_processing_time_LineEdit.setText(str(test_text))
        temp_roi = [self.para_list[index][13][2],self.para_list[index][13][3],self.para_list[index][13][0],self.para_list[index][13][1]]
        self.roi_size_LineEdit.setText(str(temp_roi))
        self.bin_LineEdit.setText("("+str(self.para_list[index][10])+"x"+str(self.para_list[index][10])+")")
        #self.median_LineEdit.setText("("+str(self.para_list[index][12])+"x"+str(self.para_list[index][12])+")")
        
        self.bin_size_LineEdit.setText("("+str(self.para_list[index][12])+"x"+str(self.para_list[index][11])+")")
class Gray_ROI(QtCore.QObject):
    hist_update=QtCore.pyqtSignal(list)
    def __init__(self,ax1,ax2=None,ax3=None,fin_col=True,color="red"):
        super(Gray_ROI, self).__init__()
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
            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        if self.ax2== event.inaxes:
            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
    def on_press(self, event):
       
        self.x0 = event.xdata

        self.x1 = event.xdata

        self.rect1.set_width(self.x1 - self.x0)
        y0,y1 = self.ax1.get_ylim()
        self.rect1.set_height(y1 - y0)
        self.rect1.set_xy((self.x0, y0))
        self.rect1.set_linestyle('dashed')
        self.rect1.set_edgecolor(self.color)
        if event.inaxes == self.ax1:
            self.ax1.figure.canvas.draw()

        if self.ax2 != None:
            y0,y1 = self.ax2.get_ylim()
            self.rect2.set_width(self.x1 - self.x0)
            self.rect2.set_height(y1 - y0)
            self.rect2.set_xy((self.x0, y0))
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
            if event.inaxes == self.ax1 or event.inaxes == self.ax2:
                self.x1 = event.xdata
                self.y1 = event.ydata
            
            y0,y1 = self.ax1.get_ylim()
            self.rect1.set_width(self.x1 - self.x0)
            self.rect1.set_height(y1 - y0)
            self.rect1.set_xy((self.x0, y0))
            self.rect1.set_linestyle('dashed')

            self.ax1.figure.canvas.draw()


            if self.ax2 != None:
                
                y0,y1 = self.ax2.get_ylim()
                self.rect2.set_width(self.x1 - self.x0)
                self.rect2.set_height(y1 - y0)
                self.rect2.set_xy((self.x0, y0))
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
      
        if event.inaxes == self.ax1 or event.inaxes == self.ax2:
            self.x1 = event.xdata
        #self.y1 = event.ydata
        y0,y1 = self.ax1.get_ylim()
        self.rect1.set_width(self.x1 - self.x0)
        self.rect1.set_height(y1 - y0)
        self.rect1.set_xy((self.x0, y0))
        self.rect1.set_linestyle('solid')
        if self.fin_col == False:
            self.rect1.set_edgecolor('None')


        self.ax1.figure.canvas.draw()
        if self.ax2 != None:
            y0,y1 = self.ax2.get_ylim()
            self.rect2.set_width(self.x1 - self.x0)
            self.rect2.set_height(y1 - y0)
            self.rect2.set_xy((self.x0, y0))
            self.rect2.set_linestyle('solid')
            if self.fin_col == False:
                self.rect2.set_edgecolor('None')

            self.ax2.figure.canvas.draw()
        if self.ax3 != None:
            self.rect3.set_width(self.x1 - self.x0)
            self.rect3.set_height(self.y1 - self.y0)
            self.rect3.set_xy((self.x0, self.y0))
            self.rect3.set_linestyle('solid')
            if self.fin_col == False:
                self.rect3.set_edgecolor('None')

            self.ax3.figure.canvas.draw()
        self.is_pressed=False

        roi_x0 =int(min(self.x0,self.x1))
        roi_x1 =int(max(self.x0,self.x1))
        #roi_y0 =int(min(self.y0,self.y1))
        #roi_y1 =int(max(self.y0,self.y1))
        hist_list=[roi_x0,roi_x1,self.ax1]
        
        self.hist_update.emit(hist_list)

        #self.ax1.figure.canvas.draw()


      
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

class Gray_ROI_old(QtCore.QObject):
    histSignal = QtCore.pyqtSignal(list)
    def __init__(self,ax1,ax2=None,ax3=None,fin_col=True,color="red"):
        super(Gray_ROI, self).__init__()
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
            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        if self.ax2== event.inaxes:
            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
    def on_press(self, event):
        #print 'press'
        #print event
        self.x0 = event.xdata

        self.x1 = event.xdata

        self.rect1.set_width(self.x1 - self.x0)
        y0,y1 = self.ax1.get_ylim()
        self.rect1.set_height(y1 - y0)
        self.rect1.set_xy((self.x0, y0))
        self.rect1.set_linestyle('dashed')
        self.rect1.set_edgecolor(self.color)
        if event.inaxes == self.ax1:
            self.ax1.figure.canvas.draw()

        if self.ax2 != None:
            y0,y1 = self.ax2.get_ylim()
            self.rect2.set_width(self.x1 - self.x0)
            self.rect2.set_height(y1 - y0)
            self.rect2.set_xy((self.x0, y0))
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
            if event.inaxes == self.ax1 or event.inaxes == self.ax2:
                self.x1 = event.xdata
                self.y1 = event.ydata
            #print self.x0,self.x1
            #print self.y0,self.y1
            y0,y1 = self.ax1.get_ylim()
            self.rect1.set_width(self.x1 - self.x0)
            self.rect1.set_height(y1 - y0)
            self.rect1.set_xy((self.x0, y0))
            self.rect1.set_linestyle('dashed')

            self.ax1.figure.canvas.draw()


            if self.ax2 != None:
                
                y0,y1 = self.ax2.get_ylim()
                self.rect2.set_width(self.x1 - self.x0)
                self.rect2.set_height(y1 - y0)
                self.rect2.set_xy((self.x0, y0))
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
        #print 'release'
        if event.inaxes == self.ax1 or event.inaxes == self.ax2:
            self.x1 = event.xdata
        #self.y1 = event.ydata
        y0,y1 = self.ax1.get_ylim()
        self.rect1.set_width(self.x1 - self.x0)
        self.rect1.set_height(y1 - y0)
        self.rect1.set_xy((self.x0, y0))
        self.rect1.set_linestyle('solid')
        if self.fin_col == False:
            self.rect1.set_edgecolor('None')


        self.ax1.figure.canvas.draw()
        if self.ax2 != None:
            y0,y1 = self.ax2.get_ylim()
            self.rect2.set_width(self.x1 - self.x0)
            self.rect2.set_height(y1 - y0)
            self.rect2.set_xy((self.x0, y0))
            self.rect2.set_linestyle('solid')
            if self.fin_col == False:
                self.rect2.set_edgecolor('None')

            self.ax2.figure.canvas.draw()
        if self.ax3 != None:
            self.rect3.set_width(self.x1 - self.x0)
            self.rect3.set_height(self.y1 - self.y0)
            self.rect3.set_xy((self.x0, self.y0))
            self.rect3.set_linestyle('solid')
            if self.fin_col == False:
                self.rect3.set_edgecolor('None')

            self.ax3.figure.canvas.draw()
        self.is_pressed=False

        roi_x0 =int(min(self.x0,self.x1))
        roi_x1 =int(max(self.x0,self.x1))
        #roi_y0 =int(min(self.y0,self.y1))
        #roi_y1 =int(max(self.y0,self.y1))
        hist_list=[roi_x0,roi_x1,self.ax1]
        #self.emit(QtCore.SIGNAL('hist'),hist_list)
        self.histSignal.emit(hist_list)

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
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
def basepath(path):
    head, tail = ntpath.split(path)
    return head or ntpath.basename(tail)