from qtpy.QtCore import QObject, Signal
import time
import numpy as np
import logging


class Worker(QObject):
    finished = Signal()
    progress = Signal(int, float)
    sent_reconstructed_array = Signal(np.ndarray)

    def init(self, dictionary_of_arguments=None):
        self.dictionary_of_arguments = dictionary_of_arguments

    def run(self):

        nbr_iteration = 20
        sleeping_time = 3  # s
        dictionary_of_arguments = self.dictionary_of_arguments

        my_function(nbr_iteration, sleeping_time, self.finished, self.progress, self.sent_reconstructed_array)

        # for _i in np.arange(nbr_iteration):
        #     time.sleep(sleeping_time)
        #     fake_2d_array = np.random.random((512, 512))
        #     self.sent_reconstructed_array.emit(fake_2d_array)    # I need this
        #
        #     logging.info(f"worker iteration {_i+1}/{nbr_iteration}")
        #
        #     self.progress.emit(_i+1, 0.5)
        # self.finished.emit()


def my_function(nbr_iteration, sleeping_time, finished, progress, sent_reconstructed_array):

    for _i in np.arange(nbr_iteration):
        time.sleep(sleeping_time)
        fake_2d_array = np.random.random((512, 512))
        sent_reconstructed_array.emit(fake_2d_array)  # I need this

        logging.info(f"worker iteration {_i + 1}/{nbr_iteration}")

        progress.emit(_i + 1, 0.5)
    finished.emit()
