import cv2
import numpy as np
import os
import re

from PyQt4 import QtCore


class VideoStream(QtCore.QObject):
    class State:
        STOPPED = 0
        PAUSED = 1
        PLAYING = 2
        CLOSED = 3

    DEFAULT_FPS = 15
    newFrame = QtCore.pyqtSignal(np.ndarray)
    sourceChanged = QtCore.pyqtSignal()
    stateChanged = QtCore.pyqtSignal(int)

    def __init__(self, source=0, output=None):
        super(VideoStream, self).__init__()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.processFrame)
        self.stream = cv2.VideoCapture()
        self.resetSource(source)
        self.recordingOn = False
        self.resetOutput(output)

    def resetSource(self, source=None):
        self.stop()
        self.stream.release()
        if source or source == 0:
            self.stream.open(source)
            _, _ = self.stream.read() # we need to preread the first frame to have fps, w, h info available
            self.timer.setInterval(1000/self.fps)
        self.stateChanged.emit(self.state)
        self.sourceChanged.emit()

    def resetOutput(self, output=None):
        if output:
            self.outputPath = output
            self.diffOutputPath = os.path.join(os.path.dirname(self.outputPath), re.sub(r'(\w*)(\..*)', r'\1-diff\2', os.path.basename(self.outputPath)))
            self.videoWriter.open(self.outputPath, cv2.cv.CV_FOURCC('M','J','P','G'), self.fps, self.frameSize)
            self.diffVideoWriter.open(self.diffOutputPath, cv2.cv.CV_FOURCC('M','J','P','G'), self.fps, self.frameSize)
        else:
            self.outputPath = None
            self.diffOutputPath = None
            self.videoWriter = cv2.VideoWriter()
            self.diffVideoWriter = cv2.VideoWriter()

    # does not work :-(
    def setSize(self, w=640, h=480):
        self.stream.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, w)
        self.stream.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, h)

    @QtCore.pyqtSlot()
    def processFrame(self):
        ret, frame = self.stream.read()
        if not ret:
            return
        orig_frame = frame.copy()
        self.newFrame.emit(frame)
        if self.recordingOn and self.videoWriter.isOpened() and self.diffVideoWriter.isOpened():
            self.videoWriter.write(frame)
            self.diffVideoWriter.write(frame - orig_frame)

    def stop(self):
        self.recordStop()
        self.timer.stop()
        self.stream.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 0)
        self.stateChanged.emit(self.state)

    def pause(self):
        self.timer.stop()
        self.stateChanged.emit(self.state)

    def play(self):
        self.timer.start()
        self.stateChanged.emit(self.state)

    def record(self):
        open(self.outputPath, 'w').close() # empty the file
        open(self.diffOutputPath, 'w').close() # empty the file
        self.recordingOn = True

    def recordStop(self):
        self.recordingOn = False

    @property
    def isInputOpened(self):
        return self.stream.isOpened()

    @property
    def isOutputOpened(self):
        return self.videoWriter.isOpened()

    @property
    def state(self):
        if not self.isInputOpened:
            return VideoStream.State.CLOSED
        elif self.timer.isActive():
            return VideoStream.State.PLAYING
        elif self.stream.get(cv2.cv.CV_CAP_PROP_POS_FRAMES) != 0: # does not work properly, returns -1 or 0 :(
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

    def setFPS(self, fps):
        self.stream.set(cv2.cv.CV_CAP_PROP_FPS, fps)
