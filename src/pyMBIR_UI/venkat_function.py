from qtpy.QtCore import QObject, Signal
import time
import numpy as np
import logging


class Worker(QObject):
    finished = Signal()
    progress = Signal(int)
    sent_reconstructed_array = Signal(np.ndarray)

    def run(self, dictionary_of_arguments=None):

        nbr_iteration = 20
        sleeping_time = 3  # s

        for _i in np.arange(nbr_iteration):
            time.sleep(sleeping_time)
            fake_2d_array = np.random.random((512, 512))
            self.sent_reconstructed_array.emit(fake_2d_array)

            logging.info(f"worker iteration {_i+1}/{nbr_iteration}")

            self.progress.emit(_i+1)
        self.finished.emit()
