import website.templatetags.customfilters
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import json
from bson import json_util
import multiprocessing
from datalog_app.models import Reading
from datetime import datetime
import traceback
from website.processing import MP, get_conf
import importlib
import subprocess
from website.templatetags.customfilters import conf

def home(request, template_name='home.html'):
    conf = get_conf()
    app_info = []
    for app in conf['apps'].keys():
        try:
            d = {"name": app}
            m = importlib.import_module("%s.views" %app)
            if hasattr(m, "info"):
                d.update(m.info)
                print "added app info %s" % app
            else:
                print "app %s has no info" % app
            app_info.append(d)
        except:
            print '!!could not add info from the app %s' % (app)
    return render_to_response(template_name, {"app_info": app_info, "desc": conf.get('desc', '-')}, context_instance=RequestContext(request))

def confsetup(request, template_name='confsetup.html'):
    return render_to_response(template_name, {}, context_instance=RequestContext(request))

def test(request, template_name='test.html'):
    return render_to_response(template_name, {}, context_instance=RequestContext(request))

def nourls(why):
    def nourls(request, template_name='nourls.html'):
        return render_to_response(template_name,{"why": why}, context_instance=RequestContext(request))
    return nourls

def status(request):
    try:
        cmd = request.GET.get("cmd",None)
        dic = {}
        if cmd == "conf":
            dic['conf'] = get_conf()
        if cmd == "overview":
            dic['this process'] = multiprocessing.current_process().name
            dic['active child processes'] = [(m.name, m.pid) for m in  multiprocessing.active_children()]
            dic['utc time'] = str(datetime.utcnow())

        if cmd == "recentdata":
            dic["the last 20 recorded stamps in local DB"] = [str({'data':json_util.loads(ob.data), 'meta':json_util.loads(ob.meta)}) for ob in Reading.objects.all().order_by('-id')[:20]]
        jdic= json_util.dumps(dic)
    except:
        err = traceback.format_exc()
        jdic = json.dumps({"error": err})

    return HttpResponse(jdic, content_type='application/json')

def cmd(request):
    d = {}
    try:
        cmd = request.GET['cmd']
        d['data'] = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read().split("\n")
    except:
        d['error']=traceback.format_exc()
    return HttpResponse(json.dumps(d), content_type='application/json')

def commits_behind(request):
    def prcess_text(txt):
        l = [x for x in txt.split('\n') if "# Your branch is behind" in x]
        if l:
            return l[0]
        else:
            return "nothing to pull"

    d = {}
    try:
        d['rpislave'] = [prcess_text(subprocess.Popen("cd /home/pi/rpislave&&sudo git remote update&&git status -uno", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read())]
        d['rpislave'].append(subprocess.Popen("cd /home/pi/rpislave&&sudo git fetch&&sudo git log ..@{u}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read().split('\n'))
        d['rpislave_conf'] = [prcess_text(subprocess.Popen("cd /home/pi/rpislave_conf&&sudo git remote update&&git status -uno", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read())]
        d['rpislave_conf'].append(subprocess.Popen("cd /home/pi/rpislave_conf&&sudo git fetch&&sudo git log ..@{u}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read().split('\n'))
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

def rqst(request):
    d = {}
    try:
        d["request"] = str(request)
        return HttpResponse(json.dumps(d), content_type='application/json')
    except:
        d["error"] = traceback.format_exc()
        print d["error"]
        return HttpResponse(json.dumps(d), content_type='application/json')

def blink_led(request):
    """
    could not get the following code to work:,
    echo none | sudo tee /sys/class/leds/ACT/trigger
    for (( i=1; i <= 5; i++ ))
    do
      echo 1 | sudo tee /sys/class/leds/ACT/brightness
      sleep 0.1s
      echo 0 | sudo tee /sys/class/leds/ACT/brightness
      sleep 0.1s
    done
    echo mmc0 | sudo tee /sys/class/leds/ACT/trigger
    """
    d = {}
    try:
        lis_cmd = []
        lis_cmd.append("echo none | sudo tee /sys/class/leds/ACT/trigger")
        blink = ["echo 1 | sudo tee /sys/class/leds/ACT/brightness", "sleep 0.1s", "echo 0 | sudo tee /sys/class/leds/ACT/brightness", "sleep 0.1s"]
        lis_cmd = lis_cmd + blink * 25
        lis_cmd.append("echo mmc0 | sudo tee /sys/class/leds/ACT/trigger")
        d['data'] = subprocess.Popen("\n".join(lis_cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read().split("\n")
    except:
        d['error']=traceback.format_exc()
    return HttpResponse(json.dumps(d), content_type='application/json')

def setup_conf(request):
    try:
        if conf is None:
            str_conf = request.GET['str_conf']
            try:
                json_conf = json.loads(str_conf)

            except:
                return HttpResponse(json.dumps({"error": "not able to parse the conf that you sent %s" % str_conf}), content_type='application/json')
        else:
            return HttpResponse(json.dumps({"error": "conf is already installed, you may not overwrite it"}), content_type='application/json')
    except:
        return HttpResponse(json.dumps({"error": "%s" %traceback.format_exc()}), content_type='application/json')
