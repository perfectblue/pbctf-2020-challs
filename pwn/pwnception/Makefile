all: kernel userland main

main: src/main.c
	gcc src/main.c -lunicorn -pthread -Wall -s -Werror -o main

kernel: src/kernel.s
	nasm -f bin src/kernel.s -o kernel

userland: src/userland.c
	musl-gcc src/userland.c -o userland -s -static -Wall -Werror

docker: kernel userland main libunicorn.so.1 libc.so.6
	cp kernel userland main libunicorn.so.1 libc.so.6 docker/challenge/

clean:
	rm main userland kernel dist.zip

.PHONY: dist
dist: docker
	rm -rf dist dist.zip
	cp -a docker dist
	find dist -name '.DS_Store' -type f -delete
	echo 'pbctf{flag_goes_here}' > dist/challenge/flag.txt
	zip -r dist.zip dist/*
	rm -rf dist