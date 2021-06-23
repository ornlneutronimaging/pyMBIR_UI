import numpy as np

from .parameters_tab_handler import ParametersTabHandler
from .filter_tab_handler import FilterTabHandler
from .session_handler import SessionHandler
from .utilities.gui import Gui


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def main_tab_changed(self, new_tab_index):
        o_para = ParametersTabHandler(parent=self.parent)
        if new_tab_index == 1:  # filters
            o_filter = FilterTabHandler(parent=self.parent)
            o_filter.update_tab_content()

        elif new_tab_index == 2:  # Parameters
            o_session = SessionHandler(parent=self.parent)
            o_session.save_from_ui()
            o_para.refresh_content()
            self.parent.tab_index_was = 2

    def check_fitting_tab_status(self):
        o_gui = Gui(parent=self.parent)
        tab_status = o_gui.can_we_enable_fitting_tab()
        self.parent.ui.top_tabWidget.setTabEnabled(3, tab_status)
