import numpy as np
import logging

from NeuNorm.normalization import Normalization

from . import DataType
from pyMBIR_UI.utilities.get import Get


class Loader:

    def __init__(self, parent=None, data_type=DataType.projections):
        self.parent = parent
        self.data_type = data_type

    def retrieve_data(self, file_index=0):
        """
        Method that returns the data at the specified file index. If not in memory yet,
        it will load it and then return it
        """
        list_of_data = self.parent.input['data'][self.data_type]
        if not (list_of_data[file_index] is None):
            return list_of_data[file_index]

        self.load_data(file_index=file_index)
        return self.parent.input['data'][self.data_type][file_index]

    def load_data(self, file_index=0):
        list_of_files = self.parent.input['list files'][self.data_type]
        file_to_load = list_of_files[file_index]

        o_norm = Normalization()
        o_norm.load(file=file_to_load, notebook=False)

        data = o_norm.data['sample']['data'][0]
        self.parent.input['data'][self.data_type][file_index] = data

        if self.parent.image_size['width'] is None:
            self.parent.image_size['height'], self.parent.image_size['height'] = np.shape(data)

    def load_angles(self):
        if self.data_type != DataType.projections:
            return

        if self.parent.loading_from_config:
            self.parent.input['list angles'] = [np.float(angle) for angle in self.parent.session_dict['list angles']]
            self.parent.loading_from_config = False
        else:

            o_get = Get(parent=self.parent)
            list_angles = o_get.angles(self.parent.input['list files'][self.data_type])
            self.parent.input['list angles'] = list_angles

            logging.info(f"List of angles retrieved is: {list_angles}")
