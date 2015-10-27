from math import ceil
import struct

__author__ = 'william'


#
#               The framing of the communications packet in both directions is:
#
# |           |                        Checksum region                            |           |
# | Lead char | Addr-MSB | Addr-LSB | Command | n d-bytes | d-byte 1 ... d-byte n | Checksum  |
# | OxCA/OxCC |          |          |         |           |                       |           |
#
# Bitwise inversion of the 1 byte sum of bytes beginning with the most significant address byte and ending with the byte
# preceding the checksum. (To perform a bitwise inversion, "exclusive OR" the one byte sum with FF hex.)
#


LEAD = {'RS232': '\xCA', 'RS485': '\xCC'}



# Commands. From manual.
command_list = {
    # REQUEST STATUS
    'req_ack': ['Protocol version v1=0; v2=1', '\x00\x00', None],
    'req_sw_ver': ['Controller SW version', '\x02\x01{d1}', None],
    'req_display_msg': ['Display message in ASCII', '\x02\x00', None],
    'req_status': ['Display message in ASCII', '\x02\x00', None],
    # REQUEST MEASUREMENTS
    'req_flow1': ['Process Fluid Flow', '\x10\x00', None],
    'req_temp1': ['Process Fluid Supply Temperature (RTD1)', '\x20\x00', None],
    'req_temp2': ['Process Fluid Return Temperature (RTD2)', '\x21\x00', None],
    'req_temp4': ['Entering Air/Facility Water (RTD4)', '\x23\x00', None],
    'req_temp7': ['ThermoFlex 2500 Air-cooled Fan Speed', '\x26\x00', None],
    'req_analog1': ['Process Fluid Supply Pressure (P2)', '\x28\x00', None],
    'req_analog2': ['Refrigeration Suction Pressure (P5)', '\x29\x00', None],
    'req_analog3': ['Process Fluid Return Pressure (P1)', '\x2A\x00', None],
    'req_analog4': ['Condensing Pressure (P6)', '\x2B\x00', None],
    'req_analog5': ['Facility Inlet Pressure (P7)', '\x1C\x00', None],
    'req_analog6': ['Facility Outlet Pressure (P8)', '\x1D\x00', None],
    'req_analog7': ['Analog Level (LEV4)', '\x1E\x00', None],
    'req_analog9': ['+5V Sense', '\x2F\x00', None],
    'req_remote_rtd': ['Remote Temperature from Optional Analog Board', '\x1B\x00', None],
    'req_res1': ['Process Fluid Resistivity', '\x2C\x00', None],
    # REQUEST LOW ALARM VALUES
    'req_lo_flow1': ['Process Warning', '\x30\x00', None],
    'req_lo_flow3': ['Process Fault', '\x32\x00', None],
    'req_lo_analog1': ['Pressure Process Supply Warning', '\x48\x00', None],
    'req_lo_analog2': ['Pressure Process Supply Fault', '\x49\x00', None],
    'req_lo_analog7': ['Level Warning', '\x3E\x00', None],
    'req_lo_analog8': ['Level Fault', '\x3F\x00', None],
    'req_lo_temp1': ['Process Warning', '\x40\x00', None],
    'req_lo_temp2': ['Process Fault', '\x41\x00', None],
    'req_autorefill_on': ['Auto Refill ON Setting', '\x45\x00', None],
    'req_lo_res1': ['Process Warning', '\x4C\x00', None],
    # REQUEST HIGH ALARM VALUES
    'req_high_flow1': ['Process Warning', '\x50\x00', None],
    'req_high_flow3': ['Process Fault', '\x32\x00', None],  # TODO: Check why equals LOW
    'req_high_temp1': ['Process Warning', '\x60\x00', None],
    'req_high_temp2': ['Process Fault', '\x61\x00', None],
    'req_high_analog1': ['Pressure Process Supply Warning', '\x68\x00', None],
    'req_high_analog2': ['Pressure Process Supply Fault', '\x69\x00', None],
    'req_high_analog7': ['Level Warning', '\x5E\x00', None],
    'req_high_analog8': ['Level Fault', '\x5F\x00', None],
    'req_autorefill_off': ['Auto Refill OFF Setting', '\x65\x00', None],
    'req_high_res1': ['Process Warning', '\x6C\x00', None],
    # REQUEST PID SETTINGS
    'req_setp1': ['Process Fluid Setpoint', '\x70\x00', None],
    'req_cool_p': ['P', '\x74\x00', None],  # FIXME: Better descriptions
    'req_cool_i': ['I', '\x75\x00', None],
    'req_cool_d': ['D', '\x76\x00', None],
    # TODO: Heating commands. Mine does not haves heating option.
    # SET STATUS SETTINGS
    'set_keystroke': ['Set Keystroke', '\x80\x01{d1}', None],
    'set_onoff_array': ['Set ON/OFF array', '\x81\x01{d1}', None],  # d1: \x01 turn ON, \x00 - OFF, \x02 - no change
    # SET LOW ALARM VALUES
    'set_lo_flow1': ['Process Warning', '\xB0\x02{d1}{d2}', None],
    'set_lo_flow3': ['Process Fault', '\xB2\x02{d1}{d2}', None],
    'set_lo_temp1': ['Process Warning', '\xC0\x02{d1}{d2}', None],
    'set_lo_temp2': ['Process Fault', '\xC1\x02{d1}{d2}', None],
    'set_lo_analog1': ['Pressure Process Supply Warning', '\xC8\x02{d1}{d2}', None],
    'set_lo_analog2': ['Pressure Process Supply Fault', '\xC9\x02{d1}{d2}', None],
    'set_lo_analog7': ['Level Warning', '\xBE\x02{d1}{d2}', None],
    'set_lo_analog8': ['Level Fault', '\xBF\x02{d1}{d2}', None],
    'set_autorefill_on': ['When level % drops below this, turn on auto refill', '\xC5\x02{d1}{d2}', None],
    'set_lo_res1': ['Process Warning', '\xCC\x02{d1}{d2}', None],
    # TODO: skipped lo_res2
    # SET HIGH ALARM VALUES
    'set_hi_flow1': ['Process Warning', '\xD0\x02{d1}{d2}', None],
    'set_hi_flow3': ['Process Fault', '\xD2\x02{d1}{d2}', None],
    'set_hi_temp1': ['Process Warning', '\xE0\x02{d1}{d2}', None],
    'set_hi_temp2': ['Process Fault', '\xE1\x02{d1}{d2}', None],
    'set_hi_analog1': ['Pressure Process Supply Warning', '\xE8\x02{d1}{d2}', None],
    'set_hi_analog2': ['Pressure Process Supply Fault', '\xE9\x02{d1}{d2}', None],
    'set_hi_analog7': ['Level Warning', '\xDE\x02{d1}{d2}', None],
    'set_hi_analog8': ['Level Fault', '\xDF\x02{d1}{d2}', None],
    'set_hi_res1': ['Process Warning', '\xEC\x02{d1}{d2}', None],
    # TODO: skipped hi_res2
    # SET PID SETTINGS
    'set_setp1': ['Process Fluid Setpoint', '\xF0\x02{d1}{d2}', None],
    'set_cool_p': ['Cool P Term', '\xF4\x02{d1}{d2}', None],
    'set_cool_i': ['Cool I Term', '\xF5\x02{d1}{d2}', None],
    'set_cool_d': ['Cool D Term', '\xF6\x02{d1}{d2}', None],
    # TODO: skipped heat
}

