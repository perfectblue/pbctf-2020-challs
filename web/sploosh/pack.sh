#!/usr/bin/env bash
# Produces two zips :
#   - dist.zip to be given to participants
#   - deploy.zip for deployment

zip -r challenge/src/dist.zip challenge/docker-compose.yml challenge/Dockerfile challenge/src
zip -r deploy.zip challenge/*
