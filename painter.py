import cv2
import numpy as np
from numpy.core import multiarray # NOTE: pyinstaller needs this

from PyQt4 import QtNetwork # NOTE: pyinstaller needs this
from PyQt4 import QtCore, QtGui

class Painter(QtCore.QObject):
    def __init__(self, mainWindow):
        super(QtCore.QObject, self).__init__()

        self.before_first_frame = True # to init stuff based on the properties of the first frame

        qcolor = mainWindow.colorPicker.color
        self.color = (qcolor.blue(), qcolor.green(), qcolor.red())
        self.alphaIncrement = mainWindow.alphaSetter.alpha
        self.threshold = mainWindow.thresholdSetter.threshold
        self.fading = mainWindow.fadingSetter.fading

        mainWindow.colorPicker.colorChanged.connect(self.onColorChanged)
        mainWindow.alphaSetter.alphaChanged.connect(self.onAlphaChanged)
        mainWindow.thresholdSetter.thresholdChanged.connect(self.onThresholdChanged)
        mainWindow.fadingSetter.fadingChanged.connect(self.onFadingChanged)
        mainWindow.videoWidget.newFrame.connect(self.processFrame)
        mainWindow.videoWidget.sourceChanged.connect(self.onVideoSourceChanged)

        self.prevFrameInited = False
        self.frameCount = 0

    @QtCore.pyqtSlot(QtGui.QColor)
    def onColorChanged(self, newColor):
        self.color = (newColor.blue(), newColor.green(), newColor.red())
        self.alphas.fill(0)

    @QtCore.pyqtSlot(float)
    def onAlphaChanged(self, newAlphaIncrement):
        self.alphaIncrement = newAlphaIncrement
        self.alphas.fill(0)

    @QtCore.pyqtSlot(int)
    def onThresholdChanged(self, newThreshold):
        self.threshold = newThreshold
        self.alphas.fill(0)

    @QtCore.pyqtSlot(float)
    def onFadingChanged(self, newFading):
        self.fading = newFading
        self.alphas.fill(0)

    def onVideoSourceChanged(self):
        self.before_first_frame = True

    @QtCore.pyqtSlot(np.ndarray)
    def processFrame(self, frame):
        self.frameCount += 1

        # smooth frames to get rid of false positives
        smoothedFrame = cv2.GaussianBlur(frame, (3, 3), 0)

        if self.before_first_frame:
            self.alphas = np.zeros((frame.shape[0], frame.shape[1]), dtype=float)
            self.prevFrame = smoothedFrame
            self.before_first_frame = False

        # subtract current frame from previous one
        diff = cv2.absdiff(self.prevFrame, smoothedFrame)

        # convert difference to grayscale
        greyDiff = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)

        # grayscale to black and white (i.e. false and true)
        retval, mask = cv2.threshold(greyDiff, self.threshold, 1, cv2.THRESH_BINARY)

        #contours, hiearchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        #cv2.drawContours(frame, contours, -1, (255, 0, 0), 1)

        # add up some alpha for color-changed regions
        cv2.add(self.alphas, self.alphaIncrement, self.alphas, mask)

        # apply fading
        self.alphas -= self.fading

        np.clip(self.alphas, 0, 1, self.alphas)

        # calculate betas
        betas = 1 - self.alphas

        # 1-channel to 3-channel
        alphasMerged = cv2.merge([self.alphas, self.alphas, self.alphas])
        betasMerged = cv2.merge([betas, betas, betas])

        # fade out original image
        frame *= betasMerged

        # calculate color mask
        colorMask = np.ones((frame.shape[0], frame.shape[1], 3), np.uint8) * alphasMerged * self.color

        # fade in color mask
        frame += colorMask

        # copy current smoothed frame to prev frame
        self.prevFrame = smoothedFrame
