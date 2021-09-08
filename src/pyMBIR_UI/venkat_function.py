from qtpy.QtCore import QObject, Signal
import time
import numpy as np
import logging

from qtpy.QtCore import QObject, QThread, Signal


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


class VenkatWorker(QObject):
    finished = Signal()
    progress = Signal(int)
    sent_reconstructed_array = Signal(np.ndarray)

    def init(self, dictionary_of_arguments=None):
        self.dictionary_of_arguments = dictionary_of_arguments

    def run(self):
        venkat_my_function(self.progress, self.finished)


def venkat_my_function(progress, finished):

    for _i in np.arange(10):
        time.sleep(2)
        progress.emit(_i)
    finished.emit()


def run_venkat_function(parent=None):
    parent.thread = QThread()
    parent.worker = VenkatWorker()
    parent.worker.moveToThread(parent.thread)
    parent.thread.started.connect(parent.worker.run)
    parent.worker.finished.connect(parent.thread.quit)
    parent.worker.finished.connect(parent.worker.deleteLater)
    parent.thread.finished.connect(parent.thread.deleteLater)
    parent.worker.progress.connect(reportProgress)
    parent.thread.start()


def reportProgress():
    print("in report progress")
    