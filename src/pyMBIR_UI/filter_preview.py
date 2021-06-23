from qtpy import QtWidgets
from qtpy import QtGui
from qtpy import QtCore
from qtpy.QtCore import Signal
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import time
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib import rcParams
from matplotlib.patches import Rectangle
import matplotlib.lines as ml

from .guiresources.matplotlibwidget import MatplotlibWidget, Preview, ROI, Filter_Preview, LINE
from .parameter_widget import ParameterWidget
from .utilities.thread import GenericThread


class Filter_Preview(QtWidgets.QWidget):
    # roiSignal = QtCore.pyqtSignal()
    def __init__(self, name, parent=None):
        QtWidgets.QWidget.__init__(self)
        QtWidgets.QWidget.resize(self, 1300, 700)
        QtWidgets.QWidget.setWindowTitle(self, name)

        self.data_list = []
        self.ob_list = []
        self.dc_list = []
        self.zoom_list = None
        self.limitThread = None
        self.gray_value = None
        self.compare_para = ParameterWidget("Filter Parameter", parent=self)
        # self.mima=[0,0]
        # self.filter_list_raw=[]
        # self.filter_list_f=[]
        self.load_filter_list = []
        self.img_filter_list_raw = []
        self.img_filter_list_filt = []
        # a figure instance to plot on
        # plt.ion()
        self.raw_figure = MatplotlibWidget()
        self.raw_figure.figure.set_tight_layout(True)
        # self.raw_figure.axes.hold(True)
        self.ax1 = self.raw_figure.axes
        self.ax1.set_adjustable('box')
        self.raw_figure.axes.figure.canvas.rectanglecolor = QtCore.Qt.green

        self.fil_figure = MatplotlibWidget(share=self.ax1)
        self.fil_figure.axes.figure.canvas.rectanglecolor = QtCore.Qt.green
        # self.fil_figure.axes.hold(True)
        self.ax2 = self.fil_figure.axes
        self.ax2.set_adjustable('box')
        self.dif_figure = MatplotlibWidget(share=self.ax1)
        self.dif_figure.axes.figure.canvas.rectanglecolor = QtCore.Qt.green
        self.ax3 = self.dif_figure.axes
        self.ax3.set_adjustable('box')

        self.fil_figure.figure.set_tight_layout(True)
        self.dif_figure.figure.set_tight_layout(True)
        self.raw_figure.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.fil_figure.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.dif_figure.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        # self.toolbar=NavigationToolbar(self.raw_figure,self)
        # self.raw_figure.set_tight_layout(True)
        # self.fil_figure.set_tight_layout(True)
        # self.dif_figure.set_tight_layout(True)
        # self.raw_figure.clear()
        # self.fil_figure.clear()
        # self.dif_figure.clear()

        self.raw_hist = MatplotlibWidget()
        self.fil_hist = MatplotlibWidget()
        self.dif_hist = MatplotlibWidget()
        self.raw_hist.figure.set_tight_layout(True)
        self.fil_hist.figure.set_tight_layout(True)
        self.dif_hist.figure.set_tight_layout(True)
        self.raw_hist.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)
        self.fil_hist.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)
        self.dif_hist.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)
        # self.raw_hist.axes.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        self.raw_hist.axes.ticklabel_format(style='sci', axis='y', scilimits=(1, 1))
        # self.fil_hist.axes.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        self.fil_hist.axes.ticklabel_format(style='sci', axis='y', scilimits=(1, 1))
        # self.dif_hist.axes.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        self.dif_hist.axes.ticklabel_format(style='sci', axis='y', scilimits=(1, 1))

        # self.raw_hist.tick_params(axis='x', colors='red')
        # self.raw_hist.tick_params(axis='y', colors='red')

        # self.ax2.figure(sharex(self.ax1))
        self.zoom_Button = QtWidgets.QPushButton("Zoom")
        self.zoom_Button.setCheckable(True)
        self.unzoom_Button = QtWidgets.QPushButton("Unzoom")
        self.para_Button = QtWidgets.QPushButton("Show Filter Values")
        self.con1 = self.raw_figure.axes.figure.canvas.mpl_connect('button_press_event', self.selected)
        self.con2 = self.fil_figure.axes.figure.canvas.mpl_connect('button_press_event', self.selected)
        self.con3 = self.dif_figure.axes.figure.canvas.mpl_connect('button_press_event', self.selected)

        # self.draw2 = self.fil_figure.axes.figure.canvas.mpl_connect('draw_event', self.ondraw)
        # self.draw3 = self.dif_figure.axes.figure.canvas.mpl_connect('draw_event', self.ondraw)

        # mpldatacursor.datacursor(self.ax1,formatter="X:{x:.2f}\nY{y:.2f}\nValue{z:.2f}".format)

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        # self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar1 = NavigationToolbar(self.raw_figure, None)
        self.toolbar2 = NavigationToolbar(self.fil_figure, None)
        self.toolbar3 = NavigationToolbar(self.dif_figure, None)
        # self.roi_Button=QtWidgets.QPushButton("ROI")
        # self.roi_Button.setToolTip("Check to create a ROI in the image. Uncheck to fix the ROI")
        # self.roi_Button.setCheckable(True)
        # self.oscillation_Button=QtWidgets.QPushButton("Oscillation")
        # self.oscillation_Button.setEnabled(False)
        # self.oscillation_Button.setToolTip("Plots the oscillation of the Data images and the OB images in the chosen ROI")

        # self.toolbar.addWidget(self.roi_Button)
        # self.toolbar.addWidget(self.oscillation_Button)

        self.dat_vminSpinBox = QtWidgets.QSpinBox()
        self.dat_vminLabel = QtWidgets.QLabel("Min Grayvalue (Raw/Filtered)")
        self.dat_vminSpinBox.setRange(0, 64000)
        self.dat_vminSpinBox.setSingleStep(500)
        self.dat_vminSpinBox.setEnabled(False)

        self.dat_vmaxSpinBox = QtWidgets.QSpinBox()
        self.dat_vmaxLabel = QtWidgets.QLabel("Max Grayvalue (Raw/Filtered)")
        self.dat_vmaxSpinBox.setRange(0, 64000)
        self.dat_vmaxSpinBox.setValue(32000)
        self.dat_vmaxSpinBox.setSingleStep(500)
        self.dat_vmaxSpinBox.setEnabled(False)

        self.diff_vminSpinBox = QtWidgets.QSpinBox()
        self.diff_vminLabel = QtWidgets.QLabel("Min Grayvalue (Difference)")
        self.diff_vminSpinBox.setRange(0, 64000)
        self.diff_vminSpinBox.setSingleStep(100)
        self.diff_vminSpinBox.setEnabled(False)

        self.diff_vmaxSpinBox = QtWidgets.QSpinBox()
        self.diff_vmaxLabel = QtWidgets.QLabel("Max Grayvalue (Difference)")
        self.diff_vmaxSpinBox.setRange(0, 64000)
        self.diff_vmaxSpinBox.setValue(200)
        self.diff_vmaxSpinBox.setSingleStep(100)
        self.diff_vmaxSpinBox.setEnabled(False)

        # Just some button connected to `plot` method
        # self.typeCombo = QtWidgets.QComboBox()
        self.pixel_Label = QtWidgets.QLabel()
        self.raw_Label = QtWidgets.QLabel()
        self.fil_Label = QtWidgets.QLabel()
        self.dif_Label = QtWidgets.QLabel()
        self.imgCombo = QtWidgets.QComboBox()

        self.zoom_Button.clicked.connect(self.zoom_handling)
        self.unzoom_Button.clicked.connect(self.unzoom_handling)
        self.para_Button.clicked.connect(self.para_handling)

        # self.typeCombo.currentIndexChanged.connect(self.choose_type)
        self.imgCombo.currentIndexChanged.connect(self.choose_img)
        # self.dat_vminSpinBox.valueChanged.connect(self.change_limit)
        # self.dat_vmaxSpinBox.valueChanged.connect(self.change_limit)
        # self.diff_vminSpinBox.valueChanged.connect(self.change_limit)
        # self.diff_vmaxSpinBox.valueChanged.connect(self.change_limit)

        # set the layout
        layout = QtWidgets.QVBoxLayout()
        v_layout1 = QtWidgets.QVBoxLayout()
        v_layout2 = QtWidgets.QVBoxLayout()
        v_layout3 = QtWidgets.QVBoxLayout()
        layout0 = QtWidgets.QHBoxLayout()
        layout1 = QtWidgets.QHBoxLayout()
        layout2 = QtWidgets.QHBoxLayout()
        layout3 = QtWidgets.QHBoxLayout()

        # layout0.addWidget(self.toolbar)
        # layout.addWidget(self.canvas)

        # layout2.addWidget(self.typeCombo)
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

    def selected(self, event):

        if self.zoom_Button.isChecked() == False:
            self.x = int(np.around(event.xdata))
            self.y = int(np.around(event.ydata))
            self.raw_z = self.img_raw[self.y, self.x]
            self.fil_z = self.img_filtered[self.y, self.x]
            self.dif_z = self.img_diff[self.y, self.x]
            self.pixel_Label.setText("Choosen Pixel: (" + str(self.x) + "," + str(self.y) + ")")
            self.raw_Label.setText("Value of choosen Pixel: (" + str(self.raw_z) + ")")
            self.fil_Label.setText("Value of choosen Pixel: (" + str(self.fil_z) + ")")
            self.dif_Label.setText("Value of choosen Pixel: (" + str(self.dif_z) + ")")

        # self.z =

    # def para_handling()
    def zoom_thread(self):
        self.zoomThread = GenericThread(self.zoom_handling)
        self.zoomThread.start()

    def zoom_handling(self):
        self.draw1 = self.raw_figure.axes.figure.canvas.mpl_connect('draw_event', self.ondraw)
        self.toolbar1.zoom()
        self.toolbar2.zoom()
        self.toolbar3.zoom()

    def unzoom_handling(self):
        self.img_raw = self.filter_list[1][self.filter_list[0].index(str(self.imgCombo.currentText()))]
        h, w = self.img_raw.shape
        self.ax1.set_xlim([0, w])
        self.ax1.set_ylim([h, 0])
        self.raw_figure.draw()
        self.ax2.set_xlim([0, w])
        self.ax2.set_ylim([h, 0])
        self.fil_figure.draw()
        self.ax3.set_xlim([0, w])
        self.ax3.set_ylim([h, 0])
        self.dif_figure.draw()
        self.ax1.figure.canvas.mpl_disconnect(self.draw1)
        if self.zoom_Button.isChecked():
            self.toolbar1.zoom()
            self.toolbar2.zoom()
            self.toolbar3.zoom()

            self.zoom_Button.setChecked(False)

    def ondraw(self, event):
        # ax=event.canvas

        x0, x1 = self.ax2.get_xlim()

        y0, y1 = self.ax2.get_ylim()

        self.zoom_list = [y1, y0, x0, x1]

        self.hist_update(self.raw_hist, self.img_raw[int(y1):int(y0), int(x0):int(x1)])
        self.hist_update(self.fil_hist, self.img_filtered[int(y1):int(y0), int(x0):int(x1)])
        self.hist_update(self.dif_hist, self.img_diff[int(y1):int(y0), int(x0):int(x1)])

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

    def change_limit(self, hist):
        if hist[2] == self.raw_hist.axes:
            self.dat_vminSpinBox.setValue(hist[0])
            self.dat_vmaxSpinBox.setValue(hist[1])
        if hist[2] == self.dif_hist.axes:
            self.diff_vminSpinBox.setValue(hist[0])
            self.diff_vmaxSpinBox.setValue(hist[1])

        self.hist_update(self.raw_hist, self.img_raw)
        self.hist_update(self.fil_hist, self.img_filtered)
        self.hist_update(self.dif_hist, self.img_diff)

    def draw_figures(self):
        while True:
            v_min, v_max = self.raw.get_clim()
            v_min_2, v_max_2 = self.diff.get_clim()

            if v_min != self.dat_vminSpinBox.value() or v_max != self.dat_vmaxSpinBox.value():
                self.raw.set_clim(vmin=self.dat_vminSpinBox.value(), vmax=self.dat_vmaxSpinBox.value())
                self.filt.set_clim(vmin=self.dat_vminSpinBox.value(), vmax=self.dat_vmaxSpinBox.value())
                self.raw_figure.draw()
                self.fil_figure.draw()
            if v_min_2 != self.diff_vminSpinBox.value() or v_max_2 != self.diff_vmaxSpinBox.value():
                self.diff.set_clim(vmin=self.diff_vminSpinBox.value(), vmax=self.diff_vmaxSpinBox.value())
                self.dif_figure.draw()

            time.sleep(0.1)

    def choose_img(self):

        try:
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()
            index = self.filter_list[0].index(str(self.imgCombo.currentText()))
            self.img_raw = self.filter_list[1][index]
            self.img_filtered = self.filter_list[2][index]
            self.img_diff = self.img_raw - self.img_filtered

            h, w = self.img_raw.shape
            if self.gray_value == None:
                self.dat_vminSpinBox.setValue(0)
                self.dat_vmaxSpinBox.setValue(1.1 * np.median(self.img_filtered))
                self.gray_value = [self.dat_vminSpinBox.value(), self.dat_vmaxSpinBox.value()]

            self.raw = self.ax1.imshow(self.img_raw, vmin=self.dat_vminSpinBox.value(),
                                       vmax=self.dat_vmaxSpinBox.value(), cmap=plt.cm.gray, interpolation="none")
            self.ax1.set_title("Raw Image")
            self.ax1.set_xlabel("Pixel (x)")
            self.ax1.set_ylabel("Pixel (y)")
            self.ax1.locator_params(axis="x", nbins=4)
            self.ax1.locator_params(axis="y", nbins=4)
            # self.ax1.set_xlim([0,w])
            # self.ax1.set_ylim([h,0])
            self.filt = self.ax2.imshow(self.img_filtered, vmin=self.dat_vminSpinBox.value(),
                                        vmax=self.dat_vmaxSpinBox.value(), cmap=plt.cm.gray, interpolation="none")
            self.ax2.set_title("Filtered Image")
            self.ax2.set_xlabel("Pixel (x)")
            self.ax2.set_ylabel("Pixel (y)")
            self.ax2.locator_params(axis="x", nbins=4)
            self.ax2.locator_params(axis="y", nbins=4)
            self.diff = self.ax3.imshow(self.img_diff, vmin=self.diff_vminSpinBox.value(),
                                        vmax=self.diff_vmaxSpinBox.value(), cmap=plt.cm.gray, interpolation="none")
            self.ax3.set_title("Difference Image")
            self.ax3.set_xlabel("Pixel (x)")
            self.ax3.set_ylabel("Pixel (y)")
            self.ax3.locator_params(axis="x", nbins=4)
            self.ax3.locator_params(axis="y", nbins=4)
            # self.zoom_show([1,h-1,1,w-1])
            if self.zoom_list != None:
                self.ax1.set_xlim([self.zoom_list[2], self.zoom_list[3]])
                self.ax1.set_ylim([self.zoom_list[1], self.zoom_list[0]])
                self.ax2.set_xlim([self.zoom_list[2], self.zoom_list[3]])
                self.ax2.set_ylim([self.zoom_list[1], self.zoom_list[0]])
                self.ax3.set_xlim([self.zoom_list[2], self.zoom_list[3]])
                self.ax3.set_ylim([self.zoom_list[1], self.zoom_list[0]])
            self.raw_figure.draw()
            self.fil_figure.draw()
            self.dif_figure.draw()
            self.figures_thread()

            self.hist_update(self.raw_hist, self.img_raw)
            self.hist_update(self.fil_hist, self.img_filtered)
            self.hist_update(self.dif_hist, self.img_diff)

            self.compare_para.set_para(self.load_filter_list, self.para_list, index)


        except Exception as e:
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

    def hist_update(self, figure, image):
        histogram = np.histogram(image, bins=500, range=(0.1, np.amax(image) + 1))

        bins = histogram[1]
        central_bins = (bins[1:] + bins[:-1]) / 2.
        figure.axes.clear()
        figure.axes.fill_between(central_bins, 0, histogram[0], color="blue")
        figure.axes.set_xlabel("Grayvalue")
        figure.axes.set_ylabel("Pixels")
        figure.axes.set_ylim([0, max(histogram[0]) + 1])
        figure.axes.locator_params(axis="x", nbins=3)
        figure.axes.locator_params(axis="y", nbins=4)
        # figure.axes.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        figure.axes.ticklabel_format(style='sci', axis='y', scilimits=(1, 1))
        if figure == self.raw_hist or figure == self.fil_hist:
            figure.axes.axvline(self.dat_vminSpinBox.value(), color='r')
            figure.axes.axvline(self.dat_vmaxSpinBox.value(), color='r')
        else:
            figure.axes.axvline(self.diff_vminSpinBox.value(), color='r')
            figure.axes.axvline(self.diff_vmaxSpinBox.value(), color='r')
        figure.draw()
        self.data_gray = Gray_ROI(self.raw_hist.axes, ax2=self.fil_hist.axes)
        self.data_gray.hist_update.connect(self.change_limit)
        self.dif_gray = Gray_ROI(self.dif_hist.axes)
        self.dif_gray.hist_update.connect(self.change_limit)

    def add_filtered(self, test_img, raw_list, img_list, para_list):
        # self.filter_list=[]
        self.imgCombo.clear()
        # test_img=str(test_img)
        # temp_ind=test_img.rfind(str(os.path.sep))
        self.load_filter_list = test_img

        self.img_filter_list_raw = raw_list
        self.img_filter_list_filt = img_list
        self.para_list = para_list
        self.filter_list = [self.load_filter_list, self.img_filter_list_raw, self.img_filter_list_filt, self.para_list]
        self.imgCombo.addItems(self.load_filter_list)

        self.imgCombo.setCurrentIndex(self.imgCombo.count() - 1)

        # self.typeCombo.removeItem(self.typeCombo.findText("Filtered Images"))
        # self.typeCombo.addItem("Filtered Images")
        # self.choose_type()+

    def clear(self):
        self.load_filter_list = []
        self.img_filter_list_raw = []
        self.img_filter_list_filt = []
        self.filter = []
        self.imgCombo.clear()
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

    def para_handling(self):
        self.compare_para.show()


