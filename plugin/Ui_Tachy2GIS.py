# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file Ui_Tachy2GIS.ui
# Created with: PyQt4 UI code generator 4.4.4
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Tachy2GIS(object):
    def setupUi(self, Tachy2GIS):
        Tachy2GIS.setObjectName("Tachy2GIS")
        Tachy2GIS.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(Tachy2GIS)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.retranslateUi(Tachy2GIS)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Tachy2GIS.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Tachy2GIS.reject)
        QtCore.QMetaObject.connectSlotsByName(Tachy2GIS)

    def retranslateUi(self, Tachy2GIS):
        Tachy2GIS.setWindowTitle(QtGui.QApplication.translate("Tachy2GIS", "Tachy2GIS", None, QtGui.QApplication.UnicodeUTF8))
