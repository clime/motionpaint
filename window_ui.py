# -*- coding: utf-8 -*-

import numpy as np
import cv2

from PyQt4 import QtCore, QtGui
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


class MainWindow(QtGui.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def setupUi(self):
        self.setObjectName(_fromUtf8("self"))
        self.videoWidget = VideoWidget(self, self)
        self.videoWidget.setObjectName(_fromUtf8("videoWidget"))
        self.groupBox = QtGui.QGroupBox('Settings', self)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.groupBox.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        self.groupBox.setMinimumWidth(300)
        self.colorPicker = ColorPicker(self, self.groupBox)
        self.colorPicker.setObjectName(_fromUtf8("colorPicker"))
        self.alphaSetter = AlphaSetter(self, self.groupBox)
        self.alphaSetter.setObjectName(_fromUtf8("alphaSetter"))

        self.thresholdSetter = ThresholdSetter(self, self.groupBox)
        self.thresholdSetter.setObjectName(_fromUtf8("thresholdSetter"))

        self.fadingSetter = FadingSetter(self, self.groupBox)
        self.fadingSetter.setObjectName(_fromUtf8("fadingSetter"))

        self.retranslate()

        vbox_setting = QtGui.QVBoxLayout(self)
        vbox_setting.addWidget(self.colorPicker)
        vbox_setting.addWidget(self.alphaSetter)
        vbox_setting.addWidget(self.thresholdSetter)
        vbox_setting.addWidget(self.fadingSetter)
        vbox_setting.addStretch()
        self.groupBox.setLayout(vbox_setting)

        hbox = QtGui.QHBoxLayout(self)
        splitter = QtGui.QSplitter()
        splitter.addWidget(self.videoWidget)
        splitter.addWidget(self.groupBox)
        hbox.addWidget(splitter)
        self.setLayout(hbox)

    def retranslate(self):
        self.setWindowTitle(_translate("Motionpaint", "Motionpaint", None))


class ColorPicker(QtGui.QWidget):
    colorChanged = QtCore.pyqtSignal(QtGui.QColor)

    def __init__(self, mainWindow, parent=None):
        super(ColorPicker, self).__init__(parent)
        self.mainWindow = mainWindow
        self.setupUi()

    def setupUi(self):
        self.color = QtGui.QColor(255, 255, 0)
        self.label = QtGui.QLabel('Color', self)
        self.btn = QtGui.QPushButton('', self)
        self.btn.setStyleSheet("QWidget { background-color: %s }" % self.color.name())
        self.btn.clicked.connect(self.showDialog)

        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.label)
        vbox.addWidget(self.btn)

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

        self.horizontalSlider = QtGui.QSlider(self)
        self.horizontalSlider.setMaximum(100)
        self.horizontalSlider.setSingleStep(1)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName(_fromUtf8("horizontalSlider"))
        self.horizontalSlider.setValue(int(self.alpha*100))

        self.doubleSpinBox = QtGui.QDoubleSpinBox(self)
        self.doubleSpinBox.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.doubleSpinBox.setDecimals(3)
        self.doubleSpinBox.setAccelerated(True)
        self.doubleSpinBox.setMaximum(1)
        self.doubleSpinBox.setSingleStep(0.01)
        self.doubleSpinBox.setValue(self.alpha)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.horizontalSlider)
        hbox.addWidget(self.doubleSpinBox)
        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.label)
        vbox.addLayout(hbox)

        def alphaChanged(alpha):
            self.alpha = alpha
            self.horizontalSlider.setValue(int(alpha*100))
            self.alphaChanged.emit(alpha)

        QtCore.QObject.connect(self.horizontalSlider, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), lambda v: self.doubleSpinBox.setValue(v/100.0))
        QtCore.QObject.connect(self.doubleSpinBox, QtCore.SIGNAL(_fromUtf8("valueChanged(double)")), alphaChanged)


class ThresholdSetter(QtGui.QWidget):
    thresholdChanged = QtCore.pyqtSignal(int)

    def __init__(self, mainWindow, parent=None):
        super(ThresholdSetter, self).__init__(parent)
        self.mainWindow = mainWindow
        self.setupUi()

    def setupUi(self):
        self.threshold = 15

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

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.horizontalSlider)
        hbox.addWidget(self.spinBox)
        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.label)
        vbox.addLayout(hbox)

        def thresholdChanged(threshold):
            self.threshold = threshold
            self.horizontalSlider.setValue(threshold)
            self.thresholdChanged.emit(threshold)

        QtCore.QObject.connect(self.horizontalSlider, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.spinBox.setValue)
        QtCore.QObject.connect(self.spinBox, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), thresholdChanged)


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

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.horizontalSlider)
        hbox.addWidget(self.doubleSpinBox)
        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.label)
        vbox.addLayout(hbox)

        def fadingChanged(fading):
            self.fading = fading
            self.horizontalSlider.setValue(int(fading*100))
            self.fadingChanged.emit(fading)

        QtCore.QObject.connect(self.horizontalSlider, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), lambda v: self.doubleSpinBox.setValue(v/100.0))
        QtCore.QObject.connect(self.doubleSpinBox, QtCore.SIGNAL(_fromUtf8("valueChanged(double)")), fadingChanged)