class Gray_ROI(QtCore.QObject):
    hist_update = Signal(list)

    def __init__(self, ax1, ax2=None, ax3=None, fin_col=True, color="red"):
        super(Gray_ROI, self).__init__()
        # global roi_x0
        # global roi_x1
        # global roi_y0
        # global roi_y1
        self.ax1 = ax1
        self.ax2 = ax2
        self.ax3 = ax3
        self.fin_col = fin_col
        self.rect1 = Rectangle((0, 0), 1, 1, facecolor='None', edgecolor=color)
        self.rect2 = Rectangle((0, 0), 1, 1, facecolor='None', edgecolor=color)
        self.rect3 = Rectangle((0, 0), 1, 1, facecolor='None', edgecolor=color)
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        # self.ax1=plt.gca()
        self.color = color
        self.ax1.add_patch(self.rect1)
        if self.ax2 != None:
            self.ax2.add_patch(self.rect2)
        if self.ax3 != None:
            self.ax3.add_patch(self.rect3)
        # self.is_pressed=True
        self.ax1_t1 = self.ax1.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.ax1_t2 = self.ax1.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.ax1_t3 = self.ax1.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.ax1_t4 = self.ax1.figure.canvas.mpl_connect('axes_enter_event', self.change_cursor)
        if self.ax2 != None:
            self.ax2_t1 = self.ax2.figure.canvas.mpl_connect('button_press_event', self.on_press)
            self.ax2_t2 = self.ax2.figure.canvas.mpl_connect('button_release_event', self.on_release)
            self.ax2_t3 = self.ax2.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
            self.ax2_t4 = self.ax2.figure.canvas.mpl_connect('axes_enter_event', self.change_cursor)
        if self.ax3 != None:
            self.ax3_t1 = self.ax3.figure.canvas.mpl_connect('button_press_event', self.on_press)
            self.ax3_t2 = self.ax3.figure.canvas.mpl_connect('button_release_event', self.on_release)
            self.ax3_t3 = self.ax3.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
            self.ax3_t4 = self.ax3.figure.canvas.mpl_connect('axes_enter_event', self.change_cursor)
        self.is_pressed = False

    def change_cursor(self, event):
        if self.ax1 == event.inaxes:
            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        if self.ax2 == event.inaxes:
            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))

    def on_press(self, event):

        self.x0 = event.xdata

        self.x1 = event.xdata

        self.rect1.set_width(self.x1 - self.x0)
        y0, y1 = self.ax1.get_ylim()
        self.rect1.set_height(y1 - y0)
        self.rect1.set_xy((self.x0, y0))
        self.rect1.set_linestyle('dashed')
        self.rect1.set_edgecolor(self.color)
        if event.inaxes == self.ax1:
            self.ax1.figure.canvas.draw()

        if self.ax2 != None:
            y0, y1 = self.ax2.get_ylim()
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

        self.is_pressed = True

    def on_motion(self, event):
        # if self.on_press is True:
        # return
        if self.is_pressed == True:
            if event.inaxes == self.ax1 or event.inaxes == self.ax2:
                self.x1 = event.xdata
                self.y1 = event.ydata

            y0, y1 = self.ax1.get_ylim()
            self.rect1.set_width(self.x1 - self.x0)
            self.rect1.set_height(y1 - y0)
            self.rect1.set_xy((self.x0, y0))
            self.rect1.set_linestyle('dashed')

            self.ax1.figure.canvas.draw()

            if self.ax2 != None:
                y0, y1 = self.ax2.get_ylim()
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
        # global roi_x0
        # global roi_x1
        # global roi_y0
        # global roi_y1

        if event.inaxes == self.ax1 or event.inaxes == self.ax2:
            self.x1 = event.xdata
        # self.y1 = event.ydata
        y0, y1 = self.ax1.get_ylim()
        self.rect1.set_width(self.x1 - self.x0)
        self.rect1.set_height(y1 - y0)
        self.rect1.set_xy((self.x0, y0))
        self.rect1.set_linestyle('solid')
        if self.fin_col == False:
            self.rect1.set_edgecolor('None')

        self.ax1.figure.canvas.draw()
        if self.ax2 != None:
            y0, y1 = self.ax2.get_ylim()
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
        self.is_pressed = False

        roi_x0 = int(min(self.x0, self.x1))
        roi_x1 = int(max(self.x0, self.x1))
        # roi_y0 =int(min(self.y0,self.y1))
        # roi_y1 =int(max(self.y0,self.y1))
        hist_list = [roi_x0, roi_x1, self.ax1]

        self.hist_update.emit(hist_list)

        # self.ax1.figure.canvas.draw()

        # return [self.x0,self.x1,self.y0,self.y1]

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
        roi_x0 = int(min(self.x0, self.x1))
        roi_x1 = int(max(self.x0, self.x1))
        roi_y0 = int(min(self.y0, self.y1))
        roi_y1 = int(max(self.y0, self.y1))
        return roi_x0, roi_x1, roi_y0, roi_y1
