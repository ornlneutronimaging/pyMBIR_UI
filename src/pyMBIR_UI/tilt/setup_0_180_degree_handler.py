from qtpy.QtWidgets import QDialog
from .. import load_ui
import os


class Setup0180DegreeHandler(QDialog):

    def __init__(self, parent=None):
        super(Setup0180DegreeHandler, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'setup_0_180_degrees_images.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("0 and 180 degrees images setup")

    def closeEvent(self):
        pass
