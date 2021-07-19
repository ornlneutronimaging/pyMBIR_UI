import os
from qtpy.QtWidgets import QMainWindow

from . import load_ui


class AdvancedSettingsPasswordHandler(QMainWindow):

    def __init__(self, parent=None):
        self.parent = parent
        super(QMainWindow, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'password.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)

    def validate_password(self):
        password = self.ui.password_input.text()
        if password == self.parent.config["advanced_settings_password"]:

            self.close()

    def ok_clicked(self):
        pass

    def cancel_clicked(self):
        self.close()


class AdvancedSettingsHandler(QMainWindow):

    def __init__(self, parent=None):
        self.parent = parent
        super(QMainWindow, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'advanced_settings.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
