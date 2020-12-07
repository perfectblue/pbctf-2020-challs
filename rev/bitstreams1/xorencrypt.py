#!/usr/bin/python3

from binascii import unhexlify
import sys

if len(sys.argv) != 2:
    sys.stderr.write("Usage: python3 {} <hex-key>\n".format(sys.argv[0]))
    sys.exit(1)


key = unhexlify(sys.argv[1])
k = 0

data = sys.stdin.buffer.read()
for x in data:
    sys.stdout.buffer.write(bytes([x ^ key[k]]))
    k += 1
    while k >= len(key):
        k -= len(key)