unit_list = {'0': 'None',
             '1': 'deg_C',
             '2': 'deg_F',
             '3': 'liters_per_minute',
             '4': 'gallons_per_minute',
             '5': 'seconds',
             '6': 'psi',
             '7': 'bar',
             '8': 'MegaOhm_per_cm',  # TODO: Check if this is the correct resistivity
             '9': 'percent',
             '10': 'volts',
             '11': 'KiloPascal',
             '12': 'mu_s_per_cm'  # FIXME: Conductivity
             }

request_status_list = {
    'd1': {'\xb0': 'Chiller Running',
           '\xb1': 'Chiller Faulted',
           '\xb2': 'Process Supply RTD open or shorted',
           '\xb3': 'Process Return RTD open or shorted',
           '\xb4': 'Suction RTD open or shorted',
           '\xb5': 'Entering Air or Facility Water RTD open or shorted',
           '\xb6': 'High Temp Error',
           '\xb7': 'Low Temp Error'},
    'd2': {'\xb0': 'High Pressure Error',
           '\xb1': 'Low Pressure Error',
           '\xb2': 'High Flow Error (user set able)',
           '\xb3': 'Low Flow Error (user set able)',
           '\xb4': 'High Flow Error (user set able)',
           '\xb5': 'Low Level Error',
           '\xb6': 'Drip Pan fault',
           '\xb7': 'Auto Refill fault'},
    'd3': {'\xb0': 'HTC (High Temperature Cutout)',
           '\xb1': 'LLC (Low Level Cutout)',
           '\xb2': 'MOL (Motor Overload)',
           '\xb3': 'Phase Monitor',
           '\xb4': 'HPC (High Pressure Cutout)',
           '\xb5': 'LPC (Low Pressure Cutout)',
           '\xb6': 'EMO',
           '\xb7': 'External EMO'},
    'd4': {'\xb0': 'RA T_MAX (High Temperature)',
           '\xb1': 'Not used',
           '\xb2': 'Auto Refill Valve Open',
           '\xb3': 'Anti Drainback Valve Open',
           '\xb4': 'Clogged Fluid Filter Fault',
           '\xb5': 'Temp Fault Startup Bypass',
           '\xb6': 'System Low Flow',
           '\xb7': 'Not used'}
}

