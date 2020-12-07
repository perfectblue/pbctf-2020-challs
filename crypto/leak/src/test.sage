from ecdsa import SECP256k1
from ecdsa.ecdsa import Public_key, Private_key
from Crypto.Util.number import *
import random

g = SECP256k1.generator
order = int(SECP256k1.order)
secret = random.randrange(2, order - 1)
pubkey = Public_key(g, g * secret)
privkey = Private_key(pubkey, secret)

arr = []
for i in range(30):
    h = random.randrange(2, order - 1)
    k = random.randrange(2, order - 1)
    sig = privkey.sign(h, k)
    arr.append((h, k, sig))

mat = [[0 for i in range(62)] for j in range(62)]

for i in range(30):
    h = arr[i][0]
    k = arr[i][1]
    k_p = ((k >> 40) & ((1 << 176) - 1)) << 40
    s = int(arr[i][2].s)
    r = int(arr[i][2].r)

    print(k & 0xFFFFFFFFFF)

    mat[i][i] = order
    mat[30][i] = inverse_mod(s, order) * r % order
    mat[31][i] = (k_p - inverse_mod(s, order) * h) % order
    mat[32 + i][i] = 2 ** 216
    mat[32 + i][32 + i] = 1

mat[30][30] = 2**40 / order
mat[31][31] = 2**40

mat = Matrix(mat)
mat = mat.LLL()

for i in range(5):
    flag = True
    for j in range(30):
        if mat[i][j] != 0:
            flag = False
            break

    # if flag:
    print(mat[i])
