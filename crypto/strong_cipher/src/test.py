def gf2p8mul(src1, src2):
    tword = 0
    for i in range(8):
        if (src2 >> i) & 1:
            tword ^= src1 << i
    
    for i in range(14, 7, -1):
        p = 0x11B << (i - 8)
        if (tword >> i) & 1:
            tword ^= p
    
    return tword

def gf2p8pow(a, b):
    if b == 0:
        return 1
    if b == 1:
        return a
    
    t = gf2p8pow(a, b // 2)
    t = gf2p8mul(t, t)
    if b % 2 == 1:
        t = gf2p8mul(t, a)
    return t

def gf2p8div(a, b):
    b_inv = gf2p8pow(b, 2**8 - 2)
    return gf2p8mul(a, b_inv)

with open('plaintext', 'r') as f:
    plaintext = f.read().encode()

with open('key', 'rb') as f:
    key = f.read()

def enc(pt, key):
    return bytes([gf2p8mul(v, key[i % len(key)]) for i, v in enumerate(pt)])

def dec(pt, key):
    return bytes([gf2p8div(v, key[i % len(key)]) for i, v in enumerate(pt)])

with open("ciphertext", "wb") as f:
    f.write(enc(plaintext, key))
        