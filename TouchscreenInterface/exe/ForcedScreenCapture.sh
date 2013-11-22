#!/bin/sh

ssh vislin01.nccs.nasa.gov 'bash -c "source ~/.bash_profile; echo 'show' | nc localhost 35127; ScreenCapture.sh"'
scp vislin01.nccs.nasa.gov:/tmp/I.jpg $1
