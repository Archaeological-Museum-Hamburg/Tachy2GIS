# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Tachy2GisDialog
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

import os
from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal

# UI_FILE_NAME = 'Tachy2GIS_dialog_base.ui'
UI_FILE_NAME = 't2g_widget.ui'

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), UI_FILE_NAME))


class Tachy2GisDialog(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(Tachy2GisDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        self.hide()
        event.ignore()
        # event.accept()