error_list = {'\x01': 'Bad command - not recognized by slave',
              '\x02': 'Reject value and return old setting',
              '\x03': 'Do not respond at all'
              }

set_keystroke_list = {'NULL': '\x00',
                      'ENTER': '\x01',
                      'UP_YES': '\x02',
                      'DOWN_NO': '\x03',
                      'ESC': '\x04',
                      'ON/OFF': '\x05',
                      'LEFT': '\x06',
                      'RIGHT': '\x07'
                      }


def checksum(command):
    """
    Returns the checksum of command.
    """
    s = sum(map(ord, command))
    return chr(255 + 256 * int(ceil(s / 256)) - s)


def verify_checksum(response):
    """
    Returns True if response is okay, False otherwise.
    """
    return checksum(response[1:-1]) == response[-1]


def run_command(command, interface="RS232", a1='\x00', a2='\x01', **kwargs):
    cmd = ("%s%s%s%s" % (LEAD[interface], a1, a2, command_list[command][1])).format(**kwargs)
    return "%s%s" % (cmd, checksum(cmd[2:]))


# response translation functions...

def check_response_error(response):
    """
    Returns False if response is okay.
      Otherwise returns 'Response Checksum Error' for checksum error
      or the corresponding error number with error string from error_list.
    """
    if not verify_checksum(response):
        return 'Response Checksum Error'
    if response[3:5] == '\x0F\x02':
        return '%s (Error Code: %i)' % (error_list[response[5]], ord(response[6]))
    return False


def read_ack(response):
    """
    Return True if ack is okay and False otherwise.
    """
    if verify_checksum(response) and response[3:7] == '\x00\x02\x00\x01':
        return True
    return False


def read_analog_values(response):
    """
    When the controller sends a value, a qualifier byte is sent first, followed by a 2 or 4 byte integer
    (the least significant byte is sent last). The qualifier indicates the precision and units of the value.
    The host does not send the qualifier byte; it must send the value using the correct precision, units and
    number of bytes. The host first inquires about a value it wants to change, then uses the number of data bytes
    and the qualifier byte it receives to generate the proper integer to send.

    :returns data, unit, precision
    """
    n_bytes = ord(response[4])
    unit = unit_list[str((ord(response[5]) & 0b11110000) >> 4)]
    precision = 10 ** -(ord(response[5]) & 0b00001111)
    data = struct.unpack('H', '%s%s' % (response[7], response[6]))[0]
    return n_bytes, unit, precision, data