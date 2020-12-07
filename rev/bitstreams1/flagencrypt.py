#!/usr/bin/python3

import sys
from binascii import hexlify

flag = b'abctf{H0w_l0w_l3vel_c4n_y0u_r3ally_go?}'

flag = flag[6:-1]

key = flag[:8]
flag = flag[8:] 

enc = b''
for i in range(len(flag)):
    enc += bytes([key[i % len(key)] ^ flag[i]])

print(hexlify(enc))

# f(i) = f(i) ^ k(i)
enc += bytes([0])
added = b''
for i in range(len(enc) - 1):
    added += bytes([enc[i] + enc[i+1]])

# f(i) = f(i) + f(i+1)
rep = ''
for x in added:
    rep += hex(x) + ' '

print(rep)

