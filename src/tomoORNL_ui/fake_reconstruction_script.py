import time
import numpy as np
from qtpy.QtWidgets import QProgressBar
from qtpy.QtCore import QObject, Signal
import logging


def main(progress_bar_id=None, ui_id=None):

    nbr_iteration = 4
    sleeping_time = 3  # s

    valid_slider_id = False
    if type(progress_bar_id) == QProgressBar:
        progress_bar_id.setMaximum(nbr_iteration)
        progress_bar_id.setValue(0)
        progress_bar_id.setVisible(True)
        valid_slider_id = True

    for _i in np.arange(nbr_iteration):

        time.sleep(sleeping_time)

        fake_2d_array = np.random.random((512, 512))
        if valid_slider_id:
            progress_bar_id.setValue(_i+1)

        if ui_id:
            ui_id.update_output_plot(fake_2d_array)

    if valid_slider_id:
        progress_bar_id.close()


class Worker(QObject):
    finished = Signal()
    progress = Signal(int)

    def run(self):

        nbr_iteration = 4
        sleeping_time = 3  # s

        for _i in np.arange(nbr_iteration):
            time.sleep(sleeping_time)
            logging.info(f"worker iteration {_i}/{nbr_iteration}")

            self.progress.emit(_i+1)
        self.finished.emit()
