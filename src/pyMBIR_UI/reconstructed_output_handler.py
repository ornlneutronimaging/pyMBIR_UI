from .status_message_config import show_status_message, StatusMessageStatus
import dxchange


class ReconstructedOutputHandler:

    loading_worked = False

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

            self.parent.reconstructed_slices = reconstructed_sliced
            self.parent.list_tiff_reconstructed_files = list_tiff_files
            self.loading_worked = True

        except OSError:
            return

    def initialize_widgets(self):
        nbr_files = len(self.parent.list_tiff_reconstructed_files)

        self.parent.ui.final_reconstructed_slider.setMinimum(1)
        self.parent.ui.final_reconstructed_slider.setMaximum(nbr_files)
        self.parent.ui.final_reconstructed_slider.setValue(1)
        self.slider_changed()

    def slider_changed(self):
        slider_value = self.parent.ui.final_reconstructed_slider.value()
        self.parent.ui.final_reconstructed_label.setText(str(slider_value))
        self.parent.ui.final_reconstructed_selected_file_name_label.setText(
                self.parent.list_tiff_reconstructed_files[slider_value-1])
        self.display_selected_slice(file_index=slider_value-1)

    def display_selected_slice(self, file_index=0):
        data = self.parent.reconstructed_slices[file_index]
        self.parent.ui.reconstructed_image_view.setImage(data)
