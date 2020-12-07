from pwn import *
import objs

mem = objs.SeqMemory(0)
mem.writeobj(objs.B_arr, [1,4,5,6,45])
mem.write("uintle:32", 0xcccccccc)
mem.pos = 0

obj = mem.readobj()
print(repr(obj))
assert(obj.arr == [1, 4, 5, 6, 45])
assert(mem.read('uintle:32') == 0xcccccccc)

mem.pos = 0
mem.writeobj(objs.JHeap, 23, -144)
mem.write('uintle:32', 0xdddddddd)

mem.pos = 0
obj = mem.readobj()
print(repr(obj))
assert(repr(obj) == 'JHeap[23]: [deadbeef]')
assert(mem.read('uintle:32') == 0xdddddddd)

mem.pos = 0
mem.rebase(0x1000)
obj = mem.readobj()
print(repr(obj))
assert(repr(obj) == 'JHeap[23]: [00001090]')
assert(mem.read('uintle:32') == 0xdddddddd)

mem.pos = 5 * 32
mem.write("bytes:1", 'a')
mem.pos = 0
obj = mem.readobj()
print(repr(obj))
assert(repr(obj) == 'JHeap[23]: [00001061]')
assert(mem.read('uintle:32') == 0xdddddddd)

mem.pos = 0
mem.rebase(0xcccccccc)
obj = mem.readobj()
print(repr(obj))
assert(repr(obj) == 'JHeap[23]: [00001061]')
assert(mem.read('uintle:32') == 0xdddddddd)


