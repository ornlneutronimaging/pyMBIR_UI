from qtpy import QtWidgets
import numpy as np
import multiprocessing

from .utilities.file_utilities import path_leaf


class ParameterWidget(QtWidgets.QDialog):

    def __init__(self, name, parent=None):
        super(ParameterWidget, self).__init__(parent)
        ParameterWidget.resize(self, 300, 450)
        ParameterWidget.setWindowTitle(self, name)

        self.ref_name_Label = QtWidgets.QLabel("Current Image:")
        self.ref_name_LineEdit = QtWidgets.QLineEdit()
        self.ref_name_LineEdit.setEnabled(False)

        self.ref_3x3_Threshold_Label = QtWidgets.QLabel("Threshold 3x3:")
        self.ref_3x3_Threshold_LineEdit = QtWidgets.QLineEdit()
        self.ref_3x3_Threshold_LineEdit.setEnabled(False)

        self.ref_5x5_Threshold_Label = QtWidgets.QLabel("Threshold 5x5:")
        self.ref_5x5_Threshold_LineEdit = QtWidgets.QLineEdit()
        self.ref_5x5_Threshold_LineEdit.setEnabled(False)

        self.ref_7x7_Threshold_Label = QtWidgets.QLabel("Threshold 7x7:")
        self.ref_7x7_Threshold_LineEdit = QtWidgets.QLineEdit()
        self.ref_7x7_Threshold_LineEdit.setEnabled(False)

        self.ref_log_Threshold_Label = QtWidgets.QLabel("Sigma for LoG:")
        self.ref_log_Threshold_LineEdit = QtWidgets.QLineEdit()
        self.ref_log_Threshold_LineEdit.setEnabled(False)

        self.ref_3x3_Pixel_Label = QtWidgets.QLabel("Pixels filtered by 3x3:")
        self.ref_3x3_Pixel_LineEdit = QtWidgets.QLineEdit()
        self.ref_3x3_Pixel_LineEdit.setEnabled(False)

        self.ref_5x5_Pixel_Label = QtWidgets.QLabel("Pixels filtered by 5x5:")
        self.ref_5x5_Pixel_LineEdit = QtWidgets.QLineEdit()
        self.ref_5x5_Pixel_LineEdit.setEnabled(False)

        self.ref_7x7_Pixel_Label = QtWidgets.QLabel("Pixels filtered by 7x7:")
        self.ref_7x7_Pixel_LineEdit = QtWidgets.QLineEdit()
        self.ref_7x7_Pixel_LineEdit.setEnabled(False)

        self.ref_filter_time_Label = QtWidgets.QLabel("Filter Time:")
        self.ref_filter_time_LineEdit = QtWidgets.QLineEdit()
        self.ref_filter_time_LineEdit.setEnabled(False)

        self.ref_processing_time_Label = QtWidgets.QLabel("Stack processing time:")
        self.ref_processing_time_LineEdit = QtWidgets.QLineEdit()
        self.ref_processing_time_LineEdit.setEnabled(False)
        # self.ref_filter_time_LineEdit.setSuffix("s")

        self.roi_size_Label = QtWidgets.QLabel("Chosen ROI ([x0,x1,y0,y1]):")
        self.roi_size_LineEdit = QtWidgets.QLineEdit()
        self.roi_size_LineEdit.setEnabled(False)

        self.bin_Label = QtWidgets.QLabel("Binning of image:")
        self.bin_LineEdit = QtWidgets.QLineEdit()
        self.bin_LineEdit.setEnabled(False)

        self.bin_size_Label = QtWidgets.QLabel("Image size after binning (x,y):")
        self.bin_size_LineEdit = QtWidgets.QLineEdit()
        self.bin_size_LineEdit.setEnabled(False)

        self.median_Label = QtWidgets.QLabel("Blurring of image:")
        self.median_LineEdit = QtWidgets.QLineEdit()
        self.median_LineEdit.setEnabled(False)

        self.comp_name_Label = QtWidgets.QLabel("Comparison Image:")
        self.comp_name_ComboBox = QtWidgets.QComboBox()

        self.comp_3x3_Threshold_Label = QtWidgets.QLabel("Threshold 3x3:")
        self.comp_3x3_Threshold_LineEdit = QtWidgets.QLineEdit()
        self.comp_3x3_Threshold_LineEdit.setEnabled(False)

        self.comp_5x5_Threshold_Label = QtWidgets.QLabel("Threshold 5x5:")
        self.comp_5x5_Threshold_LineEdit = QtWidgets.QLineEdit()
        self.comp_5x5_Threshold_LineEdit.setEnabled(False)

        self.comp_7x7_Threshold_Label = QtWidgets.QLabel("Threshold 7x7:")
        self.comp_7x7_Threshold_LineEdit = QtWidgets.QLineEdit()
        self.comp_7x7_Threshold_LineEdit.setEnabled(False)

        self.comp_log_Threshold_Label = QtWidgets.QLabel("Sigma for LoG:")
        self.comp_log_Threshold_LineEdit = QtWidgets.QLineEdit()
        self.comp_log_Threshold_LineEdit.setEnabled(False)

        self.comp_3x3_Pixel_Label = QtWidgets.QLabel("Pixels filtered by 3x3:")
        self.comp_3x3_Pixel_LineEdit = QtWidgets.QLineEdit()
        self.comp_3x3_Pixel_LineEdit.setEnabled(False)

        self.comp_5x5_Pixel_Label = QtWidgets.QLabel("Pixels filtered by 5x5:")
        self.comp_5x5_Pixel_LineEdit = QtWidgets.QLineEdit()
        self.comp_5x5_Pixel_LineEdit.setEnabled(False)

        self.comp_7x7_Pixel_Label = QtWidgets.QLabel("Pixels filtered by 7x7:")
        self.comp_7x7_Pixel_LineEdit = QtWidgets.QLineEdit()
        self.comp_7x7_Pixel_LineEdit.setEnabled(False)

        self.comp_filter_time_Label = QtWidgets.QLabel("Filter Time:")
        self.comp_filter_time_LineEdit = QtWidgets.QLineEdit()
        self.comp_filter_time_LineEdit.setEnabled(False)
        # self.comp_filter_time_LineEdit.setSuffix("s")

        self.main_layout = QtWidgets.QHBoxLayout()
        self.grid_layout1 = QtWidgets.QGridLayout()
        self.grid_layout2 = QtWidgets.QGridLayout()
        self.vline1 = QtWidgets.QFrame()
        self.vline1.setFrameStyle(QtWidgets.QFrame.VLine)
        self.vline1.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        self.grid_layout1.addWidget(self.ref_name_Label, 1, 1)
        self.grid_layout1.addWidget(self.ref_name_LineEdit, 1, 2)

        self.grid_layout1.addWidget(self.roi_size_Label, 2, 1)
        self.grid_layout1.addWidget(self.roi_size_LineEdit, 2, 2)

        self.grid_layout1.addWidget(self.ref_3x3_Threshold_Label, 3, 1)
        self.grid_layout1.addWidget(self.ref_3x3_Threshold_LineEdit, 3, 2)

        self.grid_layout1.addWidget(self.ref_5x5_Threshold_Label, 4, 1)
        self.grid_layout1.addWidget(self.ref_5x5_Threshold_LineEdit, 4, 2)

        self.grid_layout1.addWidget(self.ref_7x7_Threshold_Label, 5, 1)
        self.grid_layout1.addWidget(self.ref_7x7_Threshold_LineEdit, 5, 2)

        self.grid_layout1.addWidget(self.ref_log_Threshold_Label, 6, 1)
        self.grid_layout1.addWidget(self.ref_log_Threshold_LineEdit, 6, 2)

        self.grid_layout1.addWidget(self.ref_3x3_Pixel_Label, 7, 1)
        self.grid_layout1.addWidget(self.ref_3x3_Pixel_LineEdit, 7, 2)

        self.grid_layout1.addWidget(self.ref_5x5_Pixel_Label, 8, 1)
        self.grid_layout1.addWidget(self.ref_5x5_Pixel_LineEdit, 8, 2)

        self.grid_layout1.addWidget(self.ref_7x7_Pixel_Label, 9, 1)
        self.grid_layout1.addWidget(self.ref_7x7_Pixel_LineEdit, 9, 2)

        self.grid_layout1.addWidget(self.bin_Label, 10, 1)
        self.grid_layout1.addWidget(self.bin_LineEdit, 10, 2)

        self.grid_layout1.addWidget(self.bin_size_Label, 11, 1)
        self.grid_layout1.addWidget(self.bin_size_LineEdit, 11, 2)

        # self.grid_layout1.addWidget(self.median_Label,12,1)
        # self.grid_layout1.addWidget(self.median_LineEdit,12,2)

        self.grid_layout1.addWidget(self.ref_filter_time_Label, 12, 1)
        self.grid_layout1.addWidget(self.ref_filter_time_LineEdit, 12, 2)

        self.grid_layout1.addWidget(self.ref_processing_time_Label, 13, 1)
        self.grid_layout1.addWidget(self.ref_processing_time_LineEdit, 13, 2)

        self.grid_layout2.addWidget(self.comp_name_Label, 1, 1)
        self.grid_layout2.addWidget(self.comp_name_ComboBox, 1, 2)

        self.grid_layout2.addWidget(self.comp_3x3_Threshold_Label, 2, 1)
        self.grid_layout2.addWidget(self.comp_3x3_Threshold_LineEdit, 2, 2)

        self.grid_layout2.addWidget(self.comp_5x5_Threshold_Label, 3, 1)
        self.grid_layout2.addWidget(self.comp_5x5_Threshold_LineEdit, 3, 2)

        self.grid_layout2.addWidget(self.comp_7x7_Threshold_Label, 4, 1)
        self.grid_layout2.addWidget(self.comp_7x7_Threshold_LineEdit, 4, 2)

        self.grid_layout2.addWidget(self.comp_log_Threshold_Label, 5, 1)
        self.grid_layout2.addWidget(self.comp_log_Threshold_LineEdit, 5, 2)

        self.grid_layout2.addWidget(self.comp_3x3_Pixel_Label, 6, 1)
        self.grid_layout2.addWidget(self.comp_3x3_Pixel_LineEdit, 6, 2)

        self.grid_layout2.addWidget(self.comp_5x5_Pixel_Label, 7, 1)
        self.grid_layout2.addWidget(self.comp_5x5_Pixel_LineEdit, 7, 2)

        self.grid_layout2.addWidget(self.comp_7x7_Pixel_Label, 8, 1)
        self.grid_layout2.addWidget(self.comp_7x7_Pixel_LineEdit, 8, 2)

        self.grid_layout2.addWidget(self.comp_filter_time_Label, 9, 1)
        self.grid_layout2.addWidget(self.comp_filter_time_LineEdit, 9, 2)

        self.grid_layout2.addWidget(self.comp_name_Label, 10, 1)
        self.grid_layout2.addWidget(self.comp_name_ComboBox, 10, 2)

        self.main_layout.addLayout(self.grid_layout1)
        # self.main_layout.addWidget(self.vline1)
        # self.main_layout.addLayout(self.grid_layout2)
        self.setLayout(self.main_layout)

    def set_para(self, image_name_list, para_list, index):
        self.data_list = image_name_list
        self.para_list = para_list
        ref_img_name = path_leaf(str(self.data_list[index]))
        temp_ind = ref_img_name.find(".")
        test_time = (self.para_list[index][8] * self.para_list[index][9]) / multiprocessing.cpu_count()
        test_text = "%2i h %2i min %2.1f sec" % (test_time / 3600, (test_time % 3600) / 60, test_time % 60)

        self.ref_name_LineEdit.setText(str(ref_img_name[0:temp_ind]))
        self.ref_3x3_Threshold_LineEdit.setText(str(self.para_list[index][4]))
        self.ref_5x5_Threshold_LineEdit.setText(str(self.para_list[index][5]))
        self.ref_7x7_Threshold_LineEdit.setText(str(self.para_list[index][6]))
        self.ref_log_Threshold_LineEdit.setText(str(self.para_list[index][7]))

        self.ref_3x3_Pixel_LineEdit.setText(str(self.para_list[index][0]) + " (" + str(
            np.around(float(100 * self.para_list[index][0]) / (self.para_list[index][11] * self.para_list[index][12]),
                      3)) + "%)")
        self.ref_5x5_Pixel_LineEdit.setText(str(self.para_list[index][1]) + " (" + str(
            np.around(float(100 * self.para_list[index][1]) / (self.para_list[index][11] * self.para_list[index][12]),
                      3)) + "%)")
        self.ref_7x7_Pixel_LineEdit.setText(str(self.para_list[index][2]) + " (" + str(
            np.around(float(100 * self.para_list[index][2]) / (self.para_list[index][11] * self.para_list[index][12]),
                      3)) + "%)")
        self.ref_filter_time_LineEdit.setText(str(np.around(self.para_list[index][3], 2)) + "s")
        self.ref_processing_time_LineEdit.setText(str(test_text))
        temp_roi = [self.para_list[index][13][2], self.para_list[index][13][3], self.para_list[index][13][0],
                    self.para_list[index][13][1]]
        self.roi_size_LineEdit.setText(str(temp_roi))
        self.bin_LineEdit.setText("(" + str(self.para_list[index][10]) + "x" + str(self.para_list[index][10]) + ")")
        # self.median_LineEdit.setText("("+str(self.para_list[index][12])+"x"+str(self.para_list[index][12])+")")

        self.bin_size_LineEdit.setText(
            "(" + str(self.para_list[index][12]) + "x" + str(self.para_list[index][11]) + ")")
