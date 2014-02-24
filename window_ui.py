# -*- coding: utf-8 -*-

import numpy as np
import cv2

from PyQt4 import QtCore, QtGui
from PyQt4.phonon import Phonon

from video_stream import VideoStream

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def setupUi(self):
        self.setObjectName(_fromUtf8("self"))
        self.resize(1024, 640)

        self.videoWidget = VideoWidget(self, self)
        self.videoWidget.setGeometry(QtCore.QRect(0, 0, 640, 640))
        self.videoWidget.setObjectName(_fromUtf8("videoWidget"))

        self.groupBox = QtGui.QGroupBox('Settings', self);
        self.groupBox.setGeometry(QtCore.QRect(655, 10, 355, 471))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.groupBox.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }");

        self.colorPicker = ColorPicker(self, self.groupBox)
        self.colorPicker.setObjectName(_fromUtf8("colorPicker"))
        self.colorPicker.move(10, 45)

        self.alphaSetter = AlphaSetter(self, self.groupBox)
        self.alphaSetter.setObjectName(_fromUtf8("alphaSetter"))
        self.alphaSetter.move(10, 115)

        self.thresholdSetter = ThresholdSetter(self, self.groupBox)
        self.thresholdSetter.setObjectName(_fromUtf8("thresholdSetter"))
        self.thresholdSetter.move(10, 175)

        self.fadingSetter = FadingSetter(self, self.groupBox)
        self.fadingSetter.setObjectName(_fromUtf8("fadingSetter"))
        self.fadingSetter.move(10, 235)

        self.retranslate()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslate(self):
        self.setWindowTitle(_translate("Motionpaint", "Motionpaint", None))


class ColorPicker(QtGui.QWidget):
    colorChanged = QtCore.pyqtSignal(QtGui.QColor)

    def __init__(self, mainWindow, parent=None):
        super(ColorPicker, self).__init__(parent)
        self.mainWindow = mainWindow
        self.setupUi()

    def setupUi(self):
        self.color = QtGui.QColor(255, 255, 255)

        self.label = QtGui.QLabel('Color', self)
        self.label.setGeometry(0, 0, 120, 20)

        self.btn = QtGui.QPushButton('', self)
        self.btn.setGeometry(0, 25, 335, 25)
        self.btn.setStyleSheet("QWidget { background-color: %s }" % self.color.name())
        self.btn.clicked.connect(self.showDialog)

    def showDialog(self):
        self.mainWindow.videoWidget.pause()
        new_color = QtGui.QColorDialog.getColor(self.color)
        self.mainWindow.videoWidget.play()
        if new_color.isValid():
            self.color = new_color
            self.btn.setStyleSheet("QWidget { background-color: %s }" % self.color.name())
            self.colorChanged.emit(self.color)


class AlphaSetter(QtGui.QWidget):
    alphaChanged = QtCore.pyqtSignal(float)

    def __init__(self, mainWindow, parent=None):
        super(AlphaSetter, self).__init__(parent)
        self.mainWindow = mainWindow
        self.setupUi()

    def setupUi(self):
        self.alpha = 0.5

        self.label = QtGui.QLabel('Alpha increment', self)
        self.label.setGeometry(0, 0, 120, 20)

        self.horizontalSlider = QtGui.QSlider(self)
        self.horizontalSlider.setGeometry(QtCore.QRect(0, 20, 245, 25))
        self.horizontalSlider.setMaximum(100)
        self.horizontalSlider.setSingleStep(1)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName(_fromUtf8("horizontalSlider"))
        self.horizontalSlider.setValue(int(self.alpha*100))

        self.doubleSpinBox = QtGui.QDoubleSpinBox(self)
        self.doubleSpinBox.setGeometry(QtCore.QRect(255, 20, 80, 25))
        self.doubleSpinBox.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.doubleSpinBox.setDecimals(3)
        self.doubleSpinBox.setAccelerated(True)
        self.doubleSpinBox.setMaximum(1)
        self.doubleSpinBox.setSingleStep(0.01)
        self.doubleSpinBox.setValue(self.alpha)

        def alphaChanged(alpha):
            self.alpha = alpha
            self.horizontalSlider.setValue(int(alpha*100))
            self.alphaChanged.emit(alpha)

        QtCore.QObject.connect(self.horizontalSlider, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), lambda v: self.doubleSpinBox.setValue(v/100.0))
        QtCore.QObject.connect(self.doubleSpinBox, QtCore.SIGNAL(_fromUtf8("valueChanged(double)")), alphaChanged)
        QtCore.QMetaObject.connectSlotsByName(self)


