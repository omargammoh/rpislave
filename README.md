# RPI SLAVE

## How to install on a raspberry pi##
* Install the raspbian (2016-05-27-raspbian-jessie) image on the raspberry pi (rpi)
* Connect the rpi to the internet, ssh into it and execute `rpislave_url=https://github.com/omargammoh/rpislave.git&&rpislave_branch=master&&cd&&sudo git clone -b $rpislave_branch $rpislave_url ~/rpislave&&sudo python ~/rpislave/setup.py`
* Execute `sudo raspi-config`
  * Boot options -> console autologin 
  * Expand filesystem
  * Enable camera
  * Advanced options -> enable SPI
  * Advanced options -> enable i2c
* Reboot
  * `sudo reboot`
* Note: at this point you may take an image of the sd card and use it for other installations, you just need to re-expand the file system 
* Optional: adding a realtime clock
  * DS3231 for pi (http://www.raspberrypi-spy.co.uk/2015/05/adding-a-ds3231-real-time-clock-to-the-raspberry-pi/)
    *  in `sudo nano /etc/modules`, ensures the lines `i2c-dev` and `rtc-ds1307` are there
    *  in `sudo nano /etc/rc.local`, ensure the line `echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device` is there before the line `exit 0`
  * Rasclock
    * follow https://www.raspberrypi.org/forums/viewtopic.php?f=63&t=161133  
      * add `dtoverlay=i2c-rtc,ds3231` to `/boot/config.txt`
      * comment out the three lines `if [ -e /run/systemd/system ] ; then exit 0 fi` in `sudo nano /lib/udev/hwclock-set`
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
* Direct ethernet connection from PC to raspberry pi
  * add `ip=169.254.0.2` to `sudo nano /boot/cmdline.txt` (see https://pihw.wordpress.com/guides/direct-network-connection/in-a-nut-shell-direct-network-connection/). reboot, connect ethernet cable to rpi and computer then ssh into `ip=169.254.0.2`. if computer is not connected, the rpi will take longer time to boot, and yu cannot connect to the internet via ethernet
* Switch to another git branch, eg: master
  * `cd /home/pi/rpislave&&sudo git checkout master`
* Use another pin than GPIO4 for one-wire
  * in `sudo nano /boot/config.txt`, choose the gpio number in the line `dtoverlay=w1-gpio,gpiopin=17`
* vnc server
  * install `sudo apt-get install tightvncserver`
  * run this before connection `sudo systemctl start vncserver-x11-serviced.service`

## Installation check-list ##
* Configuration is installed
* File system is expanded, check with `df -h`
* `ip=169.254.0.2` is removed from `sudo nano /boot/cmdline.txt`
* Check slave is up to date

