#!/bin/bash
cd
cd rpislave
sudo git checkout .
sudo git pull
tmux kill-session -t rpislave
. /home/pi/rpislave/start.sh
#tmux a -t rpislave