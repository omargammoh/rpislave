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

import datalog_app.process
import datasend_app.process
import gpio_app.process
import camstream_app.process

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
            #dic["the last 5 datalog_apped stamps in local DB"] = [{'data':json_util.loads(ob.data), 'meta':json_util.loads(ob.meta)} for ob in Reading.objects.all().order_by('-id')[:5]]
            dic["the last 20 recorded stamps in local DB"] = [str({'data':json_util.loads(ob.data), 'meta':json_util.loads(ob.meta)}) for ob in Reading.objects.all().order_by('-id')[:20]]
            #dic["the last 5 recorded stamps in local DB"] = [('data=' + ob.data + "    meta=" + ob.meta) for ob in Reading.objects.all().order_by('-id')[:5]]
        jdic= json_util.dumps(dic)
    except:
        err = traceback.format_exc()
        jdic = json.dumps({"error": err})

    return HttpResponse(jdic, content_type='application/json')


def manage(request):
    print request
    try:
        app = request.GET['app']
        if app == "datalog_app": target = datalog_app.process.main
        elif app == "datasend_app": target = datasend_app.process.main
        elif app == "gpio_app": target = gpio_app.process.main
        elif app == "camstream_app": target = camstream_app.process.main
        else: raise BaseException('unknown app %s' %app)

        mp = MP(name=app, target=target, request=request)
        mp.process_command()
        dic = json.dumps(mp.dic)
    except:
        err = traceback.format_exc()
        dic = json.dumps({"error": err})
    return HttpResponse(dic, content_type='application/json')


