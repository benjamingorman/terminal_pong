#!/bin/bash
# This script sends all the neccessary files to the Pi.
# The IP variable will probably need to be changed before it is run.
IP="192.168.1.3"

# Send code and libraries
rsync -r ../terminal_pong guest@$IP:~

# Send libraries
rsync -r ~/.local/lib/python2.7/site-packages/{blessed,wcwidth} guest@$IP:~/terminal_pong
