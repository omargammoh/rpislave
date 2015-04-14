import os
import importlib
from website.processing import _get_conf, MP
import website.status
import website.clear
import traceback
import multiprocessing
import subprocess

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")


try:
    p = multiprocessing.Process(name="status", target=website.status.main)
    p.start()
    print "initialized status process"
except:
    print traceback.format_exc()
    print "status failed"

try:
    p = multiprocessing.Process(name="clear", target=website.clear.main)
    p.start()
    print "initialized clear process"
except:
    print traceback.format_exc()
    print "clear failed"

try:
    out = subprocess.Popen("sudo /usr/local/bin/noip2", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
    print "initialized noip"
except:
    print traceback.format_exc()
    print "noip failed"


#>>>> autostart processes with the django server
try:
    print '-'*20
    print 'initializing processes'
    ac = [m.name for m in multiprocessing.active_children()]
    print 'processes before: %s' %ac

    conf = _get_conf()

    for (ps_name,conf) in conf["apps"].iteritems():
        try:
            if conf.get('autostart', False) == True:
                m = importlib.import_module("%s.process" %ps_name)
                target = m.main
                if not (ps_name in ac):
                    print 'initializing %s' %ps_name
                    p_rec = MP(name=ps_name, target=target, request=None, cmd="start")
                    p_rec.process_command()
        except:
            print "!!unable to initialize the %s process " %ps_name

    ac = [m.name for m in multiprocessing.active_children()]
    print 'processes after: %s' %ac
    print '-'*20

except:
    print traceback.format_exc()
    print "!!an error has occurred while performing the autostart operations"


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
