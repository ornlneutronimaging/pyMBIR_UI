from qtpy.QtWidgets import QDialog, QMainWindow
import os
from tomoORNL_ui import load_ui
import versioneer

from ngievaluation import available_algorithms
from tomoORNL_ui.utilities.get import Get


class HelpHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def about(self):
        o_about = About(parent=self.parent)
        o_about.show()

    def fitting_algorithm(self):
        o_get = Get(parent=self.parent)
        current_algo_fit_name = o_get.algorithm_selected()
        if self.parent.algo_help_id is None:
            o_fitting = FittingAlgorithm(parent=self.parent, current_algo_fit_name=current_algo_fit_name)
            o_fitting.show()
            self.parent.algo_help_id = o_fitting
        else:
            self.parent.algo_help_id.set_fitting_algorithm(current_algo_fit_name=current_algo_fit_name)
            self.parent.algo_help_id.activateWindow()
            self.parent.algo_help_id.setFocus


class FittingAlgorithm(QMainWindow):

    list_algo = None
    user_list_algo = None

    def __init__(self, parent=None, current_algo_fit_name=''):
        self.parent = parent

        QMainWindow.__init__(self, parent=parent)
        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('ui',
                                                 'fitting_algorithm_helper.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Fitting Algorithm Helper")

        self.initialize_widgets()
        self.set_fitting_algorithm(current_algo_fit_name)

    def initialize_widgets(self):
        list_algo, user_list_algo = Get.algorithms_list()
        self.list_algo = list_algo
        self.user_list_algo = user_list_algo
        for value, user_value in zip(list_algo, user_list_algo):
            self.ui.pre_processing_fitting_procedure_comboBox.addItem(user_value, value)

    def set_fitting_algorithm(self, current_algo_fit_name):
        current_user_algo_fit_name = available_algorithms[current_algo_fit_name]['name']
        self.ui.pre_processing_fitting_procedure_comboBox.setCurrentText(current_user_algo_fit_name)

        description = available_algorithms[current_algo_fit_name]['description']
        reference = available_algorithms[current_algo_fit_name]['reference']

        description = description if description else ""
        reference = reference if reference else "n/a"
        description += "\n\nREFERENCE: " + reference

        self.ui.description_textBrowser.setText(description)

    def fitting_algorithm_changed(self, current_algo_fit_name):
        description = None
        reference = None
        for key in available_algorithms.keys():
            name = available_algorithms[key]['name']
            if name == current_algo_fit_name:
                description = available_algorithms[key]['description']
                reference = available_algorithms[key]['reference']

        description = description if description else ""
        reference = reference if reference else "n/a"
        description += "\n\nREFERENCE: " + reference

        self.ui.description_textBrowser.setText(description)

    def ok_clicked(self):
        if self.parent.algo_help_id:
            self.parent.algo_help_id = None

        self.close()

    def closeEvent(self, c):
        self.ok_clicked()


class About(QDialog):

    def __init__(self, parent=None):
        self.parent = parent
        QDialog.__init__(self, parent=parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'about.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("About")

        self.populate_widgets()

    def populate_widgets(self):
        version = versioneer.get_version()
        self.ui.version_label.setText(version)
