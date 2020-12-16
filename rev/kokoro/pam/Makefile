all: pam_captcha.so pam_ratelimit.so

pam_captcha.so: pam_captcha.c
	gcc $(CFLAGS) -c -fPIC -DHAVE_SHADOW -Wall -Werror -Wno-unused -Wno-unused-variable -Wno-unused-result -O2 pam_captcha.c
	gcc $(LDFLAGS) -o pam_captcha.so -s -lpam -lcrypt -lz --shared pam_captcha.o

pam_ratelimit.so: pam_ratelimit.c
	gcc $(CFLAGS) -c -fPIC -DHAVE_SHADOW -Wall -Werror -Wno-unused -Wno-unused-variable -Wno-unused-result -O2 pam_ratelimit.c
	gcc $(LDFLAGS) -o pam_ratelimit.so -s -lpam -lcrypt -lz --shared pam_ratelimit.o

clean:
	rm -rf *.o *.so

.PHONY: clean all
