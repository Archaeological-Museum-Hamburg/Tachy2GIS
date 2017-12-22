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
from dateutil import parser as dateTimeParser

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'FieldDialog.ui'))


class FieldDialog(QtGui.QDialog, FORM_CLASS):
    ## This constant is used to map field data types to python data types.
    #  As demonstrated by the dateTimeParser, this can be any function that
    #  takes a single argument.
    TYPE_MAP = {2:int,
                4:int,
                6:float,
                10:unicode,
                14:dateTimeParser.parse}
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
        if QtGui is None:
            return
        self.layer = self.targetLayerComboBox.currentLayer()
        self.populateFieldTable()
    
    def populateFieldTable(self): 
        if self.layer is None:
            return
        fields = self.layer.fields()
        self.fieldTable.setColumnCount(2)
        self.fieldTable.setRowCount(len(fields))
        # The first column is populated with the names of the fields and set to 'not editable' 
        for row, field in enumerate(fields):
            item = QtGui.QTableWidgetItem(field.name())
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.fieldTable.setItem(row, 0, item)
            self.fieldTable.setItem(row, 1, None)
        # QGIS gives field data types as integers. The TYPE_MAP translates these
        # to python types 
        self.fieldTypes = [self.TYPE_MAP[field.type()] for field in fields]
        # If there are features in the layer, the records of the last one are 
        # used as default values to populate the second column
        features = [feature for feature in self.layer.getFeatures()]
        if features:
            lastFeature = features[-1]
            for row, attribute in enumerate(lastFeature.attributes()):
                self.fieldTypes.append(type(attribute))
                self.fieldTable.setItem(row, 1, QtGui.QTableWidgetItem(str(attribute)))
                    
        self.setFixedSize(self.verticalLayout.sizeHint())
    
    ## Checks if entered values can be cast to the required data type and does
    #  so when possible. This is necessary because cell contents in a 
    #  QTableWidget are converted to string for displaying.
    def validateFields(self):
        fieldNames = [self.fieldTable.item(row, 0).data(Qt.DisplayRole) for row in range(self.fieldTable.rowCount())]
        fieldItems = [self.fieldTable.item(row, 1) for row in range(self.fieldTable.rowCount())]
        fieldData = [item.data(Qt.EditRole) for item in fieldItems]
        self.fieldData = []
        fields = zip(fieldNames, self.fieldTypes, fieldData)
        
        for name, dataType, datum in fields:
            try:
                self.fieldData.append(dataType(datum))
            except ValueError:
                # if a cast is impossible, the process is aborted and a message is displayed
                QMessageBox(QMessageBox.Critical,
                            "Invalid data format.",
                            "Could not convert value for field " + name + "\nusing " + str(dataType),
                            QMessageBox.Ok).exec_()
                return 
        self.accept()
    
        
        
        