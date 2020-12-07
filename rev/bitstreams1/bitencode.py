#!/usr/bin/python3

import sys

leftOver = ''
def writeBits(bit):
#    sys.stderr.write(str(bit) + '\n')
    global leftOver
    if isinstance(bit, str):
        #sys.stderr.write(bit + '\n')
        leftOver += bit;
    elif isinstance(bit, bytes):
        #sys.stderr.write(bit.decode() + '\n')
        leftOver += bit.decode()
    else:
        #sys.stderr.write(str(bit) + '\n')
        leftOver += '1' if bit else '0'

    while len(leftOver) >= 8:
        sys.stdout.buffer.write(bytes([int(leftOver[7::-1], 2)]))
        leftOver = leftOver[8::]

def flushBits():
    global leftOver
    if len(leftOver) > 0:
        leftOver += '0' * (8 - len(leftOver))
        sys.stdout.buffer.write(bytes([int(leftOver[7::-1], 2)]))
        leftOver = ''
        

data = sys.stdin.buffer.read()

#first = True
for c in data:
    bits = ''
    bitind = 0x80
#    if first:
#        first = False
#    else:
#        writeBits(c & bitind)
#        c &= bitind - 1
#        bitind >>= 1

    first = True
    while bitind != 0:
#        if first:
#            first = False
#        else:
        bits += '0'
        if c & bitind:
            bits += '1'
        bitind >>= 1
    assert len(bits) <= 16
    writeBits(bin(len(bits) - 1)[2:].zfill(4))
    writeBits(bits)
    writeBits(0)
writeBits('0000')
writeBits(1)
flushBits()

