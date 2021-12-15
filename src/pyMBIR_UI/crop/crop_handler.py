import numpy as np
from qtpy import QtGui
import pyqtgraph as pg
import logging

from pyMBIR_UI import DataType
from pyMBIR_UI.loader import Loader


class CropHandler:

    pen = pg.mkColor((150, 0, 0, 150))
    brush = pg.mkBrush(pen)

    def __init__(self, parent=None):
        self.parent = parent

    def initialize_crop(self):
        list_image = self.parent.input['data'][DataType.projections]
        if list_image is None:
            return

        # file index
        first_image = list_image[0]
        nbr_files = len(self.parent.input['list files'][DataType.projections])
        self.parent.ui.crop_file_index_horizontalSlider.setMaximum(nbr_files-1)
        image_height, image_width = np.shape(first_image)
        self.parent.crop_image_height = image_height
        self.parent.crop_image_width = image_width

        # self.parent.ui.crop_file_index_horizontalSlider.setValue(self.parent.session_dict['crop']['file index'])
        self.file_index_changed()

        # width
        self.parent.ui.crop_width_horizontalSlider.setMaximum(np.int(image_width/2))
        self.parent.ui.crop_width_horizontalSlider.setValue(self.parent.ui.crop_width_horizontalSlider.maximum())
        self.parent.ui.crop_width_horizontalSlider.setMinimum(10)
        self.parent.ui.crop_width_label.setText(str(image_width))

        # height
        self.parent.ui.crop_from_slice_spinBox.setValue(1)
        self.parent.ui.crop_from_slice_spinBox.setMinimum(1)
        self.parent.ui.crop_to_slice_spinBox.setMaximum(image_height)
        self.parent.ui.crop_to_slice_spinBox.setValue(image_height)
        self.parent.ui.crop_from_slice_spinBox.setMaximum(self.parent.ui.crop_to_slice_spinBox.value() - 1)
        self.parent.ui.crop_to_slice_spinBox.setMinimum(self.parent.ui.crop_from_slice_spinBox.value() + 1)

        self.parent.crop_top_region_item = pg.LinearRegionItem(values=(0, 0),
                                                               orientation='horizontal',
                                                               movable=False,
                                                               brush=self.brush,
                                                               bounds=[0, image_height])
        self.parent.ui.crop_image_view.addItem(self.parent.crop_top_region_item)

        self.parent.crop_bottom_region_item = pg.LinearRegionItem(values=(image_height, image_height),
                                                                  orientation='horizontal',
                                                                  movable=False,
                                                                  brush=self.brush,
                                                                  bounds=[0, image_height])
        self.parent.ui.crop_image_view.addItem(self.parent.crop_bottom_region_item)

        self.parent.crop_left_region_item = pg.LinearRegionItem(values=(0, 0),
                                                                orientation='vertical',
                                                                movable=False,
                                                                brush=self.brush,
                                                                bounds=[0, image_width])
        self.parent.ui.crop_image_view.addItem(self.parent.crop_left_region_item)

        self.parent.crop_right_region_item = pg.LinearRegionItem(values=(image_width, image_width),
                                                                 orientation='vertical',
                                                                 movable=False,
                                                                 brush=self.brush,
                                                                 bounds=[0, image_width])
        self.parent.ui.crop_image_view.addItem(self.parent.crop_right_region_item)

    def crop_slice_spinBox_changed(self, widget='from'):
        """
        widget can take the values 'from', 'to' and 'all'
        """
        if (widget == 'from') or (widget == 'all'):
            from_value = 0
            to_value = self.parent.ui.crop_from_slice_spinBox.value()-1
            value = to_value
            not_movable_red_zone = self.parent.crop_top_region_item
            movable_line = self.parent.crop_from_slice_item
            not_movable_red_zone.setRegion((from_value, to_value))
            movable_line.setValue(value)

        if (widget == 'to') or (widget == 'all'):
            to_value = self.parent.crop_image_height
            from_value = self.parent.ui.crop_to_slice_spinBox.value()-1
            value = from_value
            not_movable_red_zone = self.parent.crop_bottom_region_item
            movable_line = self.parent.crop_to_slice_item
            not_movable_red_zone.setRegion((from_value, to_value))
            movable_line.setValue(value)

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
                self.parent.ui.crop_image_view.removeItem(self.parent.crop_top_region_item)
                self.parent.crop_top_region_item = None
                self.parent.ui.crop_image_view.removeItem(self.parent.crop_bottom_region_item)
                self.parent.crop_bottom_region_item = None
                self.parent.ui.crop_image_view.removeItem(self.parent.crop_left_region_item)
                self.parent.crop_left_region_item = None
                self.parent.ui.crop_image_view.removeItem(self.parent.crop_right_region_item)
                self.parent.crop_right_region_item = None

    def file_index_changed(self):
        file_index_selected = self.parent.ui.crop_file_index_horizontalSlider.value()

        o_loader = Loader(parent=self.parent)
        image = o_loader.retrieve_data(file_index=file_index_selected)
        transpose_image = np.transpose(image)
        self.parent.crop_image_view.setImage(transpose_image)

    def slice_range(self):
        from_slice = self.parent.ui.crop_from_slice_spinBox.value()
        to_slice = self.parent.ui.crop_to_slice_spinBox.value()

        _pen = QtGui.QPen()
        _pen.setColor(QtGui.QColor(0, 255, 255))
        _pen.setWidth(50)

        _hover_pen = QtGui.QPen()
        _hover_pen.setColor(QtGui.QColor(255, 255, 255))
        _hover_pen.setWidth(50)

        image_height = self.parent.crop_image_height
        image_width = self.parent.crop_image_width

        self.parent.crop_from_slice_item = pg.InfiniteLine(from_slice,
                                                           pen=_pen,
                                                           hoverPen=_hover_pen,
                                                           angle=0,
                                                           # span=(0, 1),
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
                                                         hoverPen=_hover_pen,
                                                         angle=0,
                                                         span=(0, 1),
                                                         movable=True,
                                                         bounds=[0, self.parent.crop_image_height-1])
        self.parent.crop_to_slice_label_item = pg.TextItem(text=f"{to_slice}",
                                                           anchor=(0, 1))
        self.parent.crop_to_slice_label_item.setPos(self.parent.crop_image_width, to_slice)
        self.parent.ui.crop_image_view.addItem(self.parent.crop_to_slice_label_item)
        self.parent.ui.crop_image_view.addItem(self.parent.crop_to_slice_item)
        self.parent.crop_to_slice_item.sigPositionChanged.connect(self.parent.crop_to_slice_changed)

        width_value = self.parent.ui.crop_width_horizontalSlider.value()
        max_value = self.parent.ui.crop_width_horizontalSlider.maximum()
        self.parent.crop_left_region_item = pg.LinearRegionItem(values=[0, max_value - width_value],
                                                                orientation='vertical',
                                                                movable=False,
                                                                brush=self.brush,
                                                                bounds=[0, image_width])
        self.parent.ui.crop_image_view.addItem(self.parent.crop_left_region_item)

        self.parent.crop_right_region_item = pg.LinearRegionItem(values=[self.parent.crop_image_width -
                                                                         (max_value - width_value),
                                                                         self.parent.crop_image_width],
                                                                 orientation='vertical',
                                                                 movable=False,
                                                                 brush=self.brush,
                                                                 bounds=[0, image_width])
        self.parent.ui.crop_image_view.addItem(self.parent.crop_right_region_item)

        if self.parent.crop_top_region_item is None:
            pen = pg.mkColor((150, 0, 0, 150))
            brush = pg.mkBrush(pen)
            from_slice_item = self.parent.crop_from_slice_item
            from_value = np.int(from_slice_item.value()) + 1
            self.parent.crop_top_region_item = pg.LinearRegionItem(values=(0, from_value),
                                                                   orientation='horizontal',
                                                                   movable=False,
                                                                   brush=brush,
                                                                   bounds=[0, self.parent.crop_image_height])
            self.parent.ui.crop_image_view.addItem(self.parent.crop_top_region_item)

            to_slice_item = self.parent.crop_to_slice_item
            to_value = np.int(to_slice_item.value()) + 1
            self.parent.crop_bottom_region_item = pg.LinearRegionItem(values=(to_value,
                                                                              self.parent.crop_image_height),
                                                                      orientation='horizontal',
                                                                      movable=False,
                                                                      brush=brush,
                                                                      bounds=[0, self.parent.crop_image_height])
            self.parent.ui.crop_image_view.addItem(self.parent.crop_bottom_region_item)

    def width_changed(self):
        width_value = self.parent.ui.crop_width_horizontalSlider.value()
        max_value = self.parent.ui.crop_width_horizontalSlider.maximum()
        self.parent.ui.crop_width_label.setText(str(width_value*2))

        if self.parent.crop_left_region_item:
            self.parent.crop_left_region_item.setRegion([0, max_value - width_value])
            self.parent.crop_right_region_item.setRegion([self.parent.crop_image_width - (max_value - width_value),
                                                          self.parent.crop_image_width])

    def crop_slice_moved(self, widget='from'):

        if self.parent.crop_to_slice_label_item:
            if widget == 'from':
                self.parent.ui.crop_image_view.removeItem(self.parent.crop_from_slice_label_item)
            else:
                self.parent.ui.crop_image_view.removeItem(self.parent.crop_to_slice_label_item)

        if widget == 'from':
            from_slice_item = self.parent.crop_from_slice_item
            from_value = np.int(from_slice_item.value())+1
            self.parent.ui.crop_from_slice_spinBox.setValue(from_value)
            self.parent.crop_from_slice_label_item = pg.TextItem(text=f"{from_value}",
                                                                 anchor=(0, 1))
            self.parent.crop_from_slice_label_item.setPos(self.parent.crop_image_width, from_value)
            self.parent.ui.crop_image_view.addItem(self.parent.crop_from_slice_label_item)

        else:
            to_slice_item = self.parent.crop_to_slice_item
            to_value = np.int(to_slice_item.value())+1
            self.parent.ui.crop_to_slice_spinBox.setValue(to_value)
            self.parent.crop_to_slice_label_item = pg.TextItem(text=f"{to_value}",
                                                               anchor=(0, 1))
            self.parent.crop_to_slice_label_item.setPos(self.parent.crop_image_width, to_value)
            self.parent.ui.crop_image_view.addItem(self.parent.crop_to_slice_label_item)

        from_value = self.parent.ui.crop_from_slice_spinBox.value()
        to_value = self.parent.ui.crop_to_slice_spinBox.value()

        real_from_value = np.min([from_value, to_value])
        real_to_value = np.max([from_value, to_value])
        self.parent.ui.crop_from_slice_spinBox.setValue(real_from_value)
        self.parent.ui.crop_to_slice_spinBox.setValue(real_to_value)

        self.parent.crop_top_region_item.setRegion([0, from_value])
        self.parent.crop_bottom_region_item.setRegion([to_value, self.parent.crop_image_height])
