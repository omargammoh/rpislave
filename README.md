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
  * Get the rpislave files: 
    * `sudo git clone -b master https://github.com/omargammoh/rpislave.git ~/rpislave`
  * Get the configuration file from somewhere such as gist and put it in the right place e.g. 
    * `conf_id=4d5eece56a8ac282dd06&&sudo git clone https://gist.github.com/$conf_id.git ~/conf&&sudo cp ~/conf/conf.json ~/rpislave/conf.json`
  * Install things (will take a while): 
    * `sudo python ~/rpislave/setup.py`
  * Reboot, The server will start automatically after the reboot
    * `sudo reboot`
* To access it from anywhere, forward your router ports to your rpi device: 
  * Port 9001 for the website
  * Port 9002 for motion's video streaming
  * Port 9003 for morion's config server
  * Port 9004 for BTSync server
  * Port 22 for ssh server
* setup ddns with www.noip.com
  * `cd /usr/local/src`
  * `sudo wget http://www.no-ip.com/client/linux/noip-duc-linux.tar.gz`
  * `sudo tar xzf noip-duc-linux.tar.gz`
  * `cd noip-2.1.9-1/`
  * `sudo make`
  * `sudo make install`
  * `sudo /usr/local/bin/noip2 -C`
  * `sudo /usr/local/bin/noip2`


# How to use #
* Surf to the page `192.168.1.201:9001` hosted by the rpi (this is the address in the default configuration file, choose the right address as configured in the conf.json file). if you enabled port forwarding you could access it with at the address your_router_ip:9001
* Look at what apps are there and start using them! the interface should be intuitive...

# Current apps #
  * <b>gpio_app</b>: Control and observe the GPIO (input output) pins of your rpi slave
  * <b>camshoot_app</b>: Take high resolution pictures using your ras-pi camera
  * <b>motion_app</b>Record videos, take pictures, create timelapse files and stream videos using a camera
  * <b>datalog_app</b>: Record data from RS485 devices and signals connected to MCP3008 chip 
  * <b>datasend_app</b>: Send data produced by your other apps to a database
  * <b>btsync_app</b>: Coming soon ...

# Contribute #
Feel free to fork and contribute with new apps or improve current apps! We need apps to use the rpi as a media center. 
  
