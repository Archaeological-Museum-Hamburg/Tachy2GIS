
# -*- coding=utf-8 -*-

import serial
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer
from qgis.core import QgsMessageLog


class TachyReader(QObject):
    lineReceived = pyqtSignal(str)
    pollingInterval = 1000
    def __init__(self, baudRate, parent=None):
        super(self.__class__, self).__init__(parent)
        self.pollingTimer = QTimer()
        self.pollingTimer.timeout.connect(self.poll)
        self.ser = serial.Serial()
        self.ser.baudrate = baudRate
        self.ser.timeout = 0.2

    def poll(self):
        if self.ser.isOpen() and self.ser.inWaiting():
            line = self.ser.readline()
            self.lineReceived.emit(line)
            #QgsMessageLog.logMessage(line, 'Serial', QgsMessageLog.INFO)

    @pyqtSlot()
    def beginListening(self):
        self.pollingTimer.start(self.pollingInterval)

    @pyqtSlot(str)
    def setPort(self, portName):
        self.ser.close()
        self.ser.port = portName
        self.ser.open()

    @pyqtSlot()
    def shutDown(self):
        if self.ser.isOpen():
            self.ser.close()
        self.pollingTimer.stop()