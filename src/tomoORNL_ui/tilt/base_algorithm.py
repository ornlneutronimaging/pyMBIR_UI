import numpy as np

from .. import DataType
from ..loader import Loader


class BaseAlgorithm:

    image_0_degree = None
    image_180_degree = None

    def __init__(self, parent=None):
        self.parent = parent

        index_0_degree = self.parent.tilt_correction_index_dict['0_degree']
        index_180_degree = self.parent.tilt_correction_index_dict['180_degree']

        image_0_degree = self.parent.input['data'][DataType.projections][index_0_degree]
        if np.shape(image_0_degree) == ():
            o_loader = Loader(parent=self.parent)
            image_0_degree = o_loader.retrieve_data(file_index=index_0_degree)
        self.image_0_degree = image_0_degree

        image_180_degree = self.parent.input['data'][DataType.projections][index_180_degree]
        if np.shape(image_180_degree) == ():
            o_loader = Loader(parent=self.parent)
            image_180_degree = o_loader.retrieve_data(file_index=index_180_degree)
        self.image_180_degree = image_180_degree
