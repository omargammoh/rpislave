#!/bin/bash
cd /home/pi/rpislave
sudo git checkout .
sudo git pull
sudo python manage.py migrate --noinput
tmux kill-session -t rpislave
sudo chmod 700 /home/pi/rpislave/tunnelonly
sudo reboot
