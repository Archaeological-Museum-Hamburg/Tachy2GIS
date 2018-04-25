# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Tachy2GIS_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Tachy2GisDialogBase(object):
    def setupUi(self, Tachy2GisDialogBase):
        Tachy2GisDialogBase.setObjectName("Tachy2GisDialogBase")
        Tachy2GisDialogBase.resize(566, 491)
        self.gridLayout = QtWidgets.QGridLayout(Tachy2GisDialogBase)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.deleteVertexButton = QtWidgets.QPushButton(Tachy2GisDialogBase)
        self.deleteVertexButton.setObjectName("deleteVertexButton")
        self.horizontalLayout_2.addWidget(self.deleteVertexButton)
        self.deleteAllButton = QtWidgets.QPushButton(Tachy2GisDialogBase)
        self.deleteAllButton.setObjectName("deleteAllButton")
        self.horizontalLayout_2.addWidget(self.deleteAllButton)
        self.gridLayout.addLayout(self.horizontalLayout_2, 7, 0, 1, 1)
        self.vertexTableView = QtWidgets.QTableView(Tachy2GisDialogBase)
        self.vertexTableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.vertexTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.vertexTableView.setObjectName("vertexTableView")
        self.gridLayout.addWidget(self.vertexTableView, 6, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_3 = QtWidgets.QLabel(Tachy2GisDialogBase)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 5, 0, 1, 1)
        self.dumpButton = QtWidgets.QPushButton(Tachy2GisDialogBase)
        self.dumpButton.setMaximumSize(QtCore.QSize(80, 16777215))
        self.dumpButton.setObjectName("dumpButton")
        self.gridLayout_2.addWidget(self.dumpButton, 5, 2, 1, 1)
        self.label = QtWidgets.QLabel(Tachy2GisDialogBase)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 3, 0, 1, 1)
        self.logFileButton = QtWidgets.QPushButton(Tachy2GisDialogBase)
        self.logFileButton.setObjectName("logFileButton")
        self.gridLayout_2.addWidget(self.logFileButton, 3, 2, 1, 1)
        self.sourceLayerComboBox = QgsMapLayerComboBox(Tachy2GisDialogBase)
        self.sourceLayerComboBox.setObjectName("sourceLayerComboBox")
        self.gridLayout_2.addWidget(self.sourceLayerComboBox, 5, 1, 1, 1)
        self.logFileEdit = QtWidgets.QLineEdit(Tachy2GisDialogBase)
        self.logFileEdit.setReadOnly(True)
        self.logFileEdit.setObjectName("logFileEdit")
        self.gridLayout_2.addWidget(self.logFileEdit, 3, 1, 1, 1)
        self.gridLayout_2.setColumnStretch(1, 1)
        self.horizontalLayout.addLayout(self.gridLayout_2)
        self.gridLayout.addLayout(self.horizontalLayout, 5, 0, 1, 1)
        self.button_box = QtWidgets.QDialogButtonBox(Tachy2GisDialogBase)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")
        self.gridLayout.addWidget(self.button_box, 8, 0, 1, 1)
        self.portComboBox = QtWidgets.QComboBox(Tachy2GisDialogBase)
        self.portComboBox.setObjectName("portComboBox")
        self.gridLayout.addWidget(self.portComboBox, 0, 0, 1, 1)

        self.retranslateUi(Tachy2GisDialogBase)
        self.button_box.accepted.connect(Tachy2GisDialogBase.accept)
        self.button_box.rejected.connect(Tachy2GisDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(Tachy2GisDialogBase)

    def retranslateUi(self, Tachy2GisDialogBase):
        _translate = QtCore.QCoreApplication.translate
        Tachy2GisDialogBase.setWindowTitle(_translate("Tachy2GisDialogBase", "Tachy2GIS"))
        self.deleteVertexButton.setText(_translate("Tachy2GisDialogBase", "Delete vertex"))
        self.deleteAllButton.setText(_translate("Tachy2GisDialogBase", "Delete all"))
        self.label_3.setText(_translate("Tachy2GisDialogBase", "Source layer:"))
        self.dumpButton.setText(_translate("Tachy2GisDialogBase", "Dump"))
        self.label.setText(_translate("Tachy2GisDialogBase", "Log file:"))
        self.logFileButton.setText(_translate("Tachy2GisDialogBase", "Select"))

from qgsmaplayercombobox import QgsMapLayerComboBox
