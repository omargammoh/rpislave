# RPI SLAVE

## How to install on a raspberry pi##
* Install the raspbian image on the raspberry pi (rpi)
* Connect the rpi to the internet, ssh into it and execute `rpislave_url=https://github.com/omargammoh/rpislave.git&&rpislave_branch=master&&cd&&sudo git clone -b $rpislave_branch $rpislave_url ~/rpislave&&sudo python ~/rpislave/setup.py`
* Execute `sudo raspi-config`
  * Expand filesystem
  * Enable camera
  * Enable SPI
  * Enable i2c
* Reboot
  * `sudo reboot`
* Note: at this point you may take an image of the sd card and use it for other installations, you just need to re-expand the file system 
* Surf to the page `<raspberrypi_ip>:9001` hosted by the rpi
* Add the configuration json file in the admin page `<ip-address>:9001/admin/website/conf/`
* Reboot, The server will start automatically after the reboot
  * `sudo reboot`
* Initiate slave on rpi-master:
  * In the rpimaster database, in the latestinfo collection, add document with the orrect parameters:`{"label": "Development and testing", "data_db": "i-1", "fs_db": "fs-1"}`

## Ports ##
* The following ports are used in he raspberry pi:
  * `9001` for the main website
  * `9002` for motion's video streaming
  * `9003` for morion's configuration
  * `9005` for ssh server

## Available apps ##
  * <b>gpio_app</b>: Control and observe the GPIO (input output) pins of your rpi slave
  * <b>motion_app</b>: Record videos, take pictures, create timelapse files and stream videos using a camera (runs another software called [motion](http://www.lavrsen.dk/foswiki/bin/view/Motion/WebHome))
  * <b>datalog_app</b>: Record data from RS485 devices and signals connected to MCP3008 chip 

## Optional ##
* Direct connection to pi
  * add `ip=169.254.0.2` to `sudo nano /boot/cmdline.txt` (see https://pihw.wordpress.com/guides/direct-network-connection/in-a-nut-shell-direct-network-connection/). reboot, connect ethernet cable to rpi and computer then ssh into `ip=169.254.0.2`. if computer is not connected, the rpi will take longer time to boot, and yu cannot connect to the internet via ethernet
* Installing real time clock:
  * under development...
* Switch to another git branch, eg: master
  * `cd /home/pi/rpislave&&sudo git checkout master`
 
## Installation check-list ##
* Configuration is installed
* File system is expanded, check with `df -h`
* `ip=169.254.0.2` is removed from `sudo nano /boot/cmdline.txt`
* Check slave is up to date
