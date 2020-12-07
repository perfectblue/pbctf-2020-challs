#!/usr/bin/python3 -u

from Crypto.Hash import SHA256
import struct
import base64
import random
import sys

n = 303111819233903650638787601663617221623
e = 17

def check_license_signature(license_buf):
    m_lo, m_hi = struct.unpack('<QQ', license_buf[0:16])
    m = m_lo | (m_hi << 64)
    m *= 0x7287472427975c62eb7fd64e061c1a3d
    m &= 0xffffffffffffffffffffffffffffffff
    c = pow(m,e,n)
    buf = struct.pack('<QQ', c & 0xffffffffffffffff, (c>>64)&0xffffffffffffffff)

    h = SHA256.new()
    h.update(license_buf[16:])
    h = h.digest()[:16]

    return h == buf

def parse_license(license_buf):
    if len(license_buf) < 84 or len(license_buf) > 1024:
        return None, None, None
    if not check_license_signature(license_buf):
        return None, None, None
    license_id, license_name = license_buf[16:48], license_buf[48:80]
    if (not b'\x00' in license_id) or (not b'\x00' in license_name):
        return None, None, None
    license_id = license_id[:license_id.index(b'\x00')].decode('ascii')
    license_name = license_name[:license_name.index(b'\x00')].decode('ascii')
    license_count = struct.unpack('<I', license_buf[80:84])
    return license_id, license_name, license_count

def safe_parse_license(license_buf):
    try:
        return parse_license(license_buf)
    except:
        return None, None, None

flag = open('flag.txt', 'r').read()

def random_id():
    d = lambda: random.randint(0,9)
    return '%d%d%d%d-%d%d%d%d-%d%d%d%d%d%d%d%d-%d%d%d%d' % (d(),d(),d(),d(),d(),d(),d(),d(),d(),d(),d(),d(),d(),d(),d(),d(),d(),d(),d(),d(),)

def random_user():
    return random.choice(['Doskey Lee', 'Jiang Ying', 'Octavian Dima', 'Zhou Tao', 'Rico Baumgart', 'Giancarlo Russo'])

def doit():
    desired_id = random_id()
    desired_user = random_user()
    print ('Please generate me a license for %s with license id %s.' % (desired_user, desired_id))
    print ('Send your license as base64 followed with \\n')
    lic = base64.b64decode(sys.stdin.readline())
    lic_id, lic_name, lic_count = parse_license(lic)
    if not lic_id:
        print ('That license is invalid!')
        exit()
    if lic_id != desired_id or lic_name != desired_user:
        print ("That's not what asked for!")
        exit()
    print('Great, that works.')

def main():
    for i in range(100):
        doit()
    print ('Great job. Here is the flag')
    print (flag)
    print()

main()
