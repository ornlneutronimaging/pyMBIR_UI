from os.path import expanduser
import os

from dataio import DataType
from ngievaluation import available_algorithms

from .file_utilities import get_short_filename


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def get_data_of_file_with_data_type(self, file_name=None, data_type=DataType.sample):
        o_experiment = self.parent.o_experiment
        if data_type == DataType.sample:
            data_images = o_experiment.sample.dataimages
        elif data_type == DataType.ob:
            # data_images = o_experiment.ob.dataimages
            data_images = o_experiment.reference.dataimages
        else:
            # data_images = o_experiment.di.dataimages
            data_images = o_experiment.offset.dataimages

        selected_file_name = get_short_filename(file_name)

        for _data_image in data_images:
            if selected_file_name == _data_image.get_filename():
                return _data_image.data

    def get_data_sample_selected(self):
        file_name_selected = self.parent.ui.pre_processing_sample_run_comboBox.currentText()
        return self.get_data_of_file_with_data_type(file_name=file_name_selected,
                                                    data_type=DataType.sample)

    def get_automatic_config_file_name(self):
        config_file_name = self.parent.config['session_file_name']
        full_config_file_name = Get.get_full_home_file_name(config_file_name)
        return full_config_file_name

    def get_log_file_name(self):
        log_file_name = self.parent.config['log_file_name']
        full_log_file_name = Get.get_full_home_file_name(log_file_name)
        return full_log_file_name

    def get_main_tab_selected(self):
        current_tab = self.parent.ui.top_tabWidget.currentIndex()
        return current_tab

    def algorithm_selected(self):
        index_selected = self.parent.ui.pre_processing_fitting_procedure_comboBox.currentIndex()
        return self.parent.ui.pre_processing_fitting_procedure_comboBox.itemData(index_selected)

    @staticmethod
    def get_full_home_file_name(base_file_name):
        home_folder = expanduser("~")
        full_log_file_name = os.path.join(home_folder, base_file_name)
        return full_log_file_name

    @staticmethod
    def algorithms_list():
        list_algo = available_algorithms.keys()
        user_list_algo = [available_algorithms[_key]["name"] for _key in list_algo]
        return list_algo, user_list_algo

