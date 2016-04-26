#!/bin/bash
# This script sends all the neccessary files to the Pi.
# The IP variable will probably need to be changed before it is run.
IP="192.168.1.3"

# Send code
rsync -r ../terminal_pong guest@$IP:~

# Send libraries
ssh guest@$IP "mkdir -p ~/.local/lib/python2.7/site-packages"

rsync -r ~/.local/lib/python2.7/site-packages/blessed* guest@$IP:~/.local/lib/python2.7/site-packages

rsync -r ~/.local/lib/python2.7/site-packages/wcwidth* guest@$IP:~/.local/lib/python2.7/site-packages
