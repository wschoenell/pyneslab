import socket

__author__ = 'william'

from pyneslab.protocol import run_command, command_list, read_analog_values
import serial
import threading
import os 
import time


class NeslabChiller(object):

    def __init__(self, port, mode='RS232'):

        self._debugLog = None
        try:
            self._debugLog = open(
                os.path.join("./", "chiller-debug.log"), "a")
        except IOError, e:
            self.log.warning("Could not create chiller debug file (%s)" % str(e))

        if ':' in port:
            self.mode = 'tcp'
            self.open_tcp(port)
        else:
            self.mode = 'serial'
            self.open_rs232(port)

    def open_tcp(self, port):
        ip, port = port.split(':')
        print ip, port

        try:
            self._serial = socket.socket()
            self._serial.connect((ip, int(port)))
            self._serial.settimeout(10)
            time.sleep(1)
            self.read_temperature()
            # self._serial.recv(100)
        except socket.error, e:
            raise e


    def open_rs232(self, port):
        # Open Serial port. Baud, parity, stop bits and bytesize are the standard.
        self._serial = serial.Serial(port=port, baudrate=9600, parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,
                                     timeout=1)

    def turn_on(self):
        self._write(run_command('set_onoff_array', d1='\x01'))

    def turn_off(self):
        self._write(run_command('set_onoff_array', d1='\x00'))

    def req_display_msg(self):
        self._write(run_command('req_display_msg'))

    def request_status(self):
        return self.run('req_status')

    def run(self, command):
        self._write(run_command(command))
        response = self._read()
        time.sleep(0.1)
        if self.mode == 'tcp':
            response = self._read()
            response = self._read()
        return response

    def read_temperature(self):
        temperatures = ['req_temp1'] #, 'req_temp2']
        results = {}
        for i in temperatures:
            comm = run_command(i)
            self._write(comm)
            n_bytes, unit, prec, data = read_analog_values(self._read(flush = False))
            temperature = float(prec)*float(data)
            results[command_list[i][0]] = [temperature, unit]
        return results

    def read_pressure(self):
        pressures = []
        for i in range(1,7):
            analog = 'req_analog' + str(i)
            pressures.append(analog)
        results = {}
        for i in pressures:
            comm = run_command(i)
            self._write(comm)
            n_bytes, unit, prec, data = read_analog_values(self._read(flush = False))
            press = float(prec)*float(data)
            results[command_list[i][0]] = [press, unit]
        return results





    #Low Level
    def _write(self, data, flush=True):
        if self.mode == 'serial':
            if not self._serial.isOpen():
                raise IOError("Device not open")

            if flush:
                self._serial.flushOutput()
            self._serial.write(data)
        else:
            self._serial.send(data)

        self._debug("[write] %s" % repr(data))

        return

    def _read(self, flush=True):

        if self.mode == 'serial':
            if not self._serial.isOpen():
                raise IOError("Device not open")

            if flush:
                self._serial.flushInput()

            ret = self._serial.readline()
        else:
            ret = self._serial.recv(1024)
        self._debug("[read ] %s" % repr(ret))
        return ret

    def _debug(self, msg):
        if self._debugLog:
            print >> self._debugLog, time.time(), threading.currentThread().getName(), msg
            self._debugLog.flush()


if __name__ == '__main__':
    # n = NeslabChiller('192.168.20.101:2001')
    n = NeslabChiller('COM1')
    print n.read_temperature()
    # print n.read_temperature()
    time.sleep(1)
    print n.read_temperature()
    # a = n.run('req_temp1')
    # print [ord(c) for c in a]
    # n._serial.close()
    # n.
