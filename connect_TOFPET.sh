#!/bin/bash

fileA="/tmp/d.sock"
fileB="/dev/shm/daqd_shm"

if [ -f "$fileA" ]
then
    echo "removing $fileA"
    rm -i $fileA
fi

if [ -f "$fileB" ]
then
    echo "removing $fileB"
    rm -i $fileB
fi

./daqd --socket-name=/tmp/d.sock --daq-type=GBE
