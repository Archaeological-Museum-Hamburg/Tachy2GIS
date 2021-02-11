
# -*- coding=utf-8 -*-


from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

import datetime

from .GSI_Parser import GSIPing
from . import gc_constants as gc
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer, QThread
from PyQt5.QtWidgets import QInputDialog, QWidget
from qgis.core import QgsMessageLog
from .geo_com import GeoCOMRequest, GeoCOMMessageQueue, GeoCOMReply, GeoCOMPing
from . import gc_constants

GEOCOM_RESPONSE_IDENTIFIER = "%R1P"

SERIAL_CONNECTED = '🔗'
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
        # comManList = [i.manufacturer() for i in QSerialPortInfo.availablePorts()]
        if QSerialPortInfo.availablePorts():  # TODO: Passes if any COM Port is available
            # if 'Prolific' in comManList:
            self.serial_available.emit(SERIAL_AVAILABLE)
        else:
            self.serial_available.emit(NO_SERIAL_AVAILABLE)

    def shutDown(self):
        self.pollingTimer.stop()


class TachyReader(QThread):
    serial_disconnected = pyqtSignal(str)  # start watchdoge again
    serial_connected = pyqtSignal(str, str)  # stop watchdoge if serial is successfully connected
    lineReceived = pyqtSignal(str)
    mirror_z_received = pyqtSignal()
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
        self.getRefHeight = ''
        super().__init__()

    # TODO: Hook up not working for every tachymeter with gsi_ping
    #       Hook up to right port automatically
    def hook_up(self):
        # close port if connection is established
        if self.ser.isOpen():
            self.ser.close()
            self.serial_disconnected.emit(NO_SERIAL_AVAILABLE)
            return
        port_names = [port.portName() for port in QSerialPortInfo.availablePorts()]
        print(port_names)
        beep = GeoCOMRequest(gc.BMM_BeepAlarm)
        # for port_name in port_names:
        #    gsi_ping = GeoCOMPing(port_name, beep, 2000)
        #    gsi_ping.found_tachy.connect(self.setPort)
        #    gsi_ping.exec()

        # Test - connect to Port which has Prolific in its manufacturer name
        for port in QSerialPortInfo.availablePorts():
            if "Prolific" in port.manufacturer():
                self.setPort(port.portName())
                print(f"Connected to '{port.manufacturer()}' at Port: '{port.portName()}'")
                self.serial_connected.emit(SERIAL_CONNECTED, port.portName())
                return
        print(f"'Prolific' not found in Port list: {[port.manufacturer() for port in QSerialPortInfo.availablePorts()]}")
        # Show port list and let user choose the port
        btPort, okPressed = QInputDialog.getItem(QWidget(),
                                                 "Verbinden...",
                                                 "Bluetooth oder COM Port auswählen:",
                                                 [p.portName() for p in QSerialPortInfo.availablePorts()],
                                                 0,
                                                 False)
        if not okPressed:
            return
        if self.setPort(btPort):
            print(f"Connected to '{btPort}'")
            self.serial_connected.emit(SERIAL_CONNECTED, btPort)
            return
        else:
            print(f"Could not connect to Port '{btPort}'")

    def poll(self):
        if self.ser.error() == QSerialPort.ResourceError:  # device is unexpectedly removed from the system
            self.ser.close()
            self.serial_disconnected.emit(NO_SERIAL_AVAILABLE)
        if self.ser.canReadLine():
            line = bytes(self.ser.readLine())
            line_string = line.decode('ascii')
            # TODO: when a point is measured, two lines are passed - the second is b'w\r\n' which leads to an error
            if line_string.startswith('w'):
                return
            if line_string.startswith(GEOCOM_RESPONSE_IDENTIFIER):
                QgsMessageLog.logMessage("Received GeoCOM Message: " + line_string)
                # request, reply = self.queue.handle_reply(line)
                reply = self.queue.handle_reply(line)
                if reply.ret_code == gc_constants.GRC_OK:
                    # TODO: Only sets reflector height - does not handle replies right now
                    self.getRefHeight = str(round(float(reply.results[0]), 3))
                    # z = reply.results[0]
                    self.mirror_z_received.emit()
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
        return self.ser.isWritable()

    @pyqtSlot()
    def shutDown(self):
        if self.ser.isOpen():
            self.ser.close()
            self.serial_disconnected.emit(NO_SERIAL_AVAILABLE)
        self.pollingTimer.stop()

    # TODO: crash when opening port without using the ping button
    #       Set ref height with geocom if gsi fails
    # Reflector height is getting set, but does not refresh in tachymeter when setting it with geocom
    def setReflectorHeight(self, refHeight):
        self.ser.close()
        self.ser.open(QSerialPort.ReadWrite)
        if self.ser.isOpen():
            # self.ser.writeData(("%R1Q,2012:" + str(refHeight) + gc.CRLF).encode('ascii'))
            # self.ser.writeData(("PUT/87...0+00001700 \r\n").encode('ascii'))
            gsi_height = refHeight
            if "," in gsi_height:
                gsi_height = gsi_height.replace(",", ".")
            if "." not in gsi_height:
                gsi_height += ".0"
            gsi_height = gsi_height.split('.')
            self.ser.writeData(("PUT/87...0+" + gsi_height[0].zfill(5) + "{:<03s}".format(gsi_height[1]) + " \r\n").encode('ascii'))

        else:
            # TODO: MessageBar?
            # iface.messageBar().pushMessage("", level=Qgis.Info, duration=10)
            QgsMessageLog.logMessage("Connection failed!")

    def getReflectorHeight(self):
        # self.ser.close()
        # self.ser.open(QSerialPort.ReadWrite)
        QgsMessageLog.logMessage("Pollingqgis reflector height!")
        if self.ser.isOpen():
            self.ser.writeData(("%R1Q,2011:Height\r\n").encode('ascii'))
            # response = self.ser.readLine()  # PyQt5.QtCore.QByteArray(b'%R1P,0,0:0,3.141\r\n') 3.141 = Tachy height
            # return str(bytes(response).decode('ascii').split(',')[3].strip("\r\n"))
        else:
            QgsMessageLog.logMessage("Couldn't get reflector height!")
