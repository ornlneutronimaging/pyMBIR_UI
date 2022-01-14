from .status_message_config import show_status_message, StatusMessageStatus
import dxchange


class ReconstructedOutputHandler:

    reconstructed_slices = None

    def __init__(self, parent=None):
        self.parent = parent

    def load_reconstructed_slices(self, list_tiff_files):
        # load and display 3D volume
        reconstructed_sliced = []

        show_status_message(parent=self.parent,
                            message=f"Loading reconstructed volume ...",
                            status=StatusMessageStatus.working)

        self.parent.eventProgress.setMaximum(len(list_tiff_files))
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        try:

            for _index, _file in enumerate(list_tiff_files):
                _data = dxchange.reader.read_tiff(_file)
                reconstructed_sliced.append(_data)
                self.parent.eventProgress.setValue(_index + 1)

            self.reconstructed_slices = reconstructed_sliced

        except OSError:
            return

    def initialize(self):
        pass

    def slider_changed(self):
        pass

    def display_selected_slice(self):
        pass