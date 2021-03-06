# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AnchorUpdateDialog
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

from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import *
import os


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'AnchorUpdateDialog.ui'))

## This dialog is displayed as long as it takes the AnchorUpdater over at 
#  T2G_VertexList to extract all vertices from a layer. It also provides a way
#  to abort the process should it take too long and be working on a layer that 
#  is not of interest.
class AnchorUpdateDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(AnchorUpdateDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
 
    @pyqtSlot(int)
    def setAnchorCount(self, n):
        self.anchorBar.setMaximum(n)
    
    @pyqtSlot(int)
    def geometriesProgress(self, n):
        self.geometriesBar.setValue(n)
    
    @pyqtSlot(int)
    def anchorProgress(self, n):
        self.anchorBar.setValue(n)
    
    
    
    
