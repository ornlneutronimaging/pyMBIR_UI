from qtpy.QtWidgets import QDialog
from qtpy.QtWidgets import QVBoxLayout
from .. import load_ui
import os
import pyqtgraph as pg


class Setup0180DegreeHandler(QDialog):

    def __init__(self, parent=None):
        super(Setup0180DegreeHandler, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'setup_0_180_degrees_images.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("0 and 180 degrees images setup")

        self.initialization()

    def initialization(self):

        # pyqtgraph
        self.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.image_view.ui.roiBtn.hide()
        self.ui.image_view.ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.ui.image_view)
        self.ui.widget.setLayout(image_layout)

    def slider_clicked(self):
        pass

    def slider_moved(self, value):
        pass

    def image_0_degree_changed(self, value):
        pass

    def image_180_degree_changed(self, value):
        pass

    def ok_clicked(self):
        self.close()

    def closeEvent(self):
        pass

