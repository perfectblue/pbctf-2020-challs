CPPFLAGS=-Wall -Wno-strict-aliasing
CFLAGS=-g -O2
LDLIBS=-lcrypto

all: core flag.enc

clean:
	rm -f *.o ccdump ccdump.bin enc /tmp/secure core flag1.h flag.key 

enc: enc.o mtwister.o

.PHONY: core_check
core_check:
	@( /usr/bin/test $$(cat /proc/sys/kernel/core_pattern) == "core"  || \
		( /bin/echo -e "Need to run:\n  echo core | sudo tee /proc/sys/kernel/core_pattern" && false ) )

core: ccdump.bin core_check passwds
	@rm -f core flag.enc
	@cp $< flag_decryptor
	@setarch x86_64 -R bash -c 'ulimit -c 100000; echo "  RUN $<" && ! ./flag_decryptor < passwds'
	@echo "  TEST /tmp/secure " && stat /tmp/secure 2> /dev/null > /dev/null
	@echo "  TEST core " && stat core 2> /dev/null > /dev/null

ccdump.c: flag1.h

flag1.h: passwds
	@echo "  GEN $@" && echo -n $$(head -1 $<) | md5sum | \
		awk '{print "#define FLAG1_HASH  #", $$1, "# ";}' | \
		sed 's/ # /"/g' > $@

flag.key: core
	sha256sum /tmp/secure | awk '{ print $$1; }' | unhex > $@

flag.enc: xor.py flag2 flag.key 
	python3 $^ $@
	@cp ccdump.bin flag_decryptor
	@setarch x86_64 -R bash -c 'ulimit -c 100000; echo "  RUN $<" && ./flag_decryptor < passwds'
	
ccdump: ccdump.o mtwister.o safeguard.o

ccdump.bin: ccdump enc
	@cp $< $@
	@strip ccdump.bin
	@./enc $@
	@chmod +x ccdump.bin
