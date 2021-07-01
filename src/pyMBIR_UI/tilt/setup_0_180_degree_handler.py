from qtpy.QtWidgets import QDialog
from qtpy.QtWidgets import QVBoxLayout
import numpy as np
import os
import pyqtgraph as pg
import logging

from .. import load_ui
from ..utilities.gui import Gui
from pyMBIR_UI import DataType
from ..loader import Loader


class Setup0180DegreeHandler(QDialog):

    index_of_0_degree_image_when_entering_ui = None
    index_of_180_degree_image_when_entering_ui = None

    preview_histogram = None

    def __init__(self, parent=None):
        self.parent = parent
        super(Setup0180DegreeHandler, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'setup_0_180_degrees_images.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("0 and 180 degrees images setup")

        self.initialization()
        self.update_display()

    def initialization(self):

        # pyqtgraph
        self.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.image_view.ui.roiBtn.hide()
        self.ui.image_view.ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.ui.image_view)
        self.ui.widget.setLayout(image_layout)

        # comboboxes
        list_of_files = self.parent.input['list files'][DataType.projections]

        o_gui = Gui(parent=self)
        o_gui.block_signal_handler(block=True,
                                   ui=self.ui.image_0_degrees_comboBox)
        self.ui.image_0_degrees_comboBox.addItems(list_of_files)
        o_gui.block_signal_handler(block=False,
                                   ui=self.ui.image_0_degrees_comboBox)

        o_gui.block_signal_handler(block=True,
                                   ui=self.ui.image_180_degrees_comboBox)
        self.ui.image_180_degrees_comboBox.addItems(list_of_files)
        o_gui.block_signal_handler(block=False,
                                   ui=self.ui.image_180_degrees_comboBox)

        # 0 and 180 degrees images
        self.ui.image_180_degrees_comboBox.setCurrentIndex(self.parent.tilt_correction_index_dict['180_degree'])
        self.ui.image_0_degrees_comboBox.setCurrentIndex(self.parent.tilt_correction_index_dict['0_degree'])

        self.index_of_0_degree_image_when_entering_ui = self.parent.tilt_correction_index_dict['0_degree']
        self.index_of_180_degree_image_when_entering_ui = self.parent.tilt_correction_index_dict['180_degree']

    def update_display(self):
        histogram_level = self.preview_histogram
        _res_view = self.ui.image_view.getView()
        _res_view_box = _res_view.getViewBox()
        _state = _res_view_box.getState()

        first_update = False
        if histogram_level is None:
            first_update = True
        histo_widget = self.ui.image_view.getHistogramWidget()
        histogram_level = histo_widget.getLevels()
        self.preview_histogram = histogram_level

        index_of_180_degree_image = self.parent.tilt_correction_index_dict['180_degree']
        index_of_0_degree_image = self.parent.tilt_correction_index_dict['0_degree']

        o_loader = Loader(parent=self.parent)
        image_of_180_degree = o_loader.retrieve_data(file_index=index_of_180_degree_image)
        image_of_0_degree = o_loader.retrieve_data(file_index=index_of_0_degree_image)

        transparency_image_180_coefficient = self.ui.transparency_horizontalSlider.value()

        final_image = transparency_image_180_coefficient * image_of_180_degree + \
                      (100 - transparency_image_180_coefficient) * image_of_0_degree
        image = np.transpose(final_image)
        self.ui.image_view.setImage(image)

        _res_view_box.setState(_state)
        if not first_update:
            histo_widget.setLevels(histogram_level[0], histogram_level[1])

    def slider_clicked(self):
        self.update_display()

    def slider_moved(self, value):
        self.update_display()

    def image_0_degree_changed(self, value):
        self.parent.tilt_correction_index_dict['0_degree'] = value
        self.update_display()

    def image_180_degree_changed(self, value):
        self.parent.tilt_correction_index_dict['180_degree'] = value
        self.update_display()

    def ok_clicked(self):
        image_0_degree_index = self.ui.image_0_degrees_comboBox.currentIndex()
        self.parent.tilt_correction_index_dict['0_degree'] = image_0_degree_index

        image_180_degree_index = self.ui.image_180_degrees_comboBox.currentIndex()
        self.parent.tilt_correction_index_dict['180_degree'] = image_180_degree_index

        logging.info("0 and 180 degrees tilt image has been set to:")
        logging.info(f"-> index of 0 degree: {image_0_degree_index}")
        logging.info(f"-> index of 180 degrees: {image_180_degree_index}")

        self.close()

    def reject(self):
        self.parent.tilt_correction_index_dict['0_degree'] = self.index_of_0_degree_image_when_entering_ui
        self.parent.tilt_correction_index_dict['180_degree'] = self.index_of_180_degree_image_when_entering_ui

        logging.info("User canceled ui that set up the 0 and 180 degrees images for tilt correction")
        logging.info(f"-> index of 0 degree: {self.index_of_0_degree_image_when_entering_ui}")
        logging.info(f"-> index of 180 degrees: {self.index_of_180_degree_image_when_entering_ui}")

        self.close()

    def closeEvent(self, e):
        pass
