
# -*- coding=utf-8 -*-


from PyQt5.QtSerialPort import QSerialPort

import datetime
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer


class TachyReader(QObject):
    lineReceived = pyqtSignal(str)
    pollingInterval = 1000
    def __init__(self, baudRate, parent=None):
        super(self.__class__, self).__init__(parent)
        self.pollingTimer = QTimer()
        self.pollingTimer.timeout.connect(self.poll)
        self.ser = QSerialPort()
        self.ser.setBaudRate(baudRate)
        self.ser.readyRead.connect(self.incoming)
        self.hasLogFile = False
        self.logFileName = ''

    @pyqtSlot()
    def incoming(self):
        print('INCOMING')
        pass

    def poll(self):
        if self.ser.canReadLine():
            line = self.ser.readLine()
            self.lineReceived.emit(line)
            if self.hasLogFile:
                timeStamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(self.logFileName, 'a') as logFile:
                    logFile.write(timeStamp + '\t' + line)
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
        self.ser.open(QSerialPort.ReadOnly)

    @pyqtSlot()
    def shutDown(self):
        if self.ser.isOpen():
            self.ser.close()
        self.pollingTimer.stop()