#!/bin/bash -e

DIST=todo_deploy/
TAR=todo.tar.gz

rm -rf $DIST
mkdir -p $DIST

#./save.sh
cp Dockerfile libc-2.31.so todo Makefile string2.cc todo.cc string2.h $DIST

rm -f $TAR
tar -czvf $TAR $DIST
