from qtpy import QtGui, QtCore
from qtpy.QtWidgets import QTableWidgetItem, QTableWidgetSelectionRange


class TableHandler:

    def __init__(self, table_ui=None):
        self.table_ui = table_ui

    def block_signals(self, block=True):
        self.table_ui.blockSignals(block)

    def get_item_str_from_cell(self, row=-1, column=-1):
        item_selected = self.table_ui.item(row, column).text()
        return str(item_selected)

    def insert_item(self, row=0, column=0, value="", format_str="{}", editable=True):
        _str_value = format_str.format(value)
        _item = QTableWidgetItem(_str_value)
        if not editable:
            _item.setFlags(QtCore.Qt.ItemIsEnabled)
           # _item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.table_ui.setItem(row, column, _item)

    def insert_empty_row(self, row=0):
        self.table_ui.insertRow(row)

    def insert_row(self, row=0, list_col_name=None):
        """row is the row number
        """
        self.table_ui.insertRow(row)
        for column, _text in enumerate(list_col_name):
            _item = QTableWidgetItem(_text)
            self.table_ui.setItem(row, column, _item)

    def row_count(self):
        return self.table_ui.rowCount()

    def set_background_color(self, row=0, column=0, qcolor=QtGui.QColor(0, 255, 255)):
        _item = self.table_ui.item(row, column)
        _item.setBackground(qcolor)

    def set_column_sizes(self, column_sizes=None):
        for _col, _size in enumerate(column_sizes):
            self.table_ui.setColumnWidth(_col, _size)

    def set_column_width(self, column_width=None):
        self.set_column_sizes(column_sizes=column_width)

    def set_widget(self, row=0, column=0, widget=None):
        self.table_ui.setCellWidget(row, column, widget)

    def set_item(self, row=0, column=0, editable=True):
        _item = self.table_ui.item(row, column)
        if not editable:
            _item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        else:
            _item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable)

    def set_item_value(self, row=0, column=0, value=""):
        _item = self.table_ui.item(row, column).setText(str(value))

    def set_widget_comboBox(self, ui=None, value=""):
        index_of_text = ui.findText(value)
        ui.setCurrentIndex(index_of_text)
