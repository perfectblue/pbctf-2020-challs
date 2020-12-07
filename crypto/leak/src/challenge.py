#!/usr/bin/env python3

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from ecdsa import SECP256k1
from ecdsa.ecdsa import Public_key, Private_key
from flag import flag
import hashlib
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
    
    lea_k = int("0x" + "{:064x}".format(k)[10:-10], 16)

    arr.append((h, lea_k, int(sig.r), int(sig.s)))

print(arr)

sha256 = hashlib.sha256()
sha256.update(str(secret).encode())
key = sha256.digest()

aes = AES.new(key, mode=AES.MODE_ECB)
print(aes.encrypt(pad(flag, 16)).hex())