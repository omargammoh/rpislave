import subprocess
import os
import json
from time import time

#get the configuration file
try:
    conffolder = '/home/pi/rpislave_conf'
    conffile = None
    if not os.path.isdir(conffolder):
        raise BaseException('could not find the rpislave_conf folder %s' %conffolder)

    for path, subdirs, files in os.walk(conffolder ):
        if not ".git" in path:
            for name in files:
                if name.endswith(".json"):                    
                    conffile = os.path.join(path, name)

    if conffile is None:
        raise BaseException('no json config file was not found in folder %s' %conffolder)

    fl = file(conffile, "r")
    conf_str = fl.read()
    fl.close()
    conf = json.loads(conf_str)
except:
    print 'error while getting the json configuration file'
    raise

def execute(lis):
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

def setup_networkinterfaces():
    network = conf.get("network_interfaces", ["### loopback ###","auto lo","iface lo inet loopback","### ethernet ###","iface eth0 inet dhcp"])
    contents = "\n".join(network)
    f = file("/etc/network/interfaces", "w+")
    f.write(contents)
    f.close()

    print "setup_networkinterfaces: interfaces successful"

def setup_db():
    import os
    import sys
    import django

    sys.path.append(os.path.dirname(__file__))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'website.settings'
    execute("sudo python /home/pi/rpislave/manage.py migrate")

    django.setup()
    from django.contrib.auth.models import User
    if len(User.objects.all()) == 0:
        u = User.objects.create_superuser(conf.get('super_user', {}).get('login', 'pi'), '', conf.get('super_user', {}).get('password', 'raspberry'))
        u.save()
        print "superuser created"
        
    from website.models import Conf
    for c in Conf.objects.all():
        c.delete()
    newconf = Conf(data=conf_str, meta="")
    newconf.save()
    print "setup_db: successful"

def create_datafolder():
    #create datafolder if doesnt exist
    pth = '/home/pi/data'
    if not os.path.isdir(pth):
        os.mkdir(pth)

    #write the conf file in the datafolder
    f = file(os.path.join(pth, "conf"), "w")
    f.write(conf_str)
    f.close()

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

def install_btsync():
    if os.path.isfile('/home/pi/btsync'):
        print "install_btsync: btsync already installed"
    else:
        execute([
            'cd /home/pi&&wget https://download-cdn.getsyncapp.com/stable/linux-arm/BitTorrent-Sync_arm.tar.gz'
            ,'cd /home/pi&&tar -zxvf BitTorrent-Sync_arm.tar.gz'
            ])
        print "install_btsync: sucessful"

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


if __name__ == "__main__":
    t1 = time()
    execute([
         "sudo apt-get -y update" #update is needed for motion
    ])
    t2 = time()
    execute([
         'sudo apt-get install -y python-dev'
        ,'sudo apt-get install -y python-pip'
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

    if 'network_interfaces' in conf:
        setup_networkinterfaces()

    if 'apps' in conf:
        if 'datalog_app' in conf['apps']: 
            execute([
                'sudo pip install spidev'
                ,'sudo pip install pymodbus==1.2.0'
                ])

        if 'datasend_app' in conf['apps']:
            pass

        if 'motion_app' in conf['apps']:
            execute([
                'sudo apt-get install -y motion'
                ])

        if "rtc" in conf:
            setup_realtimeclock()

    install_btsync()
    setup_db()
    create_datafolder()
    change_sshport()

    t4 = time()
    print "took %0.2f sec=" % (t4 - t1)
    print "    %0.2f sec" % (t2 - t1)
    print "    %0.2f sec" % (t3 - t2)
    print "    %0.2f sec" % (t4 - t3)


