# This requires nasm and nasmx to build!

all: bitstreams


.PHONY: all

bitstreams.o: phase1.bit tricks.inc

bitstreams: bitstreams.o
	ld -z noexecstack $< -o $@
	strip -w -N '*.*' -N '__*' $@

phase1.bin: phase1_5.bit tricks.inc
phase1_5.bin: phase2.bit tricks.inc
phase2.bin: phase2_1.bin phase3.xor tricks.inc
phase3.bin: tricks.inc
phase%.bin: tricks.inc

phase3.xor: XORKEY = $(shell hex "H0w_l0w_")


%.bin: %.asm
	nasm -Wall -f bin $< -o $@

%.o: %.asm
	nasm -Wall -f elf64 $<

%.xor: %.bin
	./xorencrypt.py $(XORKEY) < $< > $@

%.bit: %.bin
	./bitencode.py < $< > $@

.PHONY: clean
clean:
	rm -rf *.xor *.bin *.bit *.o bitstreams
