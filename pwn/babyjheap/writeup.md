A little backstory to this challenge:

> A while back, in Google CTF Quals 2019, I worked on an interesting Java
challenged called JIT. This was a rather perculiar challenge because it was the
first Java challenge where you had to attack the JVM engine itself, or so I
thought... see, I completely overlooked a simple unicode bug where Java would
not only deem the basic numeric numbers 0-9 as "numbers" but also a couple of
others in Unicode. In hindsight, that was quite regrettful, but I found a
different bug that would propell me on a cool journey through the JVM internals.

> The challenge itself was a simple JIT compiler, which compiled some bytecode
into x86 assembly. In the original challenge, the author implicitly *expected*
each program to end with a return instruction, which codes to a `c3 ret`
instruction. Now what if we do not put that? We end up jumping code to a series
of `add [rax], al`, repeating until the end of the current mapped memory. What
if we set rax to point to some valid address, then we could have a single byte
write. The number of adds that would occur would be equivalent to the remaining
number of zeros before the end of that current mapped memory, and then the
program would seg fault (we will later talk how we can deal with this
segmentation fault). Now the problem is, the JIT code only works with `eax`, NOT
rax, which means the top 32-bits are zero'd if you decide to make any
calculations or assignments to `eax`. This poses a *slight* issue because most
of the memory maps of Java are located above the first 2GB address space. All
except one: 

> The Java heap! Because of shear luck, the author set the option `-Xmx200m` in
the JVM, which allowed JVM to optimize compressed heap pointers into a 32-bit
word. This means we can write one byte anywhere in heap! (There are
*technically* a few limitations, but practically endless). Now about that
segmentation fault. See if, anyone has ever done JNI development (I sure have,
back in my teens!), you would've seen the iconic JVM crash dump before! Of
course this means, the JVM has hooked the SIGSEGV signal handler, and has
potentially executed some code afterwards on the JVM heap. Theoretically, this
means one could craft a fake JVM heap object and have JVM call the vtable
functions of that JVM object causing variable code execution. Except it wasn't
that easy... turns out, the SIGSEGV handler code for JVM doesn't actually call
any Java functions, but directly calls the C++ versions of them. It is
theoretically possible to leak some data, but that's about it. So that pretty
much scraps that challenge all together. I was sad, so thus birth to this
arguably easier challenge!
