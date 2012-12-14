#!/bin/sh

ssh vislin01 'bash -c "source ~/.bash_profile; echo 'show' | nc localhost 35127; ScreenCapture.sh"'
scp vislin01:/tmp/I.jpg $1
