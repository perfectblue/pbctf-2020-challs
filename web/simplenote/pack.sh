#!/usr/bin/env bash

rm -rf dist.zip
find challenge -name '.DS_Store' -type f -delete
zip -r dist.zip challenge/*