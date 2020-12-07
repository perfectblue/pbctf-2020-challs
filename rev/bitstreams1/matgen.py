#!/usr/bin/python3

from binascii import unhexlify, hexlify
import numpy as np, sys, random, struct

def randcount(clamp):
    count = 1
    while random.randint(1, 5) <= 3 and count < clamp:
        count += 1
    return count

def swap_row(arr, frm, to):
    arr[[frm, to],:] = arr[[to, frm],:]

def writeMatrix(m, out):
    s = m.shape
    if len(s) != 2:
        raise ValueError('Must be 2-d matrix')
    out.write(struct.pack('<II', m.shape[0], m.shape[1]))
    for r in m:
        for c in r:
            out.write(struct.pack('<i', c))

def sint8(x):
    x = x & 2**8 - 1
    if x >= 2**7:
        x -= 2**8
    return x

def uint8(x):
    return x & (2**8 - 1)

if len(sys.argv) != 4:
    print('Usage: python3 {} <flaghex> <matrix A outfile> <matrix B outfile>'.format(sys.argv[0]))
    sys.exit(2)

x = np.array(list(map(sint8, unhexlify(sys.argv[1]))))
x.resize((x.size, 1))
a = np.random.randint(0, 2**20, (x.size, x.size))

deprows = 8
randcount(x.size) 
aa = a.copy()
aa.resize((x.size + deprows, x.size))
for i in range(deprows):
    randcount(x.size)
    aa[i + x.size] += aa[random.randint(0, x.size - 1)] * random.randint(-5,5)

for i in range(x.size * 5):
    ia = random.randint(0, x.size + deprows - 1)
    ib = random.randint(0, x.size + deprows - 1)
    if ia != ib:
        swap_row(aa, ia, ib)

f = open(sys.argv[2], 'wb')
writeMatrix(aa, f)
f.close()

bb = aa @ x
f = open(sys.argv[3], 'wb')
writeMatrix(bb, f)
f.close()
print(bb)

xx = np.linalg.solve(a, a @ x)
xx = list(map(lambda x: np.int(np.round(x[0])),xx))
print(hexlify(bytes(map(uint8, xx))).decode())
print(sys.argv[1])

