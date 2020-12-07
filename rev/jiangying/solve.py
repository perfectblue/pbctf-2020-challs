from pwn import *
from Crypto.Hash import SHA256
import base64
import struct

n = 303111819233903650638787601663617221623
e = 17
d = 53490321041277114812464604913116260313

def make_license(lic_id, lic_name):
    buf = [0]*84

    brute = 0
    while True:
        buf[16:48] = lic_id.encode('ascii').ljust(32, b'\x00')
        buf[48:80] = lic_name.encode('ascii').ljust(32, b'\x00')
        buf[80:84] = struct.pack('<I', brute)
        
        # sign it
        h = SHA256.new()
        h.update(bytes(buf[16:]))
        h = h.digest()
        c_lo, c_hi = struct.unpack('<QQ', h[:16])
        c = c_lo | (c_hi << 64)
        
        if c < n: # if c>=n, the RSA won't work so we brute
            break
        brute += 1

    m = pow(c,d,n)
    m = m*123456789%(2**128)
    signature = struct.pack('<QQ', m & 0xffffffffffffffff, (m>>64)&0xffffffffffffffff)
    buf[:16] = signature

    return bytes(buf)

r = remote('localhost', 5555)
# context.log_level = 'debug'

for i in range(100):
    x = r.recvuntil('Please generate me a license for ')
    lic_user = r.recvuntil(b' with license id ').split(b' with license id ')[0].decode('ascii')
    lic_id = r.recvuntil(b'.').split(b'.')[0].decode('ascii')
    print(lic_user, lic_id)
    lic = make_license(lic_id, lic_user)
    print (lic.hex())
    r.sendline(base64.b64encode(lic))
r.interactive()