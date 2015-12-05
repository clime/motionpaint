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

    def __init__(self, source=0, outputPath=None):
        super(VideoStream, self).__init__()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.processFrame)
        self.preReadFrame = None
        self.stream = cv2.VideoCapture()
        self.resetSource(source)
        self.recordingOn = False
        self.videoWriter = cv2.VideoWriter()
        self.diffVideoWriter = cv2.VideoWriter()
        if outputPath:
            self.setOutput(outputPath)

    def resetSource(self, source=None):
        self.stop()
        self.stream.release()
        if source is not None:
            self.stream.open(source)
            _, preReadFrame = self.stream.read() # we need to preread the first frame to have fps, w, h info available
            self.timer.setInterval(1000/self.fps)
        self.stateChanged.emit(self.state)
        self.sourceChanged.emit()

    def setOutput(self, outputPath):
        diffOutputPath = os.path.dirname(outputPath) + re.sub(r'(\w*)(\..*)?', r'\1-diff\2', os.path.basename(outputPath))
        self.videoWriter.open(outputPath, cv2.cv.CV_FOURCC('M','J','P','G'), self.fps, self.frameSize)
        self.diffVideoWriter.open(diffOutputPath, cv2.cv.CV_FOURCC('M','J','P','G'), self.fps, self.frameSize)

    # does not work :-(
    def setSize(self, w=640, h=480):
        self.stream.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, w)
        self.stream.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, h)

    @QtCore.pyqtSlot()
    def processFrame(self):
        if self.preReadFrame:
            self.newFrame.emit(self.preReadFrame)
            self.preReadFrame = None
            return
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
        open(self.output, 'w').close() # empty the file
        open(self.diffOutput, 'w').close() # empty the file
        self.recordingOn = True

    def recordStop(self):
        self.recordingOn = False

    @property
    def isOpened(self):
        return self.stream.isOpened()

    @property
    def state(self):
        if not self.isOpened:
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
