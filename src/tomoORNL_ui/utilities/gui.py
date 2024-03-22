import logging


class Gui:

    def __init__(self, parent=None):
        self.parent = parent

    def enable_status_of_menu_buttons(self, enabled=True):
        list_ui = [self.parent.ui.actionSave,
                   self.parent.ui.actionLoad,
                   self.parent.ui.actionSelect_new_instrument]
        for _ui in list_ui:
            _ui.setEnabled(enabled)

    def can_we_enable_fitting_tab(self):
        """return True if all the conditions are met to enable the fitting button"""

        # if "use normalization roi" is checked and no norm_roi_list selected -> False
        if self.parent.ui.use_normalization_roi_checkBox.isChecked():
            if self.parent.norm_roi_list is None:
                logging.warning("Missing normalization ROI!")
                return False

        are_all_data_type = self._are_all_data_type_there()
        if not are_all_data_type:
            return are_all_data_type

        # more check here

        logging.info("Everything in place to activate fitting tab!")
        return True

    def can_we_enable_filters_tab(self):
        are_all_data_type = self._are_all_data_type_there()
        if not are_all_data_type:
            return are_all_data_type

        # more check here

        return True

    def check_ui(self):
        # filters tab
        can_we_enable_filters_tab = self.can_we_enable_filters_tab()
        self.parent.ui.top_tabWidget.setTabEnabled(1, can_we_enable_filters_tab)

        # fitting tab
        if not can_we_enable_filters_tab:
            can_we_enable_fitting_tab = False
        else:
            can_we_enable_fitting_tab = self.can_we_enable_fitting_tab()
        self.parent.ui.top_tabWidget.setTabEnabled(3, can_we_enable_fitting_tab)

    # def _are_all_data_type_there(self):
    #     if self.parent.working_list_files[DataType.sample] is None:
    #         logging.warning("Missing sample data!")
    #         return False
    #
    #     if self.parent.working_list_files[DataType.ob] is None:
    #         logging.warning("Missing ob data!")
    #         return False
    #
    #     if self.parent.working_list_files[DataType.di] is None:
    #         logging.warning("Missing di data!")
    #         return False
    #
    #     return True

    @classmethod
    def enable_those_widgets(list_widgets=None, enable_state=True):
        for _ui in list_widgets:
            _ui.setEnabled(enable_state)

    def block_signal_handler(self, block=True, ui=None):
        ui.blockSignals(block)
