#!/bin/bash
cd /home/pi/rpislave
sudo git checkout .
sudo git pull
sudo python /home/pi/rpislave/manage.py migrate --noinput
tmux kill-session -t rpislave
echo 'restarting in 3 seconds'
sleep 3
sudo reboot
