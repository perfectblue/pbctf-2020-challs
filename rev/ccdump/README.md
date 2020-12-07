# Corey's Coredump

**Category**: Reversing

**Author**: theKidOfArcrania

**Description**: 

Ahh dammit... worked so hard on this decryptor to print the flag, but now it 
just crashed and my work is gone :(

Thankfully I have the coredump and backed up the encrypted flag, pls get the
flag decrypted for me!

**Public files**:
 * core
 * flag.enc

## Solution
Here you have to reverse the challenge. There are actually existing tools out
there that convert [core dumps to ELF binaries][1].

There are a few anti-reversing tricks that make the reverse job a lot harder:
  1. You didn't have the actual ELF binary. Only a core dump of the binary is
     provided, but you will find out a core dump actually gives more information
     about a binary (well except for the useful section headers, which I don't
     think gets loaded at runtime); in addition to the memory segments of the
     actual ELF code, it also provides the current snapshot of all the memory
     mappings (so like the variables in use, which you will find useful later).
  2. Assuming that you manage to extract into an ELF binary and successfully run
     the binary, you will find out that it will remove itself :D
  3. This binary makes heavy uses of signal oriented code:
     * It uses SIGTRAP to implement trapcalls (syscalls) to invoke certain
       functions, by sending a TRAP signal each time it wants to call some
       system library function. I found it surprisingly difficult to debug,
       because falling through on this "TRAP" signal that gdb usually does will
       produce erratic behavior!
     * It uses SIGILL whenever part of the code is encoded. (The exact algorithm
       for encoding a segment of code is just XOR'ing with the mersenne twister
       PRNG, seeded with the lower 12-bits of that code segment's address). It
       also uses SIGILL shortly after leaving this code segment to reencode this
       segment.
     * It also catches SIGSEG to mprotect read-only regions to make it RWX
       (whenever the SIGILL handler needs to write to some code section). There
       is also a special address read which will undo the RWX mprotect command.

With that in mind, the intended solution was to examine the stack addresses
corresponding to the main function, and try to recover a few local variable
values located in the stack. The first password is stored in the BSS segment,
and is relatively unscathed; however, the second password has undergone several
processes that make the recovery process a lot more difficult:

  1. The second password first gets encrypted using our encryption routine
     (takes in the string and XORs using a PRNG with the seed being the address
     of the string).
  2. Then it gets XOR'd with the first password.
  3. Finally it then gets XOR'd one more time with a PRNG using a randomized
     seed. We then zero out the seed so it seems as if the password is
     unrecoverable?

It turns out that the state of this last PRNG step is actually maintained on the
stack, so we can extract the state and rewind the PRNG algorithm. It turns out
the original mersenne twister algorithm seems to not be fully reversable, so I
revised the twisting part of the algorithm to make it reversable. At this point,
we would just extract the encrypted strings and the PRNG state and solve the
password. 

Then at this point, we then SHA256 the second password, and decrypt the flag!

[1]: https://github.com/enbarberis/core2ELF64
