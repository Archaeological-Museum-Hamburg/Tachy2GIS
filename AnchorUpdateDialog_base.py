# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AnchorUpdateDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_anchorDialog(object):
    def setupUi(self, anchorDialog):
        anchorDialog.setObjectName("anchorDialog")
        anchorDialog.resize(474, 153)
        anchorDialog.setModal(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(anchorDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.geometriesLabel = QtWidgets.QLabel(anchorDialog)
        self.geometriesLabel.setObjectName("geometriesLabel")
        self.verticalLayout.addWidget(self.geometriesLabel)
        self.geometriesBar = QtWidgets.QProgressBar(anchorDialog)
        self.geometriesBar.setProperty("value", 0)
        self.geometriesBar.setInvertedAppearance(False)
        self.geometriesBar.setObjectName("geometriesBar")
        self.verticalLayout.addWidget(self.geometriesBar)
        self.anchorLabel = QtWidgets.QLabel(anchorDialog)
        self.anchorLabel.setObjectName("anchorLabel")
        self.verticalLayout.addWidget(self.anchorLabel)
        self.anchorBar = QtWidgets.QProgressBar(anchorDialog)
        self.anchorBar.setProperty("value", 0)
        self.anchorBar.setObjectName("anchorBar")
        self.verticalLayout.addWidget(self.anchorBar)
        self.abortButton = QtWidgets.QPushButton(anchorDialog)
        self.abortButton.setAutoDefault(False)
        self.abortButton.setObjectName("abortButton")
        self.verticalLayout.addWidget(self.abortButton)

        self.retranslateUi(anchorDialog)
        QtCore.QMetaObject.connectSlotsByName(anchorDialog)

    def retranslateUi(self, anchorDialog):
        _translate = QtCore.QCoreApplication.translate
        anchorDialog.setWindowTitle(_translate("anchorDialog", "Updating Anchor Vertices"))
        self.geometriesLabel.setText(_translate("anchorDialog", "Reading geomtries in layer: "))
        self.geometriesBar.setFormat(_translate("anchorDialog", "%v / %m"))
        self.anchorLabel.setText(_translate("anchorDialog", "Extracting vertices:"))
        self.abortButton.setText(_translate("anchorDialog", "Abort"))

