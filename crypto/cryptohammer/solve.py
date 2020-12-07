#with open('cryptohammer_40000/flag.iso.enc', 'rb') as f:
with open('cryptohammer_40000/flag.iso.enc', 'rb') as f:
	e = f.read()

base = 0x0040000
for i in range(90000*2):
	print(e[base+i]&1)
