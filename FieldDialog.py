# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FieldDialog
                                  A QGIS plugin
 This plugin allows to create geometries directly with a connected tachymeter
                             -------------------
        begin                : 2017-11-26
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Christian Trapp
        email                : mail@christiantrapp.net
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtGui, uic
from PyQt4.QtCore import *
import os
from PyQt4.Qt import QMessageBox


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'FieldDialog.ui'))


class FieldDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, layer, parent=None):
        """Constructor."""
        super(FieldDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.layer = layer
        self.fieldTypes = []
        self.fieldData = []
        
        self.targetLayerComboBox.setLayer(self.layer)
        self.targetLayerComboBox.layerChanged.connect(self.layerChanged)
        self.buttonBox.accepted.connect(self.validateFields)
    
    def layerChanged(self):
        self.layer = self.targetLayerComboBox.currentLayer()
        self.populateFieldTable()
    
    def populateFieldTable(self): 
        fields = self.layer.fields()
        self.fieldTable.setColumnCount(2)
        self.fieldTable.setRowCount(len(fields))
        for row, field in enumerate(fields):
            item = QtGui.QTableWidgetItem(field.name())
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.fieldTable.setItem(row, 0, item)
            self.fieldTable.setItem(row, 1, None)
        
        features = [feature for feature in self.layer.getFeatures()]
        self.fieldTypes = []
        if features:
            lastFeature = features[-1]
            for row, attribute in enumerate(lastFeature.attributes()):
                self.fieldTypes.append(type(attribute))
                self.fieldTable.setItem(row, 1, QtGui.QTableWidgetItem(str(attribute)))
                    
        self.setFixedSize(self.verticalLayout.sizeHint())
        
    def validateFields(self):
        fieldNames = [self.fieldTable.item(row, 0).data(Qt.DisplayRole) for row in range(self.fieldTable.rowCount())]
        fieldItems = [self.fieldTable.item(row, 1) for row in range(self.fieldTable.rowCount())]
        fieldData = [item.data(Qt.EditRole) for item in fieldItems]
        self.fieldData = []
        fields = zip(fieldNames, self.fieldTypes, fieldData)
        
        for name, type, datum in fields:
            try:
                self.fieldData.append(type(datum))
            except ValueError:
                message = "Could not convert value for field " + name + "\nto type " + str(type)
                QMessageBox(QMessageBox.Critical,
                            "Invalid data type",
                            message,
                            QMessageBox.Ok).exec_()
                return 
        self.accept()
        
    def getFields(self):
        #self.validateFields()
        return self.fieldData
        
        
        
        
        