import cv2
import numpy as np

from PyQt4 import QtCore


class VideoStream(QtCore.QObject):
    DEFAULT_FPS = 30
    newFrame = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, source=0, mirrored=False):
        super(VideoStream, self).__init__()

        self.stream = cv2.VideoCapture(0)
        #self.stream = cv2.VideoCapture('/home/clime/mrak/motionpaint/patron_web.mp4')

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.queryFrame)
        self.timer.setInterval(1000/self.fps)

        self.mirrored = mirrored
        self.paused = False

    def setSource(self, source):
        self.stream.release()
        self.stream.open(source)

    @QtCore.pyqtSlot()
    def queryFrame(self):
        ret, frame = self.stream.read()
        if not ret: return

        if self.mirrored:
            frame = cv2.flip(frame, 1)

        self.newFrame.emit(frame)

    @property
    def paused(self):
        return not self.timer.isActive()

    @paused.setter
    def paused(self, p):
        if p:
            self.timer.stop()
        else:
            self.timer.start()

    @property
    def fps(self):
        fps = self.stream.get(cv2.cv.CV_CAP_PROP_FPS)
        if not fps > 0: fps = self.DEFAULT_FPS
        return fps

    @property
    def frameSize(self):
        w = self.stream.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
        h = self.stream.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
        return int(w), int(h)
