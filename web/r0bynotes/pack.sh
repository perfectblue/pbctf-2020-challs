#!/usr/bin/env bash

rm -rf dist dist.zip
cp -a challenge dist

find dist -name '.DS_Store' -type f -delete
rm -rf dist/app/.idea
echo 'flag{not_the_flag}' > dist/flag.txt

zip -r dist.zip dist/*
rm -rf dist
