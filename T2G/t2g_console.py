#!/usr/bin/python
import os
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 't2g_port_debug_console.ui'))

CRLF = "\r\n"

class T2GPortDebug(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(T2GPortDebug, self).__init__(parent)
        self.serial = QSerialPort()
        self.setupUi(self)

    def closeSerial(self):
        if self.serial.isOpen():
            self.serial.close()

    def setup(self):
        self.rejected.connect(self.closeSerial)
        self.connectButton.clicked.connect(self.connect)
        for i in QSerialPortInfo.availablePorts():
            self.serialBox.addItem(i.portName())
        for i in QSerialPortInfo.standardBaudRates():
            self.baudBox.addItem(str(i))
        self.baudBox.setCurrentIndex(6)
        self.sendButton.clicked.connect(self.execute)
        self.testGeoGSIButton.clicked.connect(self.testGeoGSI)
        self.serial.readyRead.connect(self.response)

    def connect(self):
        self.serial.close()
        self.serial.setPortName(self.serialBox.currentText())
        self.serial.setBaudRate(int(self.baudBox.currentText()))
        self.serial.open(QSerialPort.ReadWrite)
        if self.serial.isOpen():
            self.output.append('Connected to ' + self.serialBox.currentText())
        else:
            self.output.append('Connection failed!')

    def execute(self):
        if not self.serial.isOpen():
            self.output.append('Not connected!')
            return
        self.serial.clear()
        self.output.append("Input: " + self.inputLine.text())
        self.serial.writeData((self.inputLine.text() + CRLF).encode('ascii'))
        self.output.append("Response:")

    def response(self):
        while self.serial.canReadLine():
            self.output.append(str(self.serial.readLine()))

    def testGeoGSI(self):
        # Send geocom and gsi commands and see if there is a reply
        testGeo = "%R1Q,2011:"
        testGSI = "GET/I/WI87"
        self.serial.writeData((testGeo + CRLF).encode('ascii'))
        self.output.append("Reading reflector height:")
        self.serial.writeData((testGSI + CRLF).encode('ascii'))


def main():
    app = QApplication(sys.argv)
    dlg = T2GPortDebug()
    dlg.setup()
    dlg.show()
    app.exec_()


if __name__ == '__main__':
    main()
