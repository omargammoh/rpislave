import json
import subprocess
import os
import sys
import traceback

def _sanitize_colname(label):
    if label == "":
        return ""
    if not(label[0].isalpha() or label[0] == "_"):
        label = "_" + label
    if label.startswith('system.') or label.startswith('objectlabs-system.'):
        label = "_" + label

    label = label.replace(' ', '_').lower()
    label = "".join([l if (l.isdigit() or l.isalpha() or l in ['_', '-', '.']) else '_' for l in label])
    if len(label)>50:
        label=label[:50]
    return label
    #The name you choose must begin with a letter or underscore and must not begin with 'system.' or 'objectlabs-system.'
    #. It also must have fewer than 80 characters and cannot have any spaces or special characters (hyphens, underscores and periods are OK) in it.

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

def _getconf():
    #get the configuration file
    try:
        #first priority is to use /home/pi/rpislave/conf.json is existing
        conffilepath = '/home/pi/rpislave/conf.json'
        if os.path.isfile(conffilepath):
            fl = file(conffilepath, "r")
            conf_str = fl.read()
            fl.close()
            conf = json.loads(conf_str)
            print 'using the json file for the installation %s' % conffilepath

        #second priority is to check for a configuration in the sqlite database
        else:
            print "attempting to get conf from sqlite db"
            try:
                #prepare django
                import django
                os.environ['DJANGO_SETTINGS_MODULE'] = 'website.settings'
                django.setup()

                #get conf
                from website.processing import get_conf
                conf = get_conf()
                conf_str = json.dumps(conf)
                print "got the conf from sqlite db, using it for the installation"
            except:
                #proceed with conf = None, conf_str = None
                print "was not able to get conf from sqlite db"
                print "proceeding the installation with conf = None, which installs all the apps"
                conf_str = None
                conf = None
    except:
        print traceback.format_exc()
        conf = None
        conf_str = None

    return conf, conf_str

def setup_networkinterfaces():
    if conf is None or (not('network_interfaces' in conf)):
        print "setup_networkinterfaces: Nothing done"
        return None

    network = conf.get("network_interfaces", ["### loopback ###","auto lo","iface lo inet loopback","### ethernet ###","iface eth0 inet dhcp"])
    contents = "\n".join(network)

    f = file("/etc/network/interfaces", "w+")
    f.write(contents)
    f.close()
    print "setup_networkinterfaces: interfaces successful"

def setup_db():

    import django
    sys.path.append(os.path.dirname(__file__))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'website.settings'

    django.setup()

    #adding a superuser
    from django.contrib.auth.models import User
    for u in User.objects.all():
        u.delete()

    if conf is not None:
        login = conf.get('super_user', {}).get('login', 'pi')
        password = conf.get('super_user', {}).get('password', 'raspberry')
    else:
        login = "pi"
        password = "raspberry"
    u = User.objects.create_superuser(login, '', password)
    u.save()

    #updating the conf in the sqlite db only if there is a conf.json file
    if conf_str is not None and os.path.isfile('/home/pi/rpislave/conf.json'):
        from website.models import Conf
        for c in Conf.objects.all():
            c.delete()
        newconf = Conf(data=conf_str, meta="")
        newconf.save()

def network_name():
    """
    http://www.howtogeek.com/167195/how-to-change-your-raspberry-pi-or-other-linux-devices-hostname/
    rename raspberrypi in 'sudo nano /etc/hosts'    and 'sudo nano /etc/hostname'
    sudo /etc/init.d/hostname.sh

    """
    if conf is not None:
        # read and edit /etc/hosts
        newname = _sanitize_colname(conf['label']).replace('_', '-')#underscores are not allowed in hostnames
        f = file('/etc/hosts')
        lines = [('127.0.1.1\t%s\n' %newname if ln.startswith('127.0.1.1') else ln) for ln in f.readlines()]
        f.close()

        #overwrite /etc/hosts
        f = file('/etc/hosts', 'w+')
        f.writelines(lines)
        f.close()

        #overwrite /etc/hostname
        f = file('/etc/hostname', 'w+')
        f.write(newname)
        f.close()

        _execute(["sudo /etc/init.d/hostname.sh"])

        print 'changed network name to %s' %newname
        return None
    else:
        print "did not change network name"

if __name__== '__main__':
    if not os.path.isfile('/home/pi/rpislave/db.sqlite3'):
        _execute("sudo python /home/pi/rpislave/manage.py migrate")
    conf, conf_str = _getconf()
    setup_db()
    _execute("sudo python /home/pi/rpislave/manage.py collectstatic --noinput --settings=website.settings")
    setup_networkinterfaces()
    network_name()
