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
    execute("cd /home/pi/conf&&sudo git checkout .&&sudo git pull")

    #get conf_str
    try:
        conffile = os.path.join(os.path.dirname(__file__), 'conf.json')
        if not os.path.isfile(conffile):
            raise BaseException('the json config file was not found %s' %conffile)
        fl = file(conffile,"r")
        conf_str = fl.read()
        fl.close()
        #conf = json.loads(conf_str)
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

    print "update_conf: successful"

if __name__ == "__main__":
    update_conf()

