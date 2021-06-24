import numpy as np

from . import DataType


class CropHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def initialize_view(self):
        list_image = self.parent.input['data'][DataType.projections]
        if list_image is None:
            return

        first_image = list_image[0]
        transpose_image = np.transpose(first_image)
        self.parent.crop_image_view.setImage(transpose_image)
