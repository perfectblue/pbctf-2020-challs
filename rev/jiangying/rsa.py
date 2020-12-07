import math
from Crypto.Util import number

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m

n_len = 128
e = 17

while True:
    p, q = number.getPrime(n_len//2), number.getPrime(n_len//2)
    n = p*q
    phi = (p-1)*(q-1)
    gcd, _, _ = egcd(e, phi)
    if gcd != 1:
        continue
    d = modinv(e, phi)
    break

q = 17560823292485810621
p = 17260683863472602563
n = 303111819233903650638787601663617221623
e = 17
d = 53490321041277114812464604913116260313

m = 0xBF9196FEA262D62B8A6186D415DB9D1B
print(hex(pow(m,d,n)*123456789%(2**128)))

print('q = %d' % p)
print('p = %d' % q)
print('n = %d' % n)
print('e = %d' % e)
print('d = %d' % d)

shift = n_len*2+int(math.log(n, 2))
n_inv = 2**shift // n + 1
print('n bits = %d' % n_len)
print('ring = Z_%d' % (n_len*4))
print('n^-1 = 0x%x' % n_inv)
print('n shift = %d' % shift)

print('n^-1:')
parts = []
while n_inv:
    print '0x%016x,' % (n_inv & 0xffffffffffffffff),
    n_inv >>= 64

print('\nn:')
parts = []
while n:
    print '0x%016x,' % (n & 0xffffffffffffffff),
    n >>= 64

exit()

# Correctness proof
from z3 import *
x = BitVec('x', n_len)
# solve(ForAll([x],
# 	LShR(ZeroExt(3*n_len, x)*n_inv, shift) == UDiv(ZeroExt(3*n_len, x), n)
# ))
s = Solver()
s.add(x - (n*Extract(n_len-1, 0, LShR(ZeroExt(n_len*3, x)*n_inv, shift))) != URem(x, n))
assert str(s.check()) == 'unsat'
