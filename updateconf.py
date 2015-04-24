import subprocess
import os
import sys
import django

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


def update_conf():

    # git checkout and pull
    execute("cd /home/pi/rpislave_conf&&sudo git checkout .&&sudo git pull")

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
    except:
        print 'error while getting the json configuration file'
        raise


    # setup django
    sys.path.append(os.path.dirname(__file__))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'website.settings'
    django.setup()

    # copy conf to django
    from website.models import Conf
    for c in Conf.objects.all():
        c.delete()
    newconf = Conf(data=conf_str, meta="")
    newconf.save()

    # create data folder if not existing and copy conf there
    pth = '/home/pi/data'
    if not os.path.isdir(pth):
        os.mkdir(pth)

    f = file(os.path.join(pth, "conf"), "w")
    f.write(conf_str)
    f.close()

    print "update_conf: successful"



if __name__ == "__main__":
    update_conf()

