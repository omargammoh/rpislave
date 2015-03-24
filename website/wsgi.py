import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")

#>>>> autostart processes with the django server
try:
    import multiprocessing
    print '-'*20
    print 'initializing processes'
    ac = [m.name for m in multiprocessing.active_children()]
    print 'processes before: %s' %ac

    import mng.processing
    conf = mng.processing._get_conf()
    print "autostart %s" %conf["autostart"]

    import record.process
    import send.process


    for ps_name in conf["autostart"]:
        try:
            if ps_name == "record": target = record.process.main
            elif ps_name == "send": target = send.process.main
            else: raise BaseException('dont know how to autostart this process %s' %ps_name)
            if not (ps_name in ac):
                print 'initializing %s' %ps_name
                p_rec = mng.processing.MP(name=ps_name, target=target, request=None, cmd="start")
                p_rec.process_command()
        except:
            print "!!unable to initialize the %s process " %ps_name


    ac = [m.name for m in multiprocessing.active_children()]
    print 'processes after: %s' %ac
    print '-'*20
except:
    print "!!an error has occurred while performing the autostart operations"


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
