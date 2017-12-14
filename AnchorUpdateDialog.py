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

from PyQt4 import QtGui, uic
from PyQt4.QtCore import *
import os


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'AnchorUpdateDialog.ui'))


class AnchorUpdateDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(AnchorUpdateDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.aborted = False
        self.abortButton.clicked.connect(self.abortButtonClicked)
    
    def abortButtonClicked(self):
        self.aborted = True
        
    def show(self, *args, **kwargs):
        self.aborted = False
        return QtGui.QDialog.show(self, *args, **kwargs)
    
    @pyqtSlot(int)
    def setAnchorCount(self, n):
        self.anchorBar.setMaximum(n)
    
    @pyqtSlot(int)
    def geometriesProgress(self, n):
        self.geometriesBar.setValue(n)
    
    @pyqtSlot(int)
    def anchorProgress(self, n):
        self.anchorBar.setValue(n)
    
    
    
    
