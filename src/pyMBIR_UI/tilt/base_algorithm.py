from .. import DataType


class BaseAlgorithm:

    image_0_degree = None
    image_180_degree = None

    def __init__(self, parent=None):
        self.parent = parent

        index_0_degree = self.parent.tilt_correction_index_dict['0_degree']
        index_180_degree = self.parent.tilt_correction_index_dict['180_degree']

        self.image_0_degree = self.parent.input['data'][DataType.projections][index_0_degree]
        self.image_180_degree = self.parent.input['data'][DataType.projections][index_180_degree]
