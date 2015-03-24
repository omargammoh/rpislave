#sudo apt-get install git
#sudo git clone -b master https://omargammoh@github.com/omargammoh/pylog485.git
#sudo python ~/pylog485/setup.py

import subprocess
import os
import json

try:
    jsonfile = os.path.join(__file__,'setup.json')
    #jsonfile = r"C:\Users\omarg_000\Google Drive\Code\pylog485\setup.json"

    if not os.path.isfile(jsonfile):
        raise BaseException('the json config file was not found %s' %jsonfile)

    fl = file(jsonfile,"r")
    js = json.load(fl)
    fl.close()
except:
    print 'error while getting the json configuration file'
    raise

"""
"{{{0[network][address]}dfs df s df s}}"
""".format(js)


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
    #TODO: put the right variables here!
    filepath=r"/etc/inittab"
    linestarttocomment = "1:2345:respawn:/sbin/getty "
    linetoappend = "1:2345:respawn:/bin/login -f pi tty1 </dev/tty1 >/dev/tty1 2>&1"

    f = file(filepath, "r")
    lines = f.readlines()
    f.close()
    newlines = []
    done = False
    alreadydone = False

    for line in lines:
        if line.startswith(linestarttocomment):
            newlines.append("#the following line is commented by the script, the line after is appended by the script\n")
            newlines.append("#" + line)
            newlines.append(linetoappend + "\n")
            done = True
        elif line.startswith(linetoappend):
            alreadydone = True
            print "already done"
            break
        else:
            newlines.append(line)

    if alreadydone:
        return None

    if not done:
        raise BaseException('the string was not found in the file')

    os.remove(filepath)
    f = file(filepath, "w")
    f.write("".join(newlines))
    f.close()
    print "setup_autologin completed"

def setup_autostart():
    filepath = "/home/pi/.bashrc"
    #filepath = r"C:\Users\omarg_000\Desktop\test.txt"
    linetoappend = r". /home/pi/pylog485/start.sh"

    f = file(filepath,"r")
    s = f.readlines()
    f.close()
    if linetoappend in "".join(s):
        print "line already there"
        return None
    else:
        f = file(filepath, "w")
        f.writelines(s + [linetoappend])
        f.close()

    print "setup_autologin successful"
    return None

def setup_internetsettings():
    f = file("/etc/wpa_supplicant/wpa_supplicant.conf", "w")
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
}}""".format(js)
    f.write(contents)
    f.close()

    f = file("sudo nano /etc/network/interfaces", "r+")
    contents="""
auto lo
iface lo inet loopback
iface eth0 inet dhcp

#### for a wlan DHCP ip
#iface wlan0 inet dhcp
#   wpa-ssid "xx"
#   wpa-psk "xx"

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

""".format(js)
    print "setup_staticwifi: successful"

def setup_realtimeclock():
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


if False and __name__ == "__main__":
    execute([
         'sudo apt-get install python-dev <<<y'
        ,'sudo apt-get install python-pip <<<y'
        ,'sudo apt-get install tmux'
        ,'sudo pip install django==1.7'
        ,'sudo pip install pymodbus==1.2.0'
        ,'sudo pip install pymongo==2.8'
        ])

    setup_autologin()
    setup_autostart()
    setup_internetsettings()
    if js["realtimeclock"]["installed"]:
        setup_realtimeclock()


if False:
    fp = r"C:\Users\omarg_000\Desktop\test.txt"
    f = file(fp, "r")
    s=f.readlines()
    f.close()
    f = file(fp, "w")
    f.writelines(s)
    f.close()
