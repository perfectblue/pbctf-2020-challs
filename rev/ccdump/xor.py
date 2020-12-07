import sys

_, in1, in2, out = sys.argv

try:
    f = open(out, 'w+b')
except:
    f = open(out, 'x+b')

data = []
for a, b in zip(open(in1, 'rb').read(), open(in2, 'rb').read()):
    data.append(a ^ b)
f.write(bytes(data))
f.close()

