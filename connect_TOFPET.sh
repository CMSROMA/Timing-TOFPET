#!/bin/bash

file1="/tmp/d.sock"
file2="/dev/shm/daqd shm"

if [ -f "$file1" ]
then
    echo "removing $file1"
    rm -i $file1
fi

if [ -f "$file2" ]
then
    echo "removing $file2"
    rm -i $file2
fi

./daqd --socket-name=/tmp/d.sock --daq-type=GBE
