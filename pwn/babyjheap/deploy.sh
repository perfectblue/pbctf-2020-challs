#!/bin/bash -e

TAR=jheap.tar.gz

make -C src

rm -rf jheap_deploy
mkdir jheap_deploy
cp -r deploy src README gdb Dockerfile java-atk-wrapper.jar jheap_deploy/

rm -f $TAR
tar -czf $TAR jheap_deploy 