class ThresholdSetter(QtGui.QWidget):
    thresholdChanged = QtCore.pyqtSignal(int)

    def __init__(self, mainWindow, parent=None):
        super(ThresholdSetter, self).__init__(parent)
        self.mainWindow = mainWindow
        self.setupUi()

    def setupUi(self):
        self.threshold = 10

        self.label = QtGui.QLabel('Threshold', self)
        self.label.setGeometry(0, 0, 120, 20)

        self.horizontalSlider = QtGui.QSlider(self)
        self.horizontalSlider.setGeometry(QtCore.QRect(0, 20, 245, 25))
        self.horizontalSlider.setMaximum(100)
        self.horizontalSlider.setSingleStep(1)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName(_fromUtf8("horizontalSlider"))
        self.horizontalSlider.setValue(self.threshold)

        self.spinBox = QtGui.QSpinBox(self)
        self.spinBox.setGeometry(QtCore.QRect(255, 20, 80, 25))
        self.spinBox.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.spinBox.setAccelerated(True)
        self.spinBox.setMaximum(100)
        self.spinBox.setSingleStep(1)
        self.spinBox.setValue(self.threshold)

        def thresholdChanged(threshold):
            self.threshold = threshold
            self.horizontalSlider.setValue(threshold)
            self.thresholdChanged.emit(threshold)

        QtCore.QObject.connect(self.horizontalSlider, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.spinBox.setValue)
        QtCore.QObject.connect(self.spinBox, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), thresholdChanged)
        QtCore.QMetaObject.connectSlotsByName(self)


class FadingSetter(QtGui.QWidget):
    fadingChanged = QtCore.pyqtSignal(float)

    def __init__(self, mainWindow, parent=None):
        super(FadingSetter, self).__init__(parent)
        self.mainWindow = mainWindow
        self.setupUi()

    def setupUi(self):
        self.fading = 0.075

        self.label = QtGui.QLabel('Fading', self)
        self.label.setGeometry(0, 0, 120, 20)

        self.horizontalSlider = QtGui.QSlider(self)
        self.horizontalSlider.setGeometry(QtCore.QRect(0, 20, 245, 25))
        self.horizontalSlider.setMaximum(100)
        self.horizontalSlider.setSingleStep(1)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName(_fromUtf8("horizontalSlider"))
        self.horizontalSlider.setValue(int(self.fading*100))

        self.doubleSpinBox = QtGui.QDoubleSpinBox(self)
        self.doubleSpinBox.setGeometry(QtCore.QRect(255, 20, 80, 25))
        self.doubleSpinBox.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.doubleSpinBox.setDecimals(3)
        self.doubleSpinBox.setAccelerated(True)
        self.doubleSpinBox.setMaximum(1)
        self.doubleSpinBox.setSingleStep(0.01)
        self.doubleSpinBox.setValue(self.fading)

        def fadingChanged(fading):
            self.fading = fading
            self.horizontalSlider.setValue(int(fading*100))
            self.fadingChanged.emit(fading)

        QtCore.QObject.connect(self.horizontalSlider, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), lambda v: self.doubleSpinBox.setValue(v/100.0))
        QtCore.QObject.connect(self.doubleSpinBox, QtCore.SIGNAL(_fromUtf8("valueChanged(double)")), fadingChanged)
        QtCore.QMetaObject.connectSlotsByName(self)


class FileWidget(QtGui.QWidget):
    fileChanged = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self, mainWindow, parent=None):
        super(FileWidget, self).__init__(parent)
        self.mainWindow = mainWindow
        self.setupUi()

    def setupUi(self):
        self.btn = QtGui.QPushButton('Select File', self)
        self.btn.clicked.connect(self.showDialog)
        dirIcon = self.style().standardIcon(self.style().SP_DirIcon)
        self.btn.setIcon(dirIcon)

        self.label = QtGui.QLabel('No file selected', self)
        self.label.move(120, 8)

        def onFileChanged(filename):
            self.label.setText(filename)
            self.label.adjustSize()

        self.fileChanged.connect(onFileChanged)

    def showDialog(self):
        self.mainWindow.videoWidget.pause()
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Select video file', '.', "avi, mp4 (*.avi *.mp4)")
        self.mainWindow.videoWidget.play()
        if not fname.isEmpty():
            self.fname = fname
            self.fileChanged.emit(self.fname)


