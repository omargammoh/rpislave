# RPI SLAVE

# About this project #

There are many things a raspberry pi (rpi) can do (e.g. record data, stream video, ...).
This project is a django server which can be easily installed on an rpi, where different things an rpi can do are coded in django apps. The rpi will serve an intuitive website which can be used to control the apps and the rpi device.

# How to easily install #
* Install the raspberian image on the raspberry pi
* `sudo raspi-config`
  * Expand filesystem
  * Enable camera
  * Enable SPI
* Connect the rpi to the internet and:
  * Get the rpislave repository:
    * `sudo git clone -b master https://github.com/omargammoh/rpislave.git ~/rpislave`
  * Get the configuration file from somewhere and put it in the right place, for example: 
    * `conf_id=4d5eece56a8ac282dd06&&sudo git clone https://gist.github.com/$conf_id.git ~/conf&&sudo cp ~/conf/conf.json ~/rpislave/conf.json`
  * Install things (will take a while): 
    * `sudo python ~/rpislave/setup.py`
  * Reboot, The server will start automatically after the reboot
    * `sudo reboot`

# How to use #
* Surf to the page `<raspi_ip>:9001` hosted by the rpi
* Look at what apps are there and start using them! the interface should be intuitive...
* To access it from outside your network, you need to forward the following ports:
  * 9001 for the main website
  * 9002 for motion's video streaming
  * 9003 for morion's configuration
  * 9004 for BTSync server
  * 22 for ssh server

# Current apps #
  * <b>gpio_app</b>: Control and observe the GPIO (input output) pins of your rpi slave
  * <b>camshoot_app</b>: Take high resolution pictures using your ras-pi camera
  * <b>motion_app</b>: Record videos, take pictures, create timelapse files and stream videos using a camera (runs another software called [motion](http://www.lavrsen.dk/foswiki/bin/view/Motion/WebHome))
  * <b>datalog_app</b>: Record data from RS485 devices and signals connected to MCP3008 chip 
  * <b>datasend_app</b>: Send data produced by your other apps to a database
  * <b>btsync_app</b>: Sync the data of the other apps with other devices (runs another software called [bittorrent sync](https://www.getsync.com/))

# Contribute #
Feel free to do so...
  
