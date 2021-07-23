from qtpy.QtWidgets import QDialog, QVBoxLayout
import os
from . import load_ui
import pyqtgraph as pg
import numpy as np

from . import DataType
from .loader import Loader


class PreviewHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def check_status_of_button(self):
        if self.parent.input['data'][DataType.projections] is None:
            self.parent.ui.preview_pushButton.setEnabled(False)
        else:
            self.parent.ui.preview_pushButton.setEnabled(True)


class PreviewLauncher:

    def __init__(self, parent=None, data_type=DataType.projections):
        self.parent = parent
        self.data_type = data_type

        if self.parent.preview_id is None:
            preview_id = Preview(parent=self.parent, data_type=data_type)
            preview_id.show()
            self.parent.preview_id = preview_id
        else:
            self.parent.preview_id.change_data_type(new_data_type=data_type)
            self.parent.preview_id.update_radiobuttons_state()
            self.parent.preview_id.activateWindow()
            self.parent.preview_id.setFocus()

        self.parent.ui.preview_pushButton.setEnabled(False)


class Preview(QDialog):

    image_view = None  # pyqtgraph ui

    histogram_level = None

    radfobuttons = {DataType.projections: None,
                    DataType.ob: None,
                    DataType.df: None,
                   }

    data_type_slider_value = {DataType.projections: -1,
                              DataType.ob: -1,
                              DataType.df: -1,
                              }

    def __init__(self, parent=None, data_type=DataType.projections):
        self.parent = parent
        self.data_type = data_type

        QDialog.__init__(self, parent=parent)
        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('ui',
                                                 'preview.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Preview")

        self.radiobuttons = {DataType.projections: self.ui.sample_radioButton,
                             DataType.ob    : self.ui.ob_radioButton,
                             DataType.df    : self.ui.di_radioButton}

        self.init_pyqtgraph()
        self.update_slider()
        self.update_display_data()
        self.update_radiobuttons_state()
        self.radiobuttons[DataType.projections].setChecked(True)

    def get_data_type(self):
        if self.radiobuttons[DataType.projections].isChecked():
            return DataType.projections
        elif self.radiobuttons[DataType.ob].isChecked():
            return DataType.ob
        else:
            return DataType.df

    def update_display_data(self):
        histogram_level = self.parent.preview_histogram
        _res_view = self.ui.image_view.getView()
        _res_view_box = _res_view.getViewBox()
        _state = _res_view_box.getState()

        first_update = False
        if histogram_level is None:
            first_update = True
        histo_widget = self.ui.image_view.getHistogramWidget()
        histogram_level = histo_widget.getLevels()
        self.parent.preview_histogram = histogram_level

        slider_value = self.ui.slider.value()

        o_loader = Loader(parent=self.parent,
                          data_type=self.data_type)
        _data = o_loader.retrieve_data(file_index=slider_value)
        _filename = os.path.basename(self.parent.input['list files'][self.data_type][slider_value])
        _image = np.transpose(_data)
        self.ui.image_view.setImage(_image)
        self.ui.filename_label.setText(_filename)

        _res_view_box.setState(_state)
        if not first_update:
            histo_widget.setLevels(histogram_level[0], histogram_level[1])

        self.data_type_slider_value[self.data_type] = self.ui.slider.value()

    def update_slider(self):
        list_files = self.parent.input['list files'][self.data_type]
        self.ui.slider.setMaximum(len(list_files)-1)
        self.ui.slider.setValue(0)

    def update_slider_widgets(self):
        slider_value = self.data_type_slider_value[self.data_type]
        if slider_value == -1:
            slider_value = 0

        self.ui.slider.setMaximum(len(self.parent.input['list files'][self.data_type])-1)
        self.ui.slider.setValue(slider_value)

    def init_pyqtgraph(self):
        self.image_view = pg.ImageView(view=pg.PlotItem())
        self.image_view.ui.roiBtn.hide()
        self.image_view.ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.image_view)
        self.ui.image_widget.setLayout(image_layout)

    def update_radiobuttons_state(self):
        for data_type in [DataType.projections, DataType.ob, DataType.df]:
            if self.parent.input['data'][data_type] is None:
                status = False
            else:
                status = True
            self.radiobuttons[data_type].setEnabled(status)

    def change_data_type(self, new_data_type=DataType.projections):
        self.data_type = new_data_type
        self.update_radiobuttons_state()
        self.update_slider_widgets()
        self.update_display_data()

    def slider_moved(self, new_value):
        pass

    def slider_pressed(self):
        self.update_display_data()

    def slider_value_changed(self, new_value):
        self.update_display_data()

    def radiobuttons_changed(self):
        self.data_type = self.get_data_type()
        self.update_slider_widgets()
        self.update_display_data()

    def closeEvent(self, c):
        self.parent.preview_id = None
        self.parent.preview_histogram = None
        self.parent.ui.preview_pushButton.setEnabled(True)
