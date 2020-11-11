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

from .FieldDialog_base import Ui_Targetselection
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
import os
from PyQt5.Qt import QMessageBox
from dateutil import parser as dateTimeParser


class FieldDialog(Ui_Targetselection):
    ## This constant is used to map field data types to python data types.
    #  As demonstrated by the dateTimeParser, this can be any function that
    #  takes a single argument.
    TYPE_MAP = {2:int,
                4:int,
                6:float,
                10:str,
                14:dateTimeParser.parse}

    def __init__(self, layer, parent=None):
        """Constructor."""
        Ui_Targetselection.__init__(self, parent=parent)
        #QDialog.__init__(self)
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

    ## This function maps pyshp data types to python data types.
    @staticmethod
    def fieldTypeFromShapefile(fieldMetadata):
        # the way pyshp handles field types is (roughly) described here:
        # https://github.com/GeospatialPython/pyshp#reading-shapefile-meta-data
        baseType = fieldMetadata[1]
        decimalPrecision = fieldMetadata[3]
        if baseType in ('N', 'F'):
            # these are numbers, ints have zero decimal places
            if decimalPrecision == 0:
                return int
            else:
                return float
        # Strings are called 'C':
        if baseType == 'C':
            return str
        if baseType == 'D':
            return dateTimeParser.parse
        if baseType == 'L':
            return bool
        # An exception is thrown if an unknown type pops up
        raise ValueError('Unknown data type: ' + baseType)


    def layerChanged(self):
        if QtGui is None:
            return
        self.layer = self.targetLayerComboBox.currentLayer()
        self.populateFieldTable()
    
    def populateFieldTable(self): 
        if self.layer is None:
            return
        else:
            return
        dataUri = self.layer.dataProvider().dataSourceUri()
        shapefileName = os.path.splitext(dataUri.split('|')[0])[0]
        sf = shapefile.Reader(shapefileName)
        fields = sf.fields
        # shapefiles have at least one field, the so called 'deletion flag' if only this is present, the file has to be
        # considered having no attributes at all
        if len(fields) > 1:
            fields = fields[1:]

        else:
            pass
        self.fieldTable.setColumnCount(2)
        self.fieldTable.setRowCount(len(fields))
        # The first column is populated with the names of the fields and set to 'not editable' 
        for row, field in enumerate(fields):
            item = QtWidgets.QTableWidgetItem(field[0])
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.fieldTable.setItem(row, 0, item)
            self.fieldTable.setItem(row, 1, None)
        # QGIS gives field data types as integers. The TYPE_MAP translates these
        # to python types
        self.fieldTypes = [FieldDialog.fieldTypeFromShapefile(field) for field in fields]
        # If there are features in the layer, the records of the last one are 
        # used as default values to populate the second column

        if len(sf.records()) > 0:
            features = [feature for feature in self.layer.getFeatures()]
            lastFeature = features[-1]
            for row, attribute in enumerate(lastFeature.attributes()):
                self.fieldTypes.append(type(attribute))
                self.fieldTable.setItem(row, 1, QtWidgets.QTableWidgetItem(str(attribute)))

        self.setFixedSize(self.verticalLayout.sizeHint())
    
    ## Checks if entered values can be cast to the required data type and does
    #  so when possible. This is necessary because cell contents in a 
    #  QTableWidget are converted to string for displaying.
    def validateFields(self):
        fieldNames = [self.fieldTable.item(row, 0).data(Qt.DisplayRole) for row in range(self.fieldTable.rowCount())]
        fieldItems = [self.fieldTable.item(row, 1) for row in range(self.fieldTable.rowCount())]
        fieldData = [item.data(Qt.EditRole) for item in fieldItems]
        self.fieldData = []
        fields = list(zip(fieldNames, self.fieldTypes, fieldData))
        
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
