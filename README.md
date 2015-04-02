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
  * Get the rpislave files: `sudo git clone -b master https://github.com/omargammoh/rpislave.git ~/rpislave`
  * Edit the conf file to your needs `sudo nano ~/rpislave/conf.json`, OR get it from somewhere and put it in the right place e.g. `sudo git clone https://gist.github.com/4d5eece56a8ac282dd06.git ~/rpislave && cp ~/rpislave/4d5eece56a8ac282dd06/example  ~/rpislave/conf.json`
  * Install things (will take a while): `sudo python ~/rpislave/setup.py`
  * Reboot `sudo reboot`. The server will start automatically after the reboot
* to access it from anywhere, forward your router ports 9001, 9002, 9003 to your rpi
 
# How to use #
* Surf to the page `192.168.1.201:9001` hosted by the rpi (this is the address in the default configuration file, choose the right address as configured in the conf.json file). if you enabled port forwarding you could access it with at the address <your router's ip>:9001
* Look at what apps are there and start using them! the interface should be intuitive...

# Current apps #
  * <b>gpio_app</b>: Control and observe the GPIO (input output) pins of your rpi slave
  * <b>camshoot_app</b>: Take high resolution pictures using your ras-pi camera
  * <b>motion_app</b>Record videos, take pictures, create timelapse files and stream videos using a camera
  * <b>datalog_app</b>: Record data from RS485 devices and signals connected to MCP3008 chip 
  * <b>datasend_app</b>: Send data produced by your other apps to a database

# Contribute #
Feel free to fork and contribute with new apps or improve current apps! We need apps to use the rpi as a media center. 
  
