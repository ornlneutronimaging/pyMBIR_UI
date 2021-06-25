import numpy as np
from qtpy import QtGui, QtCore
import pyqtgraph as pg

from . import DataType


class CropHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def initialize_crop(self):
        list_image = self.parent.input['data'][DataType.projections]
        if list_image is None:
            return

        self.file_index_changed()

        # file index
        first_image = list_image[0]
        nbr_files = len(self.parent.input['list files'][DataType.projections])
        self.parent.ui.crop_file_index_horizontalSlider.setMaximum(nbr_files-1)
        image_height, image_width = np.shape(first_image)
        self.parent.crop_image_height = image_height
        self.parent.crop_image_width = image_width

        # width
        self.parent.ui.crop_width_horizontalSlider.setMaximum(image_width)
        self.parent.ui.crop_width_horizontalSlider.setValue(image_width)
        self.parent.ui.crop_width_label.setText(str(image_width))
        self.parent.ui.crop_width_horizontalSlider.setMinimum(20)

        # height
        self.parent.ui.crop_from_slice_label.setText("1")
        self.parent.ui.crop_to_slice_label.setText(str(image_height))

    def master_checkbox_clicked(self):
        self.parent.ui.crop_frame.setEnabled(self.parent.ui.cropping_checkBox.isChecked())

        if self.parent.ui.cropping_checkBox.isChecked():
            self.slice_range()
        else:
            if self.parent.crop_from_slice_item:
                self.parent.ui.crop_image_view.removeItem(self.parent.crop_from_slice_item)
                self.parent.crop_from_slice_item = None
                self.parent.ui.crop_image_view.removeItem(self.parent.crop_to_slice_item)
                self.parent.crop_to_slice_item = None
                self.parent.ui.crop_image_view.removeItem(self.parent.crop_from_slice_label_item)
                self.parent.crop_from_slice_label_item = None
                self.parent.ui.crop_image_view.removeItem(self.parent.crop_to_slice_label_item)
                self.parent.crop_to_slice_label_item = None

    def file_index_changed(self):
        file_index_selected = self.parent.ui.crop_file_index_horizontalSlider.value()
        list_image = self.parent.input['data'][DataType.projections]
        image = list_image[file_index_selected]
        transpose_image = np.transpose(image)
        self.parent.crop_image_view.setImage(transpose_image)

    def slice_range(self):
        from_slice = np.int(str(self.parent.ui.crop_from_slice_label.text()))
        to_slice = np.int(str(self.parent.ui.crop_to_slice_label.text()))

        _pen = QtGui.QPen()
        _pen.setColor(QtGui.QColor(255, 0, 0))
        _pen.setWidth(0.01)

        self.parent.crop_from_slice_item = pg.InfiniteLine([0, 0],
                                                           pen=_pen,
                                                           angle=0,
                                                           span=(0, 1),
                                                           movable=True,
                                                           bounds=[0, self.parent.crop_image_height-1])
        self.parent.crop_from_slice_label_item = pg.TextItem(text=f"{from_slice}",
                                                             anchor=(0, 1))
        self.parent.crop_from_slice_label_item.setPos(self.parent.crop_image_width, from_slice)
        self.parent.ui.crop_image_view.addItem(self.parent.crop_from_slice_label_item)
        self.parent.ui.crop_image_view.addItem(self.parent.crop_from_slice_item)
        self.parent.crop_from_slice_item.sigPositionChanged.connect(self.parent.crop_from_slice_changed)

        self.parent.crop_to_slice_item = pg.InfiniteLine([0, to_slice],
                                                         pen=_pen,
                                                         angle=0,
                                                         span=(0, 1),
                                                         movable=True,
                                                         bounds=[0, self.parent.crop_image_height-1])
        self.parent.crop_to_slice_label_item = pg.TextItem(text=f"{to_slice}",
                                                           anchor=(0, 1))
        self.parent.crop_to_slice_label_item.setPos(self.parent.crop_image_width, to_slice)
        self.parent.ui.crop_image_view.addItem(self.parent.crop_to_slice_label_item)
        self.parent.ui.crop_image_view.addItem(self.parent.crop_to_slice_item)
        self.parent.crop_to_slice_item.sigPositionChanged.connect(self.parent.crop_from_slice_changed)

    def crop_slice_moved(self):
        if self.parent.crop_to_slice_label_item:
            self.parent.ui.crop_image_view.removeItem(self.parent.crop_from_slice_label_item)
            self.parent.ui.crop_image_view.removeItem(self.parent.crop_to_slice_label_item)

        from_slice_item = self.parent.crop_from_slice_item
        from_value = np.int(from_slice_item.value())+1
        self.parent.crop_from_slice_label_item = pg.TextItem(text=f"{from_value}",
                                                             anchor=(0, 1))
        self.parent.crop_from_slice_label_item.setPos(self.parent.crop_image_width, from_value)
        self.parent.ui.crop_image_view.addItem(self.parent.crop_from_slice_label_item)

        to_slice_item = self.parent.crop_to_slice_item
        to_value = np.int(to_slice_item.value())+1
        self.parent.crop_to_slice_label_item = pg.TextItem(text=f"{to_value}",
                                                           anchor=(0, 1))
        self.parent.crop_to_slice_label_item.setPos(self.parent.crop_image_width, to_value)
        self.parent.ui.crop_image_view.addItem(self.parent.crop_to_slice_label_item)

        real_from_value = np.min([from_value, to_value])
        real_to_value = np.max([from_value, to_value])
        self.parent.ui.crop_from_slice_label.setText(str(real_from_value))
        self.parent.ui.crop_to_slice_label.setText(str(real_to_value))
