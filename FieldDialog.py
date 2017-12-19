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
        self.layerLabel.setText(self.layer.name())
        self.attributeFields = []
        for row, field in enumerate(self.layer.fields()):
            fieldLabel = QtGui.QLabel(field.name())
            self.gridLayout.addWidget(fieldLabel, row, 0)
            inputField = QtGui.QLineEdit()
            self.gridLayout.addWidget(inputField, row, 1)
            self.attributeFields.append(inputField)
        features = [feature for feature in self.layer.getFeatures()]
        if features:
            lastFeature = features[-1]
            for i, attribute in enumerate(lastFeature.attributes()):
                    self.attributeFields[i].setText(str(attribute))
        
        