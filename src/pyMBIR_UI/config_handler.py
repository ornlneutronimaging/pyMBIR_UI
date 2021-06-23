import json
import os
import copy
from dataio import DataType


class ConfigHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def load(self):
        config_file_name = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_file_name) as f:
            config = json.load(f)
        reformated_config = self.reformat_config_using_datatype(config=config)
        self.parent.config = reformated_config
        self.parent.selected_instrument = reformated_config['default_instrument']
        self.parent.homepath = reformated_config['homepath']

    def reformat_config_using_datatype(self, config=None):

        reformated_config = copy.deepcopy(config)
        parameters_tab_table_dict = reformated_config['parameters_tab']['table']
        for key in parameters_tab_table_dict.keys():
            _input_list = parameters_tab_table_dict[key]
            _new_list = [DataType.sample if _val == "sample data" else _val for _val in _input_list]
            _new_list = [DataType.ob if _val == "open beam" else _val for _val in _new_list]
            _new_list = [DataType.di if _val == "dark image" else _val for _val in _new_list]
            parameters_tab_table_dict[key] = _new_list

        return reformated_config
