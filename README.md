# RPI SLAVE

## How to install on a raspberry pi##
* Install the raspberian image on the raspberry pi
* ssh into the the raspberry pi and execute `rpislave_url=https://github.com/omargammoh/rpislave.git&&rpislave_branch=master&&cd&&sudo git clone -b $rpislave_branch $rpislave_url ~/rpislave&&sudo python ~/rpislave/setup.py`
* `sudo raspi-config`
  * Expand filesystem
  * Enable camera
  * Enable SPI
  * Enable i2c
* Reboot, The server will start automatically after the reboot
  * `sudo reboot`
* Surf to the page `<raspi_ip>:9001` hosted by the rpi
* Add the configuration json file in the admin page `<ip-address>:9001/admin/website/conf/`
* ssh into the raspberry pi and run the setup.py
  * `sudo python ~/rpislave/setup.py` 
* To access it from outside your network, you need to forward the following ports:
  * `9001` for the main website
  * `9002` for motion's video streaming
  * `9003` for morion's configuration
  * `9004` for BTSync server
  * `9005` for ssh server

# Available apps #
  * <b>gpio_app</b>: Control and observe the GPIO (input output) pins of your rpi slave
  * <b>motion_app</b>: Record videos, take pictures, create timelapse files and stream videos using a camera (runs another software called [motion](http://www.lavrsen.dk/foswiki/bin/view/Motion/WebHome))
  * <b>datalog_app</b>: Record data from RS485 devices and signals connected to MCP3008 chip 

# direct connection to pi #
  * add `ip=169.254.0.2` to `sudo nano /boot/cmdline.txt` https://pihw.wordpress.com/guides/direct-network-connection/in-a-nut-shell-direct-network-connection/
