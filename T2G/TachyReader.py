
# -*- coding=utf-8 -*-


from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

import datetime
from . import gc_constants as gc
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer
from qgis.core import QgsMessageLog
from .geo_com import GeoCOMRequest, GeoCOMMessageQueue, GeoCOMReply, GeoCOMPing

GEOCOM_RESPONSE_IDENTIFIER = "%R1P"


class TachyReader(QObject):
    lineReceived = pyqtSignal(str)
    geo_com_received = pyqtSignal(str)
    pollingInterval = 1000

    def __init__(self, baudRate, parent=None):
        super(self.__class__, self).__init__(parent)
        self.pollingTimer = QTimer()
        self.pollingTimer.timeout.connect(self.poll)
        self.ser = QSerialPort()
        self.ser.setBaudRate(baudRate)
        self.hasLogFile = False
        self.logFileName = ''

    def hook_up(self):
        port_names = [port.portName() for port in QSerialPortInfo.availablePorts()]
        beep = GeoCOMRequest(gc.BMM_BeepAlarm)
        for port_name in port_names:
            geo_ping = GeoCOMPing(port_name, beep, 1200)
            geo_ping.found_tachy.connect(self.setPort)
            geo_ping.exec()

    def poll(self):
        if self.ser.canReadLine():
            line = bytes(self.ser.readLine())
            line_string = line.decode('ascii')
            if line_string.startswith(GEOCOM_RESPONSE_IDENTIFIER):
                self.geo_com_received.emit(line_string)
            else:
                self.lineReceived.emit(line_string)
            if self.hasLogFile:
                timeStamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(self.logFileName, 'a') as logFile:
                    logFile.write(timeStamp + '\t' + line_string)
        else:
            pass

    def setLogfile(self, logFileName):
        self.hasLogFile = True
        self.logFileName = logFileName

    @pyqtSlot()
    def beginListening(self):
        self.pollingTimer.start(self.pollingInterval)

    @pyqtSlot(str)
    def setPort(self, portName):
        self.ser.close()
        self.ser.setPortName(portName)
        self.ser.open(QSerialPort.ReadWrite)
        QgsMessageLog.logMessage("Connection established: " + portName)

    @pyqtSlot()
    def shutDown(self):
        if self.ser.isOpen():
            self.ser.close()
        self.pollingTimer.stop()
