from . import gc_constants as gc
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtSerialPort import QSerialPort
from time import time


class GeoCOMMessage:
    PREFIX = "%R1Q"
    TERMINATOR = ""

    def __init__(self, command, *args):
        self.command = str(command)
        self.args = ','.join(map(str, args))
        self.transaction_id = 0

    def __str__(self):
        msg = ",".join((GeoCOMMessage.PREFIX, self.command))
        if self.transaction_id:
            msg = ",".join((msg, self.transaction_id))
        msg = ":".join((msg, self.args))
        msg += GeoCOMMessage.TERMINATOR
        return msg

    def bytes(self):
        return str(self).encode("ascii")

    __repr__ = __str__


class GeoCOMReply:
    PREFIX = "%R1P"

    def __init__(self, bites):
        self.msg = bites.decode('ascii')
        head, tail = self.msg.split(':')
        head = head.split(',')
        tail = tail.strip().split(',')
        self.com_code = int(head[1])
        self.transaction_id = int(head[2])
        self.ret_code = int(tail.pop(0))
        self.results = tail

    def __str__(self):
        return self.msg

    __repr__ = __str__


class GeoCOMMessageQueue:
    def __init__(self, n_slots=7):
        self.indices = list(range(1, n_slots + 1))
        self.slots = {}

    def append(self, msg, timeout=2):
        def first_free_slot():
            for i in self.indices:
                if i not in self.slots.keys():
                    return i
            return False

        slot = first_free_slot()
        if slot:
            self.slots[slot] = {"message": msg,
                                "timeout": time() + timeout}
        return slot

    def check_timeouts(self):
        over_ripes = list(filter(lambda i: i[1]['timeout'] < time(), self.slots.items()))
        messages = []
        for index, msg in over_ripes:
            messages.append((index, self.slots.pop(index)['message']))
        return messages

    def handle_reply(self, reply):
        request = self.slots.pop(reply.transaction_id)['message']
        return request, reply


@pyqtSlot(str)
def connect_beep(port_name):
    serial = QSerialPort()
    serial.setPortName(port_name)
    serial.open(QSerialPort.WriteOnly)
    message = "%R1Q," + str(gc.BMM_BeepAlarm) + ":" + gc.CRLF
    serial.writeData(message.encode('ascii'))
    serial.close()
