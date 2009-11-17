import struct, cPickle
import socket

def checksum(source_string):
    sum = 0
    countTo = (len(source_string)/2)*2
    count = 0
    while count<countTo:
        thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
        sum = sum + thisVal
        sum = sum & 0xffffffff
        count = count + 2
    if countTo<len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff
    sum = (sum >> 16)  +  (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def assemble(dest_addr, ID, seq, data):
    my_checksum = 0
    header = struct.pack('bbHHH', 8, 0, my_checksum, ID, seq)
    pdata = cPickle.dumps(data, 2)
    my_checksum = checksum(header + pdata)
    header = struct.pack('bbHHH', 8, 0, socket.htons(my_checksum), ID, seq)
    return header + pdata

def disassemble(packet):
    icmpHeader = packet[20:28]
    ptype, code, checksum, packetID, sequence = struct.unpack('bbHHH', icmpHeader)
    if ptype == 0 and code == 0:
        return (packetID, sequence, cPickle.loads(packet[28:]))
    return (None, None, None)
