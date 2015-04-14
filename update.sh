#!/bin/bash
cd /home/pi/rpislave
sudo git checkout .
sudo git pull
sudo python manage.py migrate
tmux kill-session -t rpislave
sudo reboot
