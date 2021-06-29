from NeuNorm.normalization import Normalization

from . import DataType


class Loader:

    def __init__(self, parent=None, data_type=DataType.projections):
        self.parent = parent
        self.data_type = data_type

    def retrieve_data(self, file_index=0):
        """
        Method that returns the data at the specified file index. If not in memory yet,
        it will load it and then return it
        """
        # load_success = False
        # data_type = self.data_type

        list_of_data = self.parent.input['data'][self.data_type]
        if not (list_of_data[file_index] == []):
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
