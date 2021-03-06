#!/usr/bin/env python3

from Crypto.Util.number import getStrongPrime, inverse, bytes_to_long, GCD as gcd
from Crypto.Random.random import randint
from flag import flag

p = getStrongPrime(512)
q = getStrongPrime(512)
N = p * q
phi = (p - 1) * (q - 1)

# Hehe, boi
while True:
    d = randint(int(N ** 0.399), int(N ** 0.4))
    if gcd(d, phi) == 1:
        break

e = inverse(d, phi)

# Here's a special gift. Big.
gift = d >> 120

enc = pow(bytes_to_long(flag), e, N)

print("N =", N)
print("e =", e)
print("gift =", gift)
print("enc =", enc)