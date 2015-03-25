from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import json
from bson import json_util
import multiprocessing
from mng.models import Conf
from datalog_app.models import Reading
from datetime import datetime
from django.conf import settings
import traceback
import mng.processing
from mng.processing import MP
import importlib


def home(request, template_name='home.html'):
    return render_to_response(template_name, {}, context_instance=RequestContext(request))

def status(request):
    try:
        cmd = request.GET.get("cmd",None)
        dic = {}
        if cmd == "conf":
            dic['conf'] = mng.processing._get_conf()
        if cmd == "overview":
            dic['this process'] = multiprocessing.current_process().name
            dic['active child processes'] = [m.name for m in  multiprocessing.active_children()]
            dic['utc time'] = str(datetime.utcnow())
            dic['configuration label'] = settings.CONF_LABEL

        if cmd == "recentdata":
            dic["the last 20 recorded stamps in local DB"] = [str({'data':json_util.loads(ob.data), 'meta':json_util.loads(ob.meta)}) for ob in Reading.objects.all().order_by('-id')[:20]]
        jdic= json_util.dumps(dic)
    except:
        err = traceback.format_exc()
        jdic = json.dumps({"error": err})

    return HttpResponse(jdic, content_type='application/json')

def apphome(request):
    try:
        m = importlib.import_module("%s.views" %request.GET['app'])
        res = m.home(request)
        print "yyyyyyyyyyyessss"
        return res
    except:
        print 'noooooo'
        template_name = 'nohome.html'
        return render_to_response(template_name, {}, context_instance=RequestContext(request))

def appmanage(request):
    try:
        m = importlib.import_module("%s.process" %request.GET['app'])
        target = m.main

        mp = MP(name=request.GET['app'], target=target, request=request)
        mp.process_command()
        dic = json.dumps(mp.dic)
    except:
        err = traceback.format_exc()
        dic = json.dumps({"error": err})
    return HttpResponse(dic, content_type='application/json')


