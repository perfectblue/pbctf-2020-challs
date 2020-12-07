import os
import sys
import string


class MkdirError(Exception):
    pass


def load_file(filename):
    if filename == "-":
        filename = sys.stdin.fileno()
    with open(filename, "rb") as fd:
        return fd.read()


def save_file(filename, data):
    with open(filename, "wb") as fd:
        fd.write(data)


def mkdir(dirname):
    if os.path.exists(dirname):
        return
    try:
        os.mkdir(dirname)
    except BaseException as err:
        raise MkdirError(str(err))


def rmdir(dirname):
    if dirname[-1] == os.sep:
        dirname = dirname[:-1]
    if os.path.islink(dirname):
        return  # do not clear link - we can get out of dir
    for f in os.listdir(dirname):
        if f in ('.', '..'):
            continue
        path = dirname + os.sep + f
        if os.path.isdir(path):
            rmdir(path)
        else:
            os.unlink(path)
    os.rmdir(dirname)

def decode_from_hex(text):
    text = text.decode(encoding='ascii', errors='ignore')
    only_hex_digits = "".join(c for c in text if c in string.hexdigits)
    return bytes.fromhex(only_hex_digits)


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


def degf2p8mul(text, key):
    mod = len(key)
    return bytes(gf2p8div(char, key[index % mod]) for index, char in enumerate(text))


def die(exitMessage, exitCode=1):
    print(exitMessage)
    sys.exit(exitCode)


def is_linux():
    return sys.platform.startswith("linux")


def alphanum(s):
    lst = list(s)
    for index, char in enumerate(lst):
        if char in string.ascii_letters + string.digits:
            continue
        lst[index] = char.hex()
    return "".join(lst)