class VideoWidget(QtGui.QWidget):
    def __init__(self, mainWindow, parent=None):
        super(VideoWidget, self).__init__(parent)
        self.mainWindow = mainWindow
        self.setupUi()

    def setupUi(self):
        self.videoScreen = VideoScreen(self, self)

        self.fileWidget = FileWidget(self.mainWindow, self)
        self.fileWidget.setGeometry(QtCore.QRect(20, 490, 600, 100))
        self.fileWidget.setObjectName(_fromUtf8("fileWidget"))

        self.playAction = QtGui.QAction(
            self.style().standardIcon(QtGui.QStyle.SP_MediaPlay), "Play",
            self, shortcut="Ctrl+P", enabled=False)

        self.pauseAction = QtGui.QAction(
            self.style().standardIcon(QtGui.QStyle.SP_MediaPause), "Pause",
            self, shortcut="Ctrl+A", enabled=False)

        self.stopAction = QtGui.QAction(
            self.style().standardIcon(QtGui.QStyle.SP_MediaStop), "Stop",
            self, shortcut="Ctrl+S", enabled=False)

        self.bar = QtGui.QToolBar(self)
        self.bar.addAction(self.playAction)
        self.bar.addAction(self.pauseAction)
        self.bar.addAction(self.stopAction)
        self.bar.setGeometry(QtCore.QRect(20, 535, 600, 35))

        self.fileWidget.fileChanged.connect(self.onFileChanged)

        QtCore.QMetaObject.connectSlotsByName(self)

    def onFileChanged(self, filename):
        self.videoScreen.setSource(str(filename))

    def pause(self):
        self.videoScreen.pause()

    def play(self):
        self.videoScreen.play()

    def onStateChanged(self, newState, oldState=None):
        if newState == Phonon.ErrorState:
            if self.mediaObject.errorType() == Phonon.FatalError:
                QtGui.QMessageBox.warning(self, "Fatal Error",
                        self.mediaObject.errorString())
            else:
                QtGui.QMessageBox.warning(self, "Error",
                        self.mediaObject.errorString())

        elif newState == Phonon.PlayingState:
            self.playAction.setEnabled(False)
            self.pauseAction.setEnabled(True)
            self.stopAction.setEnabled(True)

        elif newState == Phonon.StoppedState:
            self.stopAction.setEnabled(False)
            self.playAction.setEnabled(True)
            self.pauseAction.setEnabled(False)

        elif newState == Phonon.PausedState:
            self.pauseAction.setEnabled(False)
            self.stopAction.setEnabled(True)
            self.playAction.setEnabled(True)


class VideoScreen(QtGui.QWidget):
    newFrame = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, mainWindow, parent=None):
        super(VideoScreen, self).__init__(parent)
        self.mainWindow = mainWindow

        self.frame = None

        self.videoStream = VideoStream(mirrored=False)
        self.videoStream.newFrame.connect(self.onNewFrame)

        w, h = self.videoStream.frameSize
        if not w: w = 640
        if not h: h = 480

        self.setMinimumSize(w, h)
        self.setMaximumSize(w, h)

    def setSource(self, source):
        self.videoStream.setSource(source)
        self.videoStream.mirrored = False

    def frame2QImage(self, frame):
        height, width=frame.shape[:2]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return QtGui.QImage(frame, width, height, QtGui.QImage.Format_RGB888)

    @QtCore.pyqtSlot(np.ndarray)
    def onNewFrame(self, frame):
        self.frame = frame
        self.newFrame.emit(self.frame)
        self.update()

    def changeEvent(self, e):
        if e.type() == QtCore.QEvent.EnabledChange:
            if self.isEnabled():
                self.videoStream.newFrame.connect(self.onNewFrame)
            else:
                self.videoStream.newFrame.disconnect(self.onNewFrame)

    def paintEvent(self, e):
        if self.frame is None: return

        painter = QtGui.QPainter(self)
        painter.drawImage(QtCore.QPoint(0, 0), self.frame2QImage(self.frame))

    @property
    def frameSize(self):
        return self.videoStream.frameSize

    def pause(self):
        self.videoStream.paused = True

    def play(self):
        self.videoStream.paused = False
