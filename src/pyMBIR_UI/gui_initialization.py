from qtpy.QtGui import QIcon
import os
from qtpy.QtWidgets import QComboBox
from qtpy.QtWidgets import QProgressBar

from dataio import DataType

from .config_handler import ConfigHandler
from . import lock_image, help_image
from .utilities.table_utilities import TableHandler
from .filter_tab_handler import FilterTabHandler
from .utilities.gui import Gui
from .utilities.get import Get


class GuiInitialization:

    def __init__(self, parent=None):
        self.parent = parent

        # load config
        o_config = ConfigHandler(parent=self.parent)
        o_config.load()

    def all(self):
        """initialize everything here"""
        self.widgets()
        self.import_data_tab()
        self.parameters_tab()
        self.statusbar()
        self.tab_status()
        self.filter_tab()
        self.fitting_tab()

    def select_new_instrument(self):
        if not os.path.exists(self.parent.automatic_config_file_name):
            self.parent.select_new_instrument_menu_clicked()
        else:
            o_gui = Gui(parent=self.parent)
            o_gui.enable_status_of_menu_buttons(enabled=True)

    def widgets(self):
        self.parent.ui.actionAbout.setText("About")
        self.parent.ui.use_normalization_roi_error_message.setVisible(False)

        config_filters = self.parent.config["filters"]
        self.parent.ui.pre_processing_sample_ob_checkBox.setChecked(config_filters["sample data"]["enabled"])
        for _key, _ui in self.parent.list_ui["filters"]["gamma"][DataType.sample].items():
            _ui.setValue(config_filters["sample data"][_key])

        self.parent.ui.pre_processing_di_checkBox.setChecked(config_filters["dc"]["enabled"])
        for _key, _ui in self.parent.list_ui["filters"]["gamma"][DataType.di].items():
            _ui.setValue(config_filters["dc"][_key])

        list_algo, user_list_algo = Get.algorithms_list()
        for value, user_value in zip(list_algo, user_list_algo):
            self.parent.ui.pre_processing_fitting_procedure_comboBox.addItem(user_value, value)

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

    def import_data_tab(self):
        """initialize widgets"""

        # interact me style for ob and di (as tab are disabled anyway)
        self.parent.ui.open_beam_browse_pushButton.setStyleSheet(self.parent.interact_me_style)
        self.parent.ui.dark_image_browse_pushButton.setStyleSheet(self.parent.interact_me_style)

        # disable ob and df tabs
        self.parent.ui.import_data_tabs.setTabEnabled(1, False)
        self.parent.ui.import_data_tabs.setTabEnabled(2, False)

        # disable filter and fitting tab
        self.parent.ui.top_tabWidget.setTabEnabled(1, False)
        self.parent.ui.top_tabWidget.setTabEnabled(3, False)

        # parameters tab
        icon = QIcon(lock_image)
        self.parent.ui.parameters_lock.setIcon(icon)

    def parameters_tab(self):
        list_row_labels = self.parent.config["parameters_tab"]["table"].keys()
        o_table = TableHandler(table_ui=self.parent.ui.parameters_tableWidget)
        o_table.set_column_width(column_width=[300, 200])
        o_table.block_signals(block=True)

        parameters_list_ui = {}
        for _row, _label in enumerate(list_row_labels):
            o_table.insert_empty_row(row=_row)

            o_table.insert_item(row=_row,
                                column=0,
                                value=_label,
                                editable=False)

            if _label in ["full period",
                          ''"sample/ob gamma filter",
                          "dc gamma filter",
                          "median filter",
                          "image binning flag",
                          "outlier removal in epithermal dc flag",
                          "use norm region of interest",
                        ]:
                combo_box = QComboBox()
                combo_box.addItems(["True", "False"])
                combo_box.currentTextChanged.connect(self.parent.parameters_combobox_cell_changed)
                o_table.set_widget(row=_row, column=1, widget=combo_box)
                parameters_list_ui[_label] = {'row': _row,
                                              'ui': combo_box}
                combo_box.setEnabled(False)

            elif _label == "fit procedure":
                combo_box = QComboBox()
                combo_box.addItems(self.parent.config['fitting']['list procedures'])
                combo_box.currentTextChanged.connect(self.parent.parameters_combobox_cell_changed)
                o_table.set_widget(row=_row, column=1, widget=combo_box)
                parameters_list_ui[_label] = {'row': _row,
                                              'ui': combo_box}
                combo_box.setEnabled(False)

            else:
                # no widget for this row
                parameters_list_ui[_label] = {'row': _row,
                                              'ui': None}
                o_table.insert_item(row=_row,
                                    column=1,
                                    value="",
                                    editable=False)

        self.parent.parameters_list_ui = parameters_list_ui
        o_table.block_signals(block=False)

    def filter_tab(self):
        help_icon = QIcon(help_image)
        self.parent.ui.gamma_filtering_help_pushButton.setIcon(help_icon)

        o_pre_processing = FilterTabHandler(parent=self.parent)
        o_pre_processing.update_widgets()

    def tab_status(self):
        self.parent.tab_to_enabled = {self.parent.ui.top_tabWidget: [True, False, True]}

    def fitting_tab(self):
        index_fit_procedure_selected = self.parent.config["fitting"]["index procedure selected"]
        self.parent.ui.pre_processing_fitting_procedure_comboBox.setCurrentIndex(index_fit_procedure_selected)
