from qtpy.QtCore import Signal
from qtpy import QtCore


class GenericThread(QtCore.QThread):
    def __init__(self, function, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    def run(self):
        self.function(*self.args,**self.kwargs)


class GenericThreadStartEnd(QtCore.QThread):
    startSignal = Signal(int)
    finishedSignal = Signal(int)

    def __init__(self, function, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    def run(self):
        self.startSignal.emit(1)
        self.function(*self.args, **self.kwargs)
        self.finishedSignal.emit(1)
