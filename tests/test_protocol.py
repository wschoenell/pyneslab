from pyneslab.protocol import command_list, verify_checksum, run_command, read_ack, check_response_error, \
    read_analog_values

__author__ = 'william'

# Tests with the manual examples...
def test_protocol():
    for k in command_list.keys():
        print 'Testing checksum verification for command: %s' % k
        assert verify_checksum(run_command(k, d1='\x10', d2='\x20'))
    print 'Testing if ACK returns correct protocol version...'
    assert read_ack('\xca\x00\x01\x00\x02\x00\x01\xfb')
    assert not read_ack('\xca\x00\x01\x00\x02\x00\x01\xfa')
    print 'Testing if ERROR response is translated.'
    assert check_response_error(
        '\xca\x00\x01\x0f\x02\x01\x08\x33\x96\x1b') == 'Bad command - not recognized by slave (Error Code: 8)'
    assert check_response_error(
        '\xca\x00\x01\x0f\x02\x01\x08\x33\x96\x1a') == 'Response Checksum Error'
    assert check_response_error(
        '\xca\x00\x01\x0f\x02\x01\x08\x33\x96\x1a') == 'Response Checksum Error'
    print 'Testing read_analog_values...'
    assert read_analog_values('\xCA\x00\x01\x70\x03\x11\x00\xC8\xB2') == (3, 'deg_C', 0.1, 200)
    assert read_analog_values('\xCA\x00\x01\xF0\x03\x11\x00\xFA\x00') == (3, 'deg_C', 0.1, 250)
    print 'Testing examples checksums...'
    assert verify_checksum('\xCA\x00\x01\x70\x00\x8E')  # Req_setp1
    assert verify_checksum('\xCA\x00\x01\x70\x03\x11\x00\xC8\xB2')
    assert verify_checksum('\xCA\x00\x01\xF0\x02\x00\xFA\x12')
    assert verify_checksum('\xCA\x00\x01\xF0\x03\x11\x00\xFA\x00')
    print 'Testing examples commands...'
    assert run_command('req_setp1') == '\xCA\x00\x01\x70\x00\x8E'
    assert run_command('set_setp1', d1=chr(0), d2=chr(250)) == '\xCA\x00\x01\xF0\x02\x00\xFA\x12'


if __name__ == '__main__':
    test_protocol()