class FileWidget(QtGui.QWidget):
    fileChanged = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self, mainWindow, parent=None, text='Select File', saveAs=False):
        super(FileWidget, self).__init__(parent)
        self.mainWindow = mainWindow
        self.saveAs = saveAs
        self.setupUi(text)

    def setupUi(self, text):
        self.btn = QtGui.QPushButton(text, self)
        self.btn.setStyleSheet("min-width: 100px")
        self.btn.clicked.connect(self.showDialog)
        dirIcon = self.style().standardIcon(self.style().SP_DirIcon)
        self.btn.setIcon(dirIcon)

        self.label = QtGui.QLabel('No file selected', self)

        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.btn.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        hbox = QtGui.QHBoxLayout(self)
        hbox.addWidget(self.btn)
        hbox.addWidget(self.label)

        def onFileChanged(filename):
            self.label.setText(filename)
            self.label.adjustSize()

        self.fileChanged.connect(onFileChanged)

    def showDialog(self):
        self.mainWindow.videoWidget.pause()
        if not self.saveAs:
            fname = QtGui.QFileDialog.getOpenFileName(self, 'Select video file', '.', "avi, mp4 (*.avi *.mp4)")
        else:
            fname = QtGui.QFileDialog.getSaveFileName(self, 'Create video file', '.', "mpg")
        if not fname.isEmpty():
            self.fname = fname
            self.fileChanged.emit(self.fname)
        self.mainWindow.videoWidget.play()


class VideoScreen(QtGui.QWidget):
    def __init__(self, videoStream, mainWindow, parent=None):
        super(VideoScreen, self).__init__(parent)
        self.mainWindow = mainWindow
        self.videoStream = videoStream

        self.videoStream.newFrame.connect(self.onNewFrame)
        self.videoStream.sourceChanged.connect(self.onSourceChanged)
        self.videoStream.stateChanged.connect(self.onStateChanged)

        self.frame = None

        w, h = self.videoStream.frameSize
        if not w:
            w = 640
        if not h:
            h = 480
        self.setMinimumSize(w, h)

    def frame2QImage(self, frame):
        height, width = frame.shape[:2]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return QtGui.QImage(frame, width, height, QtGui.QImage.Format_RGB888)

    @QtCore.pyqtSlot(np.ndarray)
    def onNewFrame(self, frame):
        self.frame = frame
        self.update()

    def onSourceChanged(self):
        self.frame = None

    @QtCore.pyqtSlot(int)
    def onStateChanged(self, state):
        self.update()

    def paintEvent(self, e):
        if self.frame is not None and self.videoStream.state != VideoStream.State.STOPPED:
            painter = QtGui.QPainter(self)
            painter.drawImage(QtCore.QPoint(0, 0), self.frame2QImage(self.frame))

    @property
    def size(self):
        return self.videoStream.frameSize


