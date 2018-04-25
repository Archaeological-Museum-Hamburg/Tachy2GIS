# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FieldDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from qgis.gui import QgsMapLayerComboBox

class Ui_Targetselection(QtWidgets.QDialog):
    def setupUi(self, Targetselection):
        Targetselection.setObjectName("Targetselection")
        Targetselection.resize(438, 328)
        Targetselection.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(Targetselection)
        self.verticalLayout.setObjectName("verticalLayout")
        self.layerLabel = QtWidgets.QLabel(Targetselection)
        self.layerLabel.setObjectName("layerLabel")
        self.verticalLayout.addWidget(self.layerLabel)
        self.targetLayerComboBox = QgsMapLayerComboBox(Targetselection)
        self.targetLayerComboBox.setObjectName("targetLayerComboBox")
        self.verticalLayout.addWidget(self.targetLayerComboBox)
        self.fieldTable = QtWidgets.QTableWidget(Targetselection)
        self.fieldTable.setColumnCount(2)
        self.fieldTable.setObjectName("fieldTable")
        self.fieldTable.setRowCount(0)
        self.fieldTable.horizontalHeader().setVisible(False)
        self.fieldTable.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.fieldTable)
        self.buttonBox = QtWidgets.QDialogButtonBox(Targetselection)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(Targetselection)
        self.buttonBox.rejected.connect(Targetselection.reject)
        QtCore.QMetaObject.connectSlotsByName(Targetselection)

    def retranslateUi(self, Targetselection):
        _translate = QtCore.QCoreApplication.translate
        Targetselection.setWindowTitle(_translate("Targetselection", "Dialog"))
        self.layerLabel.setText(_translate("Targetselection", "Target layer:"))


