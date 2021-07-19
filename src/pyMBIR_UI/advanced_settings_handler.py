import os
from qtpy.QtWidgets import QDialog

from . import load_ui


class AdvancedSettingsHandler(QDialog):

    def __init__(self, parent=None):
        self.parent = parent
        super(QDialog, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'password.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
