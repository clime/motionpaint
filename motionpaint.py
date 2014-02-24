#!/usr/bin/env python

import sys
import signal

from PyQt4 import QtGui

from window_ui import MainWindow
from motion_painter import MotionPainter


class App(QtGui.QApplication):
    def __init__(self, args):
        QtGui.QApplication.__init__(self,  args)
        self.setStyle("cleanlooks")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.window = MainWindow()
        self.motion_painter = MotionPainter(self.window)

    def run(self):
        self.window.show()
        sys.exit(self.exec_())


if __name__ == "__main__":
    app = App(sys.argv)
    app.run()
