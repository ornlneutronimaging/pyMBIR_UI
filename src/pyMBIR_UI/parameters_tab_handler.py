from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QDialog, QComboBox
import os
import numpy as np
import logging

from . import lock_image, unlock_image
from . import load_ui, ok_cell_content_background, not_ok_cell_content_background
from .utilities.table_utilities import TableHandler
from .status_message_config import show_status_message, StatusMessageStatus


class ParametersTabHandler:
    """
    REMARK:
    when adding new widgets that need to be populated in the Paramter tab, edit the config.json
    by adding the full path of the info in the session dict
    ex:
     "full period" -> ["general settings", "full period"]
    """
    all_cells_content_is_ok = True

    def __init__(self, parent=None):
        self.parent = parent

    def check_state_main_tabs(self):
        if not self.parent.parameters_lock_activated:
            nbr_tabs = self.parent.ui.top_tabWidget.count()
            for _tab_index in np.arange(nbr_tabs):
                if _tab_index == 2:
                    continue
                self.parent.ui.top_tabWidget.setTabEnabled(_tab_index, False)
        else:
            self.parent.ui.top_tabWidget.setTabEnabled(0, True)

    def update_lock_widget(self):
        is_lock_activated = self.parent.parameters_lock_activated
        if is_lock_activated:
            image = lock_image
        else:
            image = unlock_image
        icon = QIcon(image)
        self.parent.ui.parameters_lock.setIcon(icon)
        self._set_enabled_all_parameters_widgets(enabled_status=not is_lock_activated)

    def _set_enabled_all_parameters_widgets(self, enabled_status=True):
        parameters_list_ui = self.parent.parameters_list_ui
        o_table = TableHandler(table_ui=self.parent.ui.parameters_tableWidget)
        o_table.block_signals(block=True)
        for _key in parameters_list_ui.keys():
            _ui = parameters_list_ui[_key]['ui']
            if _ui is None:
                _row = parameters_list_ui[_key]['row']
                o_table.set_item(row=_row, column=1, editable=enabled_status)
            else:
                _ui.setEnabled(enabled_status)
        o_table.block_signals(block=False)

    def launch_parameters_password(self):
        logging.info(f"Unlocking PARAMETERS table!")
        o_pass_ui = ParametersPasswordDialog(grand_parent=self.parent,
                                             parent=self)
        o_pass_ui.show()

    def refresh_content(self):
        """will repopulate the table according to the workspace dictionary

        matching key and value can be found by looking at  import_data_handler.py (self.list_ui)
        and config.json ['parameters_tab']['table']
        """
        session_dict = self.parent.session_dict
        parameters_list_ui = self.parent.parameters_list_ui
        o_table = TableHandler(table_ui=self.parent.ui.parameters_tableWidget)
        o_table.block_signals(block=True)

        def populate_table(key=None, session_dict_keys=None):
            """
            Populate table using values saved in session_dict
            """
            ui = parameters_list_ui[key]['ui']

            _value = session_dict
            if session_dict_keys == [""]:
                try:
                    _value = session_dict[key]
                except KeyError:
                    _value = None
            else:
                for _key in session_dict_keys:
                    _value = _value.get(_key, None)

            if _value is None:
                _value = ""

            if ui is None:
                row = parameters_list_ui[key]['row']
                o_table.set_item_value(row=row, column=1, value=_value)
                o_table.set_background_color(row=row, column=0, qcolor=ok_cell_content_background)
                o_table.set_background_color(row=row, column=1, qcolor=ok_cell_content_background)

            elif type(ui) == QComboBox:
                o_table.set_widget_comboBox(ui=ui, value=str(_value))

        for _key, _value in self.parent.config['parameters_tab']['table'].items():
            populate_table(key=_key,
                           session_dict_keys=_value)

        o_table.block_signals(block=False)
        logging.info("Refresh PARAMETERS table content")

    def save_content(self):
        self.parent.ui.parameters_reset_pushButton.setEnabled(True)

    def check_cell_content(self, row=0):

        def is_integer(n):
            try:
                float(n)
            except ValueError:
                return False
            else:
                return float(n).is_integer()

        def is_float(n):
            try:
                float(n)
            except ValueError:
                return False
            else:
                return float(n).is_float()

        self.all_cells_content_is_ok = True

        list_row_where_to_check_if_path_exist = [0, 1, 2, 4, 5, 6, 8, 9, 10]
        list_row_where_to_check_if_integer = [12, 15]
        #list_row_where_to_check_if_integer = [12, 15, 27]
        list_row_where_to_check_if_integer = [12, 15, 27]
        # list_row_where_to_check_if_float = [14, 17, 18, 19, 20, 22, 23, 24, 25]

        o_table = TableHandler(table_ui=self.parent.ui.parameters_tableWidget)
        nbr_row = o_table.row_count()
        for _row in np.arange(nbr_row):
            cell_background = ok_cell_content_background
            if _row in list_row_where_to_check_if_path_exist:
                _value = o_table.get_item_str_from_cell(row=_row, column=1)
                if not _value == "":
                    if not os.path.exists(_value):
                        self.all_cells_content_is_ok = False
                        cell_background = not_ok_cell_content_background

            # elif _row in list_row_where_to_check_if_float:
            #     if not is_float(_value):
            #         self.all_cells_content_is_ok = False
            #         cell_background = not_ok_cell_content_background

            elif _row in list_row_where_to_check_if_integer:
                _value = o_table.get_item_str_from_cell(row=_row, column=1)
                if not is_integer(_value):
                    self.all_cells_content_is_ok = False
                    cell_background = not_ok_cell_content_background

            else:
                continue

            o_table.set_background_color(row=_row, column=1, qcolor=cell_background)
            o_table.set_background_color(row=_row, column=0, qcolor=cell_background)

        if not self.all_cells_content_is_ok:
            self.parent.ui.parameters_lock.setEnabled(False)
        else:
            self.parent.ui.parameters_lock.setEnabled(True)


class ParametersPasswordDialog(QDialog):

    def __init__(self, grand_parent=None, parent=None):
        self.grand_parent = grand_parent
        self.parent = parent

        QDialog.__init__(self, parent=grand_parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'parameters_password.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Password")

    def accept(self):
        password_entered = str(self.ui.password_lineEdit.text()).strip()
        if password_entered == self.grand_parent.config["parameters_tab"]["password"]:
            self.grand_parent.parameters_lock_activated = False
            show_status_message(parent=self.grand_parent,
                                message="",
                                status=StatusMessageStatus.ready)
            self.grand_parent.ui.parameters_reset_pushButton.setEnabled(True)
            logging.info(f"Unlocked PARAMETERS tab with success!")
        else:
            show_status_message(parent=self.grand_parent,
                                message="Wrong password!",
                                status=StatusMessageStatus.error,
                                duration_s=10)
            logging.info(f"Unlocked PARAMETERS tab Failed (wrong password)!")
        self.parent.update_lock_widget()
        self.parent.check_state_main_tabs()

        self.close()
