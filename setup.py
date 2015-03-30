import subprocess
import os
import json
from time import time
try:
    conffile = os.path.join(os.path.dirname(__file__), 'conf.json')

    if not os.path.isfile(conffile):
        raise BaseException('the json config file was not found %s' %conffile)

    fl = file(conffile,"r")
    conf = json.load(fl)
    fl.close()
except:
    print 'error while getting the json configuration file'
    raise

def execute(lis):
    if type(lis) == str:
        lis=[lis]
    for cmd in lis:
        print ">>>> %s" %cmd
        out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
        print out
        print "<<<<"
    return out

def setup_autologin():
    # replaces a line in a file

    filepath=r"/etc/inittab"
    linetocomment = "1:2345:respawn:/sbin/getty --noclear 38400 tty1"
    linetoappend = "1:2345:respawn:/bin/login -f pi tty1 </dev/tty1 >/dev/tty1 2>&1"

    f = file(filepath, "r")
    text = f.read()
    f.close()

    if linetocomment in text:
        newtext = text.replace(linetocomment,linetoappend)
    elif linetoappend in text:
        print "setup_autologin: file seems to be already done"
        return None
    else:
        raise BaseException('could not find linetocomment or linetoappend in file')

    f = file(filepath, "w+")
    f.write(newtext)
    f.close()

    print "setup_autologin: completed"

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

def setup_internetsettings():
    #write file1
    contents = """
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={{
    ssid="{0[network][wifi_name]}"
    proto=RSN
    key_mgmt=WPA-PSK
    pairwise=CCMP TKIP
    group=CCMP TKIP
    psk="{0[network][wifi_pass]}"
}}""".format(conf)
    f = file("/etc/wpa_supplicant/wpa_supplicant.conf", "w+")
    f.write(contents)
    f.close()
    print "setup_internetsettings: wpa_supplicant.conf successful"

    #write file2
    contents="""
auto lo
iface lo inet loopback
iface eth0 inet dhcp

#### for a wlan static ip
allow-hotplug wlan0
auto wlan0
iface wlan0 inet manual
wpa-roam /etc/wpa_supplicant/wpa_supplicant.conf
iface default inet static
    #the address you want to give your pi, current address can be found with ifconfig, inet addr:192.168.1.4
    address {0[network][address]}
    #from ifconfig, Mask:255.255.255.0
    netmask {0[network][netmask]}
    #the router IP address, from netstat -nr, Destination 192.168.1.0#
    network {0[network][network]}
    #from netstat -nr, Gateway 192.168.1.1
    gateway {0[network][gateway]}

""".format(conf)
    f = file("/etc/network/interfaces", "r+")
    f.write(contents)
    f.close()

    print "setup_internetsettings: interfaces successful"

def setup_realtimeclock():
    print "not ready for this yet"
    return None

    typ = conf['rtc'].get('type','rasclock')
    if typ == "rasclock":
        execute("wget http://afterthoughtsoftware.com/files/linux-image-3.6.11-atsw-rtc_1.0_armhf.deb&&sudo dpkg -i linux-image-3.6.11-atsw-rtc_1.0_armhf.deb&&sudo cp /boot/vmlinuz-3.6.11-atsw-rtc+ /boot/kernel.img")

        filepath = "/etc/modules"
        toappend = [
            "i2c-bcm2708"
            ,"rtc-pcf2127a"
            ]

        filepath = "/etc/rc.local"

        toappend = [ #just before exit 0
             "echo pcf2127a 0x51 > /sys/class/i2c-adapter/i2c-1/new_device"
            ,"( sleep 2; hwclock -s ) &"
             ]
    else:
        raise BaseException('we do not know how to install this clock %s' %typ)


if __name__ == "__main__":
    t1 = time()
    execute([
         "sudo apt-get -y update" #update is needed for motion
        #,"sudo apt-get -y upgrade"
        #,"sudo apt-get install rpi-update"
        #,"sudo rpi-update"
    ])
    t2 = time()
    execute([
         'sudo apt-get install -y python-dev'
        ,'sudo apt-get install -y python-pip'
        ,'sudo apt-get install tmux'
        ,'sudo pip install django==1.7'
        ])
    t3 = time()

    setup_autologin()

    setup_autostart()

    if 'network' in conf:
        setup_internetsettings()

    if 'apps' in conf:
        if 'datalog_app' in conf['apps']:
            execute([
                'sudo pip install pymodbus==1.2.0'
                ])

        if 'datasend_app' in conf['apps']:
            execute([
                'sudo pip install pymongo==2.8'
                ])

        if 'motion_app' in conf['apps']:
            execute([
                'sudo apt-get install -y motion'
                ])

        if "rtc" in conf:
            setup_realtimeclock()
    t4 = time()
    print "took %0.2f sec=" %(t4-t1)
    print "    %0.2f sec" %(t2-t1)
    print "    %0.2f sec" %(t3-t2)
    print "    %0.2f sec" %(t4-t3)


