__author__ = 'william'

import serial

class NeslabChiller(object):

    def __init__(self, port, mode='RS232'):
        self.open(port)

    def open(self, port):
        # Open Serial port. Baud, parity, stop bits and bytesize are the standard.
        self._serial = serial.Serial(port=port, baudrate=9600, parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,
                                     timeout=1)

    def request_status(self):
        # Request ACK
        return '10'