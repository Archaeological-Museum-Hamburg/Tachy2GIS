
# -*- coding=utf-8 -*-

# Bearbeiter ----------------------------------------------------------------------------------------------------------#

# MODULE-------------------------------------------------------------------------------------------------------------- #

import serial
from PyQt4.QtCore import QObject, pyqtSignal, QTimer

# WOERTERBUECHER------------------------------------------------------------------------------------------------------ #



Daten = []
attribute_lists = []
pointGeometryList = []
Zeitliste = []
Koordinaten = []

#----------------------------------------------------------------------------------------------------------------------#
# Tachymeter-Daten auslesen -------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#

class TachyReader(QObject):
    lineReceived = pyqtSignal(str)
    pollingInterval = 1000
    def __init__(self, port, baudRate, parent=None):
        super(self.__class__, self).__init__(parent)
        self.pollingTimer = QTimer()
        self.pollingTimer.timeout.connect(self.poll)
        # A measurement takes roughly two seconds. timeout is provided in seconds (polling interval in milliseconds).
        self.ser = serial.Serial(port, baudRate, timeout=0.2)
        self.buffer = ""
        self.lineBuffer = []

    def poll(self):
        if self.ser.inWaiting():
            line = self.ser.readLine()
            self.lineReceived.emit(line)

