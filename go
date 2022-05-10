#!/bin/sh

# build pyvoyager image - see Dockerfile
docker build -t vg .

# run pyvoyager image in docker container
docker run -it --rm --name vg vg $*
