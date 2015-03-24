"""
WSGI config for pylog485 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")


#>>>> this part tells the sotware the start the record and send processes when the django server starts
import common
import record.views
import send.views
import multiprocessing
print '-'*20
print 'initializing processes'
ac = [m.name for m in multiprocessing.active_children()]
print 'processes before: %s' %ac

if False:
    try:
        if not ("record" in ac):
            print 'initoalizing record'
            p_rec = common.MP(name='record', target=record.views.record, request=None, cmd="start")
            p_rec.process_command()
    except:
        print "!!unable to initialize the record process"

    try:
        if not ("send" in ac):
            print 'initializing send'
            p_rec = common.MP(name='send', target=send.views.send, request=None, cmd="start")
            p_rec.process_command()
    except:
        print "!!unable to initialize the send process"

    ac = [m.name for m in multiprocessing.active_children()]
    print 'processes after: %s' %ac
    print '-'*20
    #<<<<<

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
