from qtpy.QtWidgets import QProgressBar

from .config_handler import ConfigHandler
from . import interact_me_style


class GuiInitialization:

    def __init__(self, parent=None):
        self.parent = parent

        # load config
        o_config = ConfigHandler(parent=self.parent)
        o_config.load()

    def all(self):
        """initialize everything here"""
        self.widgets()
        self.statusbar()

    def widgets(self):
        self.parent.ui.select_projections_pushButton.setStyleSheet(interact_me_style)
        self.parent.ui.tabWidget.setTabEnabled(1, False)
        self.parent.ui.tabWidget.setTabEnabled(2, False)

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)
