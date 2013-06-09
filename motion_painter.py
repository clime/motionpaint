import cv2
import cv2.cv as cv

from numpy.core import multiarray # NOTE: pyinstaller needs this
from PyQt4 import QtNetwork # NOTE: pyinstaller needs this
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QObject

class MotionPainter(QObject):

    def __init__(self, main_window):
        super(QObject, self).__init__()

        frame_size = main_window.ui.cameraWidget.frameSize

        self.prev_frame = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 3)
        self.smoothed_frame = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 3)

        self.diff = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 3)
        self.grey_diff = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 1)

        self.alphas = cv.CreateMat(frame_size[1], frame_size[0], cv.CV_32FC1)
        self.betas = cv.CreateMat(frame_size[1], frame_size[0], cv.CV_32FC1)
        cv.SetZero(self.alphas)

        self.alphas_merged = cv.CreateMat(frame_size[1], frame_size[0], cv.CV_32FC3)
        self.betas_merged = cv.CreateMat(frame_size[1], frame_size[0], cv.CV_32FC3)

        self.mask = cv.CreateMat(frame_size[1], frame_size[0], cv.CV_8UC1)
        self.color_mask = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 3)

        qcolor = main_window.ui.colorpicker.color
        self.color = cv.CV_RGB(qcolor.red(), qcolor.green(), qcolor.blue())
        main_window.color_changed.connect(self.on_color_changed)
        main_window.new_frame.connect(self.process_frame)

    @QtCore.pyqtSlot(QtGui.QColor)
    def on_color_changed(self, new_color):
        self.color = cv.CV_RGB(new_color.red(), new_color.green(), new_color.blue())

    @QtCore.pyqtSlot(cv.iplimage)
    def process_frame(self, frame):
        # smooth frames to get rid of false positives
        cv.Smooth(frame, self.smoothed_frame, cv.CV_GAUSSIAN, 3, 0)

        if not self.prev_frame:
            self.prev_frame = cv.CloneImage(self.smoothed_frame)

        # subtract current frame from previous one
        cv.AbsDiff(self.prev_frame, self.smoothed_frame, self.diff)

        # convert difference to grayscale.
        cv.CvtColor(self.diff, self.grey_diff, cv.CV_RGB2GRAY)

        # grayscale to black and white (i.e. false and true)
        threshold = 20
        cv.Threshold(self.grey_diff, self.mask, threshold, 255, cv.CV_THRESH_BINARY)

        # add up some alpha for color-changed regions
        alpha_increment = 0.04
        cv.AddS(self.alphas, alpha_increment, self.alphas, self.mask)

        # make sure alpha is not more than one (Gight not be needed)
        frame_size = cv.GetSize(frame)
        overflow = cv.CreateMat(frame_size[1], frame_size[0], cv.CV_8UC1)
        cv.InRangeS(self.alphas, 0, 1+1e-10, overflow)
        cv.Not(overflow, overflow)
        cv.Set(self.alphas, 1, overflow)

        # calculate betas
        cv.Set(self.betas, 1)
        cv.Sub(self.betas, self.alphas, self.betas)

        # 1-channel to 3-channel
        cv.Merge(self.alphas, self.alphas, self.alphas, None, self.alphas_merged)
        cv.Merge(self.betas, self.betas, self.betas, None, self.betas_merged)

        # fade out original image
        cv.Mul(frame, self.betas_merged, frame)

        # calculate color mask
        cv.Set(self.color_mask, self.color)
        cv.Mul(self.color_mask, self.alphas_merged, self.color_mask)

        # fade in color mask
        cv.Add(frame, self.color_mask, frame)

        # copy current image to prev image
        self.prev_frame = cv.CloneImage(self.smoothed_frame)
