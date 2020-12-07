from pwn import *
from hashlib import sha256

STATE_VECTOR_LENGTH = 624
STATE_VECTOR_M = 397
UPPER_MASK = 0x80000000
LOWER_MASK = 0x7fffffff
TEMPERING_MASK_B = 0x9d2c5680
TEMPERING_MASK_C = 0xefc60000

PASS_SIZE = 100
EASY_LOC = 0x555555559140
PASS_LOC = 0x7fffffffc840
RAND_LOC = 0x7fffffffc8b0

class MTRand:
    def __init__(self, seed=None, mt=None, index=STATE_VECTOR_LENGTH):
        if mt == None:
            self.mt = [0] * STATE_VECTOR_LENGTH
            self.seedRand(seed)
        else:
            self.mt = list(mt)
        self.index = index

    def seedRand(self, seed):
        self.mt[0] = seed & 0xffffffff
        for i in range(1, STATE_VECTOR_LENGTH):
            self.mt[i] = (6069 * self.mt[i-1]) & 0xffffffff

    def ungenRandLong(self):
        if self.index == 0:
            self.untwist()
            self.index = STATE_VECTOR_LENGTH
        self.index -= 1
        y = self.mt[self.index]
        y ^= (y >> 11)
        y ^= (y << 7) & TEMPERING_MASK_B
        y ^= (y << 15) & TEMPERING_MASK_C
        y ^= (y >> 18)
        return y

    def twist(self):
        tmp = list(self.mt)
        for kk in range(STATE_VECTOR_LENGTH):
            n = (kk+1) % STATE_VECTOR_LENGTH
            m = (kk + STATE_VECTOR_M) % STATE_VECTOR_LENGTH
            y = (tmp[kk] & UPPER_MASK) | (tmp[n] & LOWER_MASK)
            self.mt[kk] = self.mt[m] ^ (y >> 1) ^ (0x9908b0df * (y & 0x1))

    def untwist(self):
        mt_old = list(self.mt)
        for kk in reversed(range(STATE_VECTOR_LENGTH)):
            a = (kk+1) % STATE_VECTOR_LENGTH
            b = (kk+STATE_VECTOR_M) % STATE_VECTOR_LENGTH

            if kk < STATE_VECTOR_LENGTH - STATE_VECTOR_M: mt2 = self.mt
            else: mt2 = mt_old
            k = mt_old[kk] ^ mt2[b]
            if k & UPPER_MASK:
                y = (k ^ 0x9908b0df) << 1 | 1
            else:
                y = k << 1
            self.mt[kk] = (self.mt[kk] & ~UPPER_MASK) | (y & UPPER_MASK)
            self.mt[a]  = (self.mt[a] & ~LOWER_MASK)  | (y & LOWER_MASK)

    def genRandLong(self):
        if self.index >= STATE_VECTOR_LENGTH or self.index < 0:
            if self.index >= STATE_VECTOR_LENGTH + 1 or self.index < 0:
                self.seedRand(4357)
            self.twist()
            self.index = 0
        y = self.mt[self.index]
        self.index += 1
        y ^= y >> 11
        y ^= (y << 7) & TEMPERING_MASK_B
        y ^= (y << 15) & TEMPERING_MASK_C
        y ^= y >> 18
        return y

s_mtrand = struct.Struct('<' + 'Q' * STATE_VECTOR_LENGTH + 'I')
core = ELF('./core')
ind, *mt = s_mtrand.unpack(core.read(RAND_LOC, s_mtrand.size))[::-1]
mt.reverse()

pwd = core.read(PASS_LOC, PASS_SIZE + 3)
assert pwd[:3] == b'\x00\x05\x00'
pwd = list(pwd[3:])
easy = core.read(EASY_LOC, PASS_SIZE)

rand = MTRand(mt=mt, index=ind)
ungen = [rand.ungenRandLong() for i in range(409500)]

for i in range(0xfff):
    if ind == (i * PASS_SIZE + 1) % STATE_VECTOR_LENGTH:
        if ungen[i * PASS_SIZE] & 0xfff == i:
            v = i
            break
else:
    assert(False)

gens = ungen[0:v * PASS_SIZE + 1][::-1]
print(gens[0] & 0xfff)
gens = gens[1:]

for i in range(v):
    for j in range(PASS_SIZE):
        pwd[j] ^= gens[i*100+j] & 0xff

seed = (PASS_LOC + 3) & 0xfff
rand2 = MTRand(seed)
for i in range(PASS_SIZE):
    pwd[i] ^= easy[i]
    if pwd[i] == 0: break
    pwd[i] ^= ((rand2.genRandLong() & 0xff) | 0x80)

flag = []
key = sha256(bytes(pwd)).digest()
for a, b in zip(open('flag.enc', 'rb').read(), key):
    flag.append(a ^ b)
print(flag)
print(str(bytes(flag).split(b'\0')[0], 'utf8'))
