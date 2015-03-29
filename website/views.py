from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import json
from bson import json_util
import multiprocessing
from datalog_app.models import Reading
from datetime import datetime
from django.conf import settings
import traceback
from website.processing import MP, _get_conf
import importlib
import subprocess


def home(request, template_name='home.html'):
    app_list = _get_conf()['apps'].keys()
    print app_list
    return render_to_response(template_name, {"app_list": app_list}, context_instance=RequestContext(request))


def nourls(why):
    def nourls(request, template_name='nourls.html'):
        return render_to_response(template_name,{"why": why}, context_instance=RequestContext(request))
    return nourls


def status(request):
    try:
        cmd = request.GET.get("cmd",None)
        dic = {}
        if cmd == "conf":
            dic['conf'] = _get_conf()
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

def get_temp(request):
    d={}
    try:
        d['data'] = subprocess.Popen("/opt/vc/bin/vcgencmd measure_temp", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
    except:
        d['error']=traceback.format_exc()
    return HttpResponse(json.dumps(d), content_type='application/json')

def get_df(request):
    d={}
    try:
        d['data'] = subprocess.Popen("df -h", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
    except:
        d['error']=traceback.format_exc()
    return HttpResponse(json.dumps(d), content_type='application/json')


def appmanage(request):
    try:
        m = importlib.import_module("%s.process" %request.GET['app'])
        target = m.main

    except:
        dic = json.dumps({"error": "no process.main seams to be found for the app %s" %request.GET.get('app',"x")})
        return HttpResponse(dic, content_type='application/json')

    try:
        mp = MP(name=request.GET['app'], target=target, request=request)
        mp.process_command()
        dic = json.dumps(mp.dic)
        return HttpResponse(dic, content_type='application/json')

    except:
        err = traceback.format_exc()
        dic = json.dumps({"error": err})
        return HttpResponse(dic, content_type='application/json')


