#!/bin/bash

sudo apt install build-essential libpam-dev libz-dev

make

cp -v *.so /lib/x86_64-linux-gnu/security/
