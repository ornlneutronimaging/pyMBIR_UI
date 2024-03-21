from qtpy.uic import loadUi
from qtpy import QtGui
import os

# from pyMBIR_UI._version import get_versions

# __version__ = get_versions()['version']
# del get_versions

__all__ = ['load_ui', 'lock_image', 'unlock_image']


def load_ui(ui_filename, baseinstance):
    return loadUi(ui_filename, baseinstance=baseinstance)


root = os.path.dirname(os.path.realpath(__file__))
lock_image = os.path.join(root, "static/lock.png")
unlock_image = os.path.join(root, "static/unlock.png")
help_image = os.path.join(root, "static/help.png")
refresh_image = os.path.join(root, "static/refresh.png")

not_ok_cell_content_background = QtGui.QColor(255, 0, 0)
ok_cell_content_background = QtGui.QColor(255, 255, 255)

interact_me_style = "background-color: lime"
error_style = "background-color: red"
normal_style = ""

file_extension_accepted = ['tiff', 'tif', 'fits']


class DataType:
    projections = "projections"
    df = "df"
    ob = "ob"
    output = "output"


class TiltAlgorithm:
    direct_minimization = "direct minimization"
    phase_correlation = "phase correlation"
    use_center = "use center"
    user_defined = "user defined"


class ReconstructionAlgorithm:
    pymbir = "pymbir"
    other = "other"


class SessionKeys:
    homepath = "homepath"
