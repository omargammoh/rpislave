#!/bin/bash
cd /home/pi/rpislave
sudo git checkout .
sudo git pull
tmux kill-session -t rpislave
sudo reboot
