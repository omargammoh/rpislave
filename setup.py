"""
This file installs libraries and does neccessary changes for the rpislave to work
This installation can be executed without the configuration, installations that depend on the configuration are done in prerun.py
"""
import subprocess
import os
from time import time

def _execute(lis):
    if type(lis) == str:
        lis=[lis]
    for cmd in lis:
        print ""
        print ">>>> %s" %cmd
        out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
        print out.strip()
        print "<<<<"
    return out

def setup_autologin():
    print "setup_autologin: this is not required anymore in debian jessie"

def setup_autostart():
    #apends a line to a file
    filepath = "/home/pi/.bashrc"
    linetoappend = r". /home/pi/rpislave/start.sh"

    f = file(filepath,"r")
    s = f.readlines()
    f.close()
    if any([ss.strip() == linetoappend for ss in s]):
        print "setup_autostart: already done"
        return None

    f = file(filepath,"w+")
    s = f.writelines(s + [linetoappend])
    f.close()
    print "setup_autostart: successful"

def create_datafolder():
    #create datafolder if doesnt exist
    pth = '/home/pi/data'
    if not os.path.isdir(pth):
        os.mkdir(pth)

def change_sshport():
    """
    changes the line Port 22 to Port 9005
    """
    filepath = "/etc/ssh/sshd_config"
    linetoappend = r"Port 9005"

    f = file(filepath, "r")
    s = f.readlines()
    f.close()
    if any([ss.strip() == linetoappend for ss in s]):
        print "change_sshport: already done"
        return None

    done = False
    newlis = []
    for ss in s:
        if ss.strip() == "Port 22":
            newlis.append(linetoappend + "\n")
            done = True
        else:
            newlis.append(ss)
    if done:
        f = file(filepath, "w+")
        s = f.writelines(newlis)
        f.close()
        print "change_sshport: successful"
    else:
        print "change_sshport: !!strange behaviour"

def support_onewire():
    """
    this has to be done for one wire to be usable, see
    http://www.raspberrypi-spy.co.uk/2013/03/raspberry-pi-1-wire-digital-thermometer-sensor/
    """
    filepath = "/boot/config.txt"
    toappend = "\ndtoverlay=w1-gpio,gpiopin=4"
    f = file(filepath, "r")
    s = f.read()
    f.close()
    if toappend in s:
        print "support_onewire: already done"
    else:
        f = file(filepath, "w+")
        s = f.writelines(s + toappend)
        f.close()
        print "support_onewire: added support for onewire"

if __name__ == "__main__":
    t1 = time()
    _execute([
        "sudo apt-get -y update" #needed for motion
    ])
    t2 = time()
    _execute([
         'sudo apt-get install -y python-dev' #needed by uwsgi and other things
        ,'sudo apt-get install libpcre3 libpcre3-dev'#neeeded by uwsgi, this needs to run beforre installling uwsgi
        ,'sudo apt-get install -y python-pip'
        ,"sudo pip install uwsgi"
        ,'sudo apt-get install tmux'
        ,'sudo pip install django==1.7'
        ,'sudo pip install pymongo==2.8'
        ,'sudo pip install pytz'
        ,'sudo pip install requests'
        ,'sudo pip install python-dateutil'

        ])
    t3 = time()


    setup_autologin()
    setup_autostart()

    #if 'datalog_app' in conf.get('apps', {}):
    _execute([
         'sudo pip install spidev'
        ,'sudo pip install pymodbus==1.2.0'
        ])

    #if 'motion_app' in conf.get('apps', {}):
    _execute([
        'sudo apt-get install -y motion'
        ])

    create_datafolder()
    change_sshport()
    support_onewire()

    t4 = time()
    print "took %0.2f sec=" % (t4 - t1)
    print "    %0.2f sec for update" % (t2 - t1)
    print "    %0.2f sec for basic libraries" % (t3 - t2)
    print "    %0.2f sec for app related libraries" % (t4 - t3)


