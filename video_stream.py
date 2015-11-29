import cv2
import numpy as np

from PyQt4 import QtCore


class VideoStream(QtCore.QObject):
    class State:
        STOPPED = 0
        PAUSED = 1
        PLAYING = 2

    DEFAULT_FPS = 30
    newFrame = QtCore.pyqtSignal(np.ndarray)
    sourceChanged = QtCore.pyqtSignal()
    stateChanged = QtCore.pyqtSignal(int)

    def __init__(self, source=0):
        super(VideoStream, self).__init__()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.readFrame)
        self.preReadFrame = None
        self.stream = cv2.VideoCapture()
        self.setSource(source)

    def setSource(self, source):
        self.stream.release()
        self.stream = cv2.VideoCapture(source)
        _, preReadFrame = self.stream.read() # we need to preread the first frame to have fps, w, h info available
        self.sourceChanged.emit()
        self.timer.setInterval(1000/self.fps)

    # does not work :-(
    def setSize(self, w=640, h=480):
        self.stream.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, w)
        self.stream.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, h)

    @QtCore.pyqtSlot()
    def readFrame(self):
        if self.preReadFrame:
            self.newFrame.emit(self.preReadFrame)
            self.preReadFrame = None
            return
        ret, frame = self.stream.read()
        if not ret:
            return
        self.newFrame.emit(frame)

    def stop(self):
        self.timer.stop()
        self.stream.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 0)
        self.stateChanged.emit(self.state)

    def pause(self):
        self.timer.stop()
        self.stateChanged.emit(self.state)

    def play(self):
        self.timer.start()
        self.stateChanged.emit(self.state)

    @property
    def state(self):
        if self.timer.isActive():
            return VideoStream.State.PLAYING
        elif self.stream.get(cv2.cv.CV_CAP_PROP_POS_FRAMES) != 0:
            return VideoStream.State.PAUSED
        return VideoStream.State.STOPPED

    @property
    def fps(self):
        fps = self.stream.get(cv2.cv.CV_CAP_PROP_FPS)
        if not fps > 0:
            fps = self.DEFAULT_FPS
        return fps

    @property
    def frameSize(self):
        w = self.stream.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
        h = self.stream.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
        return int(w), int(h)
