
# -*- coding=utf-8 -*-


from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

import datetime

from .GSI_Parser import GSIPing
from . import gc_constants as gc
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer, QThread
from qgis.core import QgsMessageLog
from .geo_com import GeoCOMRequest, GeoCOMMessageQueue, GeoCOMReply, GeoCOMPing
from . import gc_constants

GEOCOM_RESPONSE_IDENTIFIER = "%R1P"

SERIAL_AVAILABLE = '🔌'      # Emoji 'electric plug', maybe cannot be displayed
NO_SERIAL_AVAILABLE = '⚠️'


# TODO: Error when T2G is closed and opened again - No Error with class TachyReader
class AvailabilityWatchdog(QThread):
    serial_available = pyqtSignal(str)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.pollingTimer = QTimer()
        self.pollingTimer.timeout.connect(self.poll)
        super().__init__()

    def start(self):
        self.pollingTimer.start(2131)

    def poll(self):
        # TODO: better way to find the right COM Port
        comManList = [i.manufacturer() for i in QSerialPortInfo.availablePorts()]
        if QSerialPortInfo.availablePorts():  # TODO: Passes if any COM Port is available
            if 'Prolific' in comManList:
                self.serial_available.emit(SERIAL_AVAILABLE)
            else:
                self.serial_available.emit(NO_SERIAL_AVAILABLE)

    def shutDown(self):
        self.pollingTimer.stop()


class TachyReader(QThread):
    lineReceived = pyqtSignal(str)
    mirror_z_received = pyqtSignal(str)
    geo_com_received = pyqtSignal(str)
    got_it = pyqtSignal(str)
    pollingInterval = 1000

    def __init__(self, baudRate, parent=None):
        super(self.__class__, self).__init__(parent)
        self.pollingTimer = QTimer()
        self.pollingTimer.timeout.connect(self.poll)
        self.ser = QSerialPort()
        self.ser.setBaudRate(baudRate)
        self.hasLogFile = False
        self.logFileName = ''
        self.queue = GeoCOMMessageQueue()
        super().__init__()

    def hook_up(self):
        port_names = [port.portName() for port in QSerialPortInfo.availablePorts()]
        print(port_names)
        beep = GeoCOMRequest(gc.BMM_BeepAlarm)
        for port_name in port_names:
            gsi_ping = GeoCOMPing(port_name, beep, 2000)
            gsi_ping.found_tachy.connect(self.setPort)
            gsi_ping.exec()

    def poll(self):
        if self.ser.canReadLine():
            line = bytes(self.ser.readLine())
            line_string = line.decode('ascii')
            # TODO: when a point is measured, two lines are passed - the second is b'w\r\n' which leads to an error
            if line_string.startswith('w'):
                return
            if line_string.startswith(GEOCOM_RESPONSE_IDENTIFIER):
                QgsMessageLog.logMessage("Received GeoCOM Message: " + line_string)
                request, reply = self.queue.handle_reply(line_string)
                if reply.ret_code == gc_constants.GRC_OK:
                    z = reply.results[0]
                    self.mirror_z_received.emit(z)
            else:
                self.lineReceived.emit(line_string)
                if self.hasLogFile:
                    timeStamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with open(self.logFileName, 'a') as logFile:
                        logFile.write(timeStamp + '\t' + line_string)
        else:
            pass
        timed_out = self.queue.check_timeouts()
        if timed_out:
            QgsMessageLog.logMessage(str(len(timed_out)) + " GeoCOM requests timed out.")

    @pyqtSlot()
    def request_mirror_z(self):
        req = GeoCOMRequest(gc_constants.TMC_GetHeight)
        self.queue.append(req)
        QgsMessageLog.logMessage("Sent: " + str(req))

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
        self.queue.set_serial(self.ser)
        QgsMessageLog.logMessage("Connection established: " + portName)
        self.got_it.emit('404')
        self.beginListening()
        # self.request_mirror_z()

    @pyqtSlot()
    def shutDown(self):
        if self.ser.isOpen():
            self.ser.close()
        self.pollingTimer.stop()
