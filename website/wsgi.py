import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")
from website.processing import get_conf, MP, filter_kwargs
import traceback
import multiprocessing
import importlib

from django.conf import settings

try:
    conf = get_conf()
except:
    conf = None
    print "> conf could not be loaded, starting without a conf"

if conf is not None:
    #autostart processes
    for proc_name in settings.RPI_PROC:
        try:
            # import the module
            m = importlib.import_module("website.proc.%s" %proc_name)
            # get the configuration of it
            proc_kwargs = conf.get("proc", {}).get(proc_name, {})
            #execute the main function
            if hasattr(m, "main"):
                p = multiprocessing.Process(name=proc_name, target=m.main, kwargs=filter_kwargs(func=m.main, kwargs_input=proc_kwargs))
                p.start()
                print '> start process: %s' % proc_name
            else:
                print '> !! process %s does not have a main function' % proc_name
        except:
            print traceback.format_exc()
            print "> !! start process failed %s" % proc_name

    #autostart apps
    try:
        print ">", '-'*20
        print '> initializing processes'
        ac = [m.name for m in multiprocessing.active_children()]
        print '> processes before: %s' % ac

        for (ps_name, conf) in conf.get("apps", {}).iteritems():
            try:
                if conf.get('autostart', True) == True:
                    m = importlib.import_module("%s.process" % ps_name)
                    target = m.main
                    if not (ps_name in ac):
                        print '> initializing %s' % ps_name
                        p_rec = MP(name=ps_name, target=target, request=None, cmd="start")
                        p_rec.process_command()
            except:
                print "> !!unable to initialize the %s process " % ps_name

        ac = [m.name for m in multiprocessing.active_children()]
        print '> processes after: %s' %ac
        print ">", '-'*20

    except:
        print traceback.format_exc()
        print "> !!an error has occurred while performing the autostart operations"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
