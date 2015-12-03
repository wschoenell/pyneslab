__author__ = 'william'

import serial
import threading
import os 
import time


class NeslabChiller(object):

    def __init__(self, port, mode='RS232'):
        self.open(port)

        self._debugLog = None
        try:
            self._debugLog = open(
                os.path.join("./", "chiller-debug.log"), "w")
        except IOError, e:
            self.log.warning("Could not create chiller debug file (%s)" % str(e))

    def open(self, port):
        # Open Serial port. Baud, parity, stop bits and bytesize are the standard.
        self._serial = serial.Serial(port=port, baudrate=9600, parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,
                                     timeout=1)

    def turn_on(self):
        on = run_command('set_onoff_array', d1 = '\x01')
        self._write(on)

    def turn_off(self):
        off = run_command('set_onoff_array', d1 = '\x00')
        self._write(off)

    def request_status(self):
        # Request ACK
        return '10'

    def run(self, command):
        # Enter a command from the protocol command_list
        hex_comm  = run_command(command)
        self._write(hex_comm)
        response = self._read()
        return response

    def read_temperature(self):
        temperatures = ['req_temp1', 'req_temp2']
        results = {}
        self._serial.flushInput()
        self._serial.flushOutput()
        for i in temperatures:
            comm = run_command(i)
            self._write(comm)
            n_bytes, unit, prec, data = read_analog_values(self._read(flush = False))
            temperature = float(prec)*float(data)
            results[command_list[i][0]] = [temperature, unit]
            self._serial.flushInput()
            self._serial.flushOutput()
        return results

    def read_pressure(self):
        pressures = []
        for i in range(1,7):
            analog = 'req_analog' + str(i)
            pressures.append(analog)
        results = {}
        self._serial.flushInput()
        self._serial.flushOutput()
        for i in pressures:
            comm = run_command(i)
            self._write(comm)
            n_bytes, unit, prec, data = read_analog_values(self._read(flush = False))
            press = float(prec)*float(data)
            results[command_list[i][0]] = [press, unit]
            self._serial.flushInput()
            self._serial.flushOutput()
        return results





    #Low Level
    def _write(self, data, flush=True):
        if not self._serial.isOpen():
            raise IOError("Device not open")

        if flush:
            self._serial.flushOutput()

        self._debug("[write] %s" % repr(data))

        return self._serial.write(data)

    def _read(self, n=1, flush=True):

        if not self._serial.isOpen():
            raise IOError("Device not open")

        if flush:
            self._serial.flushInput()

        ret = self._serial.readline()
        self._debug("[read ] %s" % repr(ret))
        return ret

    def _debug(self, msg):
        if self._debugLog:
            print >> self._debugLog, time.time(
            ), threading.currentThread().getName(), msg
            self._debugLog.flush()