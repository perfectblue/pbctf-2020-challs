FROM ubuntu:focal

ENV DEBIAN_FRONTEND noninteractive

# Update
RUN apt-get update --fix-missing && apt-get -y upgrade && apt-get install -y xinetd libglib2.0 libpixman-1-0 zlib1g

# Create ctf-user
RUN groupadd -r ctf && useradd -r -g ctf ctf
RUN mkdir /home/ctf

# Configuration files/scripts
ADD ctf.xinetd /etc/xinetd.d/ctf

# Challenge files
ADD challenge/bzImage /home/ctf/bzImage
ADD challenge/pc-bios /home/ctf/pc-bios
ADD challenge/qemu-system-x86_64 /home/ctf/qemu-system-x86_64
ADD challenge/rootfs-real.cpio.gz /home/ctf/rootfs.cpio.gz
ADD challenge/run.sh /home/ctf/run.sh
ADD run_challenge.sh /home/ctf/run_challenge.sh

# Set some proper permissions
RUN chmod 755 /home/ctf/qemu-system-x86_64
RUN chmod 755 /home/ctf/run.sh
RUN chmod 755 /home/ctf/run_challenge.sh

WORKDIR /home/ctf/
EXPOSE 1337

CMD service xinetd restart && /bin/sleep infinity