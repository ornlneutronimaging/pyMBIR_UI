from . import DataType


class CenterOfRotation:

    def __init__(self, parent=None):
        self.parent = parent

    def initialization(self):
        list_of_files = self.parent.input['list files'][DataType.projections]
        self.parent.ui.center_of_rotation_0_degrees_comboBox.addItems(list_of_files)
        self.parent.ui.center_of_rotation_180_degrees_comboBox.addItems(list_of_files)

    def master_checkbox_clicked(self):
        status = self.parent.ui.master_checkBox.isChecked()
        list_ui = [self.parent.ui.center_of_rotation_frame,
                   self.parent.ui.center_of_rotation_0_degree_label,
                   self.parent.ui.center_of_rotation_0_degrees_comboBox,
                   self.parent.ui.center_of_rotation_180_degree_label,
                   self.parent.ui.center_of_rotation_180_degrees_comboBox]
        for _ui in list_ui:
            _ui.setEnabled(status)