class VideoWidget(QtGui.QWidget):
    newFrame = QtCore.pyqtSignal(np.ndarray)
    sourceChanged = QtCore.pyqtSignal()
    stateChanged = QtCore.pyqtSignal(int)

    def __init__(self, mainWindow, parent=None):
        super(VideoWidget, self).__init__(parent)
        self.mainWindow = mainWindow

        self.videoStream = VideoStream(0)
        self.videoStream.newFrame.connect(self.onNewFrame)
        self.videoStream.sourceChanged.connect(self.onSourceChanged)
        self.videoStream.stateChanged.connect(self.onStateChanged)

        self.setupUi()

        self.setOutputNotReadyState()
        self.switchToWebCamBtn.setChecked(True)
        self.play()

    def setupUi(self):
        self.videoScreen = VideoScreen(self.videoStream, self, self)

        self.fileWidget = FileWidget(self.mainWindow, self, 'Set input')
        self.fileWidget.setObjectName(_fromUtf8("fileWidget"))
        self.fileWidget.fileChanged.connect(self.onFileChanged)
        self.switchToWebCamBtn = QtGui.QPushButton(QtGui.QIcon("webcam.png"), "", self)
        self.switchToWebCamBtn.setStyleSheet("margin-right: 7px; padding: 6px")
        self.switchToWebCamBtn.clicked.connect(self.onSwitchToWebCamBtnClicked)
        self.switchToWebCamBtn.setFlat(True)
        self.switchToWebCamBtn.setCheckable(True)

        self.spacer1 = QtGui.QWidget()
        self.spacer1.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.playAction = QtGui.QAction(
            self.style().standardIcon(QtGui.QStyle.SP_MediaPlay), "Play",
            self, shortcut="Ctrl+P", enabled=True)
        self.playAction.triggered.connect(self.play)

        self.pauseAction = QtGui.QAction(
            self.style().standardIcon(QtGui.QStyle.SP_MediaPause), "Pause",
            self, shortcut="Ctrl+A", enabled=True)
        self.pauseAction.triggered.connect(self.pause)

        self.stopAction = QtGui.QAction(
            self.style().standardIcon(QtGui.QStyle.SP_MediaStop), "Stop",
            self, shortcut="Ctrl+S", enabled=True)
        self.stopAction.triggered.connect(self.stop)

        self.bar1 = QtGui.QToolBar(self)
        self.bar1.addWidget(self.fileWidget)
        self.bar1.addWidget(self.spacer1)
        self.bar1.addAction(self.playAction)
        self.bar1.addAction(self.pauseAction)
        self.bar1.addAction(self.stopAction)
        self.bar1.addWidget(self.switchToWebCamBtn)

        self.saveAsWidget = FileWidget(self.mainWindow, self, 'Set output', True)
        self.saveAsWidget.fileChanged.connect(self.onSaveAsChanged)

        self.recordAction = QtGui.QAction(
            QtGui.QIcon("record.png"), "Record",
            self, shortcut="Ctrl+R", enabled=True)
        self.recordAction.triggered.connect(self.record)
        self.recordAction.setVisible(True)

        self.recordStopAction = QtGui.QAction(
            QtGui.QIcon("recording.png"), "Stop recording",
            self, shortcut="Ctrl+R", enabled=True)
        self.recordStopAction.triggered.connect(self.recordStop)
        self.recordStopAction.setVisible(False)

        self.spacer2 = QtGui.QWidget()
        self.spacer2.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.processBtn = QtGui.QPushButton("Process", self)
        self.processBtn.setStyleSheet("margin-right: 7px; padding: 5px; width: 140px")
        self.processBtn.clicked.connect(self.onProcessBtnClicked)

        self.bar2 = QtGui.QToolBar(self)
        self.bar2.addWidget(self.saveAsWidget)
        self.bar2.addWidget(self.spacer2)
        self.bar2.addAction(self.recordAction)
        self.bar2.addAction(self.recordStopAction)
        self.bar2.addWidget(self.processBtn)

        hbox = QtGui.QVBoxLayout(self)
        hbox.addWidget(self.videoScreen)
        hbox.addStretch()
        hbox.addWidget(self.bar1)
        hbox.addWidget(self.bar2)
        hbox.setContentsMargins(-1, -1, -1, 2)

    def onProcessBtnClicked(self):
        pass

    def onSwitchToWebCamBtnClicked(self):
        if self.switchToWebCamBtn.isChecked():
            self.videoStream.resetSource(0)
            self.play()
        else:
            self.videoStream.resetSource()

    def onFileChanged(self, filename):
        self.videoStream.resetSource(str(filename))

    def onSaveAsChanged(self, filename): # todo
        if not filename:
            self.setOutputNotReadyState()
        else:
            self.setOutputReadyState()
            self.videoStream.setOutput(str(filename))

    def pause(self):
        self.videoStream.pause()

    def play(self):
        self.videoStream.play()

    def stop(self):
        self.videoStream.stop()

    def record(self):
        self.recordAction.setVisible(False)
        self.recordStopAction.setVisible(True)
        self.videoStream.record()

    def recordStop(self):
        self.recordAction.setVisible(True)
        self.recordStopAction.setVisible(False)
        self.videoStream.recordStop()

    @QtCore.pyqtSlot(np.ndarray)
    def onNewFrame(self, frame):
        self.newFrame.emit(frame)

    def onSourceChanged(self):
        self.sourceChanged.emit()

    @QtCore.pyqtSlot(int)
    def onStateChanged(self, state):
        if state == VideoStream.State.CLOSED:
            self.setClosedState()
        elif state == VideoStream.State.STOPPED:
            self.setStoppedState()
        elif state == VideoStream.State.PAUSED:
            self.setPausedState()
        elif state == VideoStream.State.PLAYING:
            self.setPlayingState()
        self.stateChanged.emit(state)

    def setClosedState(self):
        self.playAction.setEnabled(False)
        self.pauseAction.setEnabled(False)
        self.stopAction.setEnabled(False)

    def setStoppedState(self):
        self.playAction.setEnabled(True)
        self.pauseAction.setEnabled(False)
        self.stopAction.setEnabled(False)

    def setPausedState(self):
        self.playAction.setEnabled(True)
        self.pauseAction.setEnabled(False)
        self.stopAction.setEnabled(True)

    def setPlayingState(self):
        self.playAction.setEnabled(False)
        self.pauseAction.setEnabled(True)
        self.stopAction.setEnabled(True)

    def setOutputReadyState(self):
        self.recordAction.setEnabled(True)
        self.recordStopAction.setEnabled(True)
        self.processBtn.setEnabled(True)

    def setOutputNotReadyState(self):
        self.recordAction.setEnabled(False)
        self.recordStopAction.setEnabled(False)
        self.processBtn.setEnabled(False)
