import re
import os

DEFAULT = '/ext/dev/linux-5.2.2'

class Syscalls:
	pass

def syscalls(arch='x86', mode='_64'):
	s = Syscalls()
	if not os.path.isdir(DEFAULT):
		print('ERROR: kernel sources not found under '+repr(DEFAULT))
		return s
	with open(DEFAULT+'/arch/'+arch+'/entry/syscalls/syscall'+mode+'.tbl', 'r') as f:
		for line in f:
			line = line.strip()
			if line.startswith('#') or len(line) == 0:
				continue
			num, abi, name = line.split()[:3]
			setattr(s, name, int(num))
	return s
