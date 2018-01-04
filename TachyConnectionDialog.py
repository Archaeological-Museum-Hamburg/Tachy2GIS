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
import serial
import serial.tools.list_ports as list_ports
from TachyReader import TachyReader
from PyQt4.Qt import QMessageBox
from dateutil import parser as dateTimeParser

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'TachyConnectionDialog.ui'))


class TachyConnectionDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(TachyConnectionDialog, self).__init__(parent)
        self.setupUi(self)

        self.availablePorts = list_ports.comports()
        portNames = [port.device for port in self.availablePorts]
        self.portComboBox.addItems(portNames)
        self.tachyReader = TachyReader(self.portComboBox.currentText(), 9600, parent=parent)
        self.pollingThread = QThread()
        self.connectButton.clicked.connect(self.connectSerial)

    def connectSerial(self):
        port = self.portComboBox.currentText()
        self.tachyReader = TachyReader(port, 9600)
        self.tachyReader.moveToThread(self.pollingThread)
        self.pollingThread.start()
        self.tachyReader.lineReceived.connect(self.displayReceived)
        self.tachyReader.beginListening()
        self.monitor.append('Connected')

    @pyqtSlot(str)
    def displayReceived(self, line):
        self.monitor.append(line)

