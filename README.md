# RPI SLAVE

# About this project #

### What is it ###
There are many things a raspberry pi (rpi) can do (e.g. stream video, record data, ...).
This project is django server which can be easily installed on an rpi, where different things an rpi can do are coded in django apps. The rpi will serve an intuitive website which can be used to control the apps and the rpi device.

# How to easily install #
* Install the raspberian image on the raspberry pi
* Connect the rpi to the internet and execute:
  * `sudo git clone https://github.com/omargammoh/rpislave.git`
  * Configure your rpi slave with the file `sudo nano ~/rpislave/conf.json`
  * `sudo python ~/rpislave/setup.py`
  * `sudo reboot` the server will start automatically after the reboot

# How to use #
* Surf to the page `192.168.1.201:9001` hosted by the rpi (this is the address in the default configuration file, choose the right address as configured in the conf.json file)
* Look at what apps are there and start using them! the interface should be intuitive...

# Current apps #
  * <b>datalog_app</b>: an app to log data from RS485 devices connected to the usb port and sensors connected to MCP3008 connected to the SPI interface of the rpi 
  * <b>datasend_app</b>: an app to send data logged by the datalog_app to any mongodb
  * <b>gpio_app</b>: under construction ...
  * <b>camstream_app</b>: under construction ...

# This project is currently under construction ... #
