#!/usr/bin/env python

import cv2
import cv2.cv as cv

import sys
import signal

from PyQt4 import QtGui
from PyQt4 import QtCore

from window_ui import WindowUI
from motion_painter import MotionPainter


class MainWindow(QtGui.QMainWindow):
    color_changed = QtCore.pyqtSignal(QtGui.QColor)
    new_frame = QtCore.pyqtSignal(cv.iplimage)

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.ui = WindowUI()
        self.ui.setup(self)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()


class App(QtGui.QApplication):
    def __init__(self, args):
        QtGui.QApplication.__init__(self,args)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.window = MainWindow()
        self.motion_painter = MotionPainter(self.window)

    def run(self):
        self.window.show()
        sys.exit(self.exec_())


if __name__ == "__main__":
    app = App(sys.argv)
    app.run()
