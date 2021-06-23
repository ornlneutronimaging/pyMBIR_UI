from qtpy.QtWidgets import QDialog
import os
import logging

from . import load_ui
from .utilities.get import Get


class SelectInstrumentLauncher(QDialog):

    def __init__(self, parent=None, config=None):
        self.parent = parent
        QDialog.__init__(self, parent=parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'instrument_selection.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Instrument Selection")

        list_of_instruments = list(config['list_of_instruments'].keys())

        if config:
            self.ui.list_instrument_comboBox.addItems(list_of_instruments)

        if parent.selected_instrument in list_of_instruments:
            index = list_of_instruments.index(parent.selected_instrument)
            self.ui.list_instrument_comboBox.setCurrentIndex(index)

        self.ui.ok_pushButton.setStyleSheet(self.parent.interact_me_style)

        self.enable_status_of_menu_buttons(enabled=False)

    def ok_clicked(self):
        new_current_instrument = self.ui.list_instrument_comboBox.currentText()
        logging.info(f"New instrument selected: {new_current_instrument}")
        self.parent.selected_instrument = new_current_instrument
        self.parent.ui.sample_data_browse_pushButton.setStyleSheet(self.parent.interact_me_style)
        self.enable_status_of_menu_buttons(enabled=True)
        o_get = Get(parent=self.parent)
        main_tab_index = o_get.get_main_tab_selected()
        if main_tab_index == 1:
            self.parent.main_tab_changed(1)
        self.close()

    def enable_status_of_menu_buttons(self, enabled=True):
        list_ui = [self.parent.ui.actionSave,
                   self.parent.ui.actionLoad,
                   self.parent.ui.actionSelect_new_instrument]
        for _ui in list_ui:
            _ui.setEnabled(enabled)
