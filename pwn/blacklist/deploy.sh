#!/bin/bash -e

DIST=blacklist-dist
TAR=blacklist.tar.gz

make

rm -rf $DIST
mkdir $DIST

cp blacklist genfiles.py Dockerfile Makefile xinetd $DIST
cp exploit.c blacklist.bsm $DIST

rm -f $TAR
tar -czf $TAR $DIST
