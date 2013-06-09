# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from camera import CameraWidget

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


class WindowUI(object):
    def setup(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 600)

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        MainWindow.setCentralWidget(self.centralwidget)

        self.cameraWidget = CameraWidget(MainWindow, self.centralwidget)

        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))

        self.colorpicker = ColorPicker(MainWindow, self.centralwidget)
        self.colorpicker.setObjectName(_fromUtf8("colorpicker"))
        self.horizontalLayout.addWidget(self.colorpicker)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 666, 29))
        self.menubar.setObjectName(_fromUtf8("menubar"))

        MainWindow.setMenuBar(self.menubar)

        self.retranslate(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslate(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))


class ColorPicker(QtGui.QWidget):
    def __init__(self, mainWindow, parent=None):
        super(ColorPicker, self).__init__(parent)
        self.mainWindow = mainWindow
        self.initUI()

    def initUI(self):
        self.color = QtGui.QColor(200, 100, 50)

        self.btn = QtGui.QPushButton('Dialog', self)
        self.btn.move(20, 20)

        self.btn.clicked.connect(self.showDialog)

        self.frm = QtGui.QFrame(self)
        self.frm.setStyleSheet("QWidget { background-color: %s }" % self.color.name())
        self.frm.setGeometry(130, 22, 100, 100)

        self.setGeometry(300, 300, 250, 180)
        self.setWindowTitle('Color dialog')
        self.show()

    def showDialog(self):
        self.color = QtGui.QColorDialog.getColor()

        if self.color.isValid():
            self.frm.setStyleSheet("QWidget { background-color: %s }" % self.color.name())

        self.mainWindow.color_changed.emit(self.color)
