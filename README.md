# RPI SLAVE

# About this project #

### What is it ###
There are many things a raspberry pi (rpi) can do (e.g. stream video, record data, datasend_app data, ...).
This project is a way to easily setup a server on on rpi using django, where different things an rpi can do is coded in a django app. The raspberry pi and the apps are controlled with the django server.

# How to easily install #
* Install the raspberian image on the raspberry pi
* Connect the rpi to the internet and execute:
  * `sudo git clone https://github.com/omargammoh/rpislave.git`
  * Configure your rpi slave with the file `sudo nano ~/rpislave/conf.json`
  * `sudo python ~/rpislave/setup.py`
  * `sudo reboot`

# How to use #
* Surf to the page `192.168.1.201:9001` hosted by rpi (this is the address in the default configuration file, choose the right address as configured in the conf.json file)
* Look at what apps are there and start using them! the interface should be intuitive...

# Current apps #
  * datalog_app: an app to log data from RS485 devices connected to the usb port and sensors connected to MCP3008 connected to the SPI interface of the rpi 
  * datasend_app: an app to send data logged by the datalog_app to any mongodb
  * gpio_app: under construction ...
  * camstream_app: under construction ...



# Currently under construction ... #
