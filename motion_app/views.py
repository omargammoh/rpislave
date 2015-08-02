import json
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
import traceback
import subprocess
import os
from itertools import groupby
from motion_app.process import get_motion_config
from motion_app.models import EventFile
from bson import json_util
import datetime
import pytz
import base64

info = {
    "label": "MOTION",
    "desc": "Record videos, take pictures, create timelapse files and stream videos using a camera"
}


lis_signals = [
#      {"name": "SIGHUP", "btn": "hangup",  "desc": "The config file will be reread.	This is a very useful signal when you experiment with settings in the config file"}
#    , {"name": "SIGTERM", "btn": "terminate", "desc": "If needed motion will create an mpeg file of the last event and exit"}
     {"name": "SIGUSR1", "btn": "create movie", "desc": "Motion will create an mpeg file of the current event"}
]


def _get_pid():
    s = subprocess.Popen("ps aux", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
    lis = [line for line in s.split("\n") if line.split()[-2:]==['sudo', 'motion'] and not('bin/sh' in line)]
    if len(lis) != 1:
        print 'could not get pid, len(lis) = %s' %len(lis)
        for l in lis:
            print l
        return None
    pid = lis[0].split()[1]
    return pid


def home(request, template_name='motion_app/home.html'):
    conf = get_motion_config()
    host = request.get_host().lstrip('http://').split(':')[0]

    #camera is accessed from lan, the host is the ip of the rpi
    if host.startswith('192.168.1'):
        cameraport = str(conf["webcam_port"])

    #camera is accessed from wan, port needs to be calculated
    else:
        #try get lan ip, because based on it we will find the camera ip
        try:
            fp = '/home/pi/data/status'
            f = file(fp, "r")
            s = f.read()
            f.close()
            ip_lan = json.loads(s)['ip_lan']
            if not ip_lan.startswith('192.168.1'):
                raise BaseException('')
            cameraport = '9' + ip_lan.split('.')[-1][1:3] + '2'
        except:
            cameraport = conf["webcam_port"]
            print ">> status: previous status not loadable"

    motion_conf = {k: {"h" : "<code>%s</code> (currently %s)" %(k, v), "v": v} for (k,v) in conf.iteritems()}
    d = {"motion_conf": motion_conf, "lis_signals": lis_signals, "info": info}
    d["stream_address"] = 'http://' + host + ":" + cameraport
    return render_to_response(template_name, d, context_instance=RequestContext(request))


def send_signal(request):
    d = {}
    try:
        signal = request.GET['cmd']

        pid = _get_pid()
        if pid:
            s = subprocess.Popen("sudo kill -s %s %s" %(signal, pid), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
            d["msg"] = "%done"
        else:
            d["msg"] = "could not find pid"
        print request
        return HttpResponse(json.dumps(d), content_type='application/json')
    except:
        d["error"] = traceback.format_exc()
        print d["error"]
        return HttpResponse(json.dumps(d), content_type='application/json')


def du(request):
    d = {}
    try:
        d['data'] = subprocess.Popen("cd /home/pi/data/motion_app&&du -h", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read().split("\n")
    except:
        d['error']=traceback.format_exc()
    return HttpResponse(json.dumps(d), content_type='application/json')


def get_files(request):
    d = {}
    try:
        folder = get_motion_config()["target_dir"]
        if not os.path.isdir(folder):
            d["error"] = "the directory %s does not exist, please start the motion app first" %folder
        else:
            files = os.listdir(folder)
            fun = lambda x: x.split('.')[-1]
            for key, group in groupby(sorted(files, key=fun),fun ):
                fl = sorted(list(group))


                d2 = {"count": len(fl)}
                if fl:
                    d2.update({'first': fl[0], 'last': fl[-1]})
                else:
                    d2.update({'first': '-', 'last': "-"})

                if key != 'jpg':
                    d2.update({"files": fl})

                d[key] = d2

        return HttpResponse(json.dumps(d), content_type='application/json')
    except:
        d["error"] = traceback.format_exc()
        print d["error"]
        return HttpResponse(json.dumps(d), content_type='application/json')

def register_event(request):
    d = {}
    try:
        data = {}
        data["dt"] = datetime.datetime.utcnow()
        data["label"] = request.GET['label']
        data["path"] = request.GET['path']

        ef = EventFile(data=json_util.dumps(data))
        ef.save()

        d["msg"] = "done"
        return HttpResponse(json.dumps(d), content_type='application/json')
    except:
        d["error"] = traceback.format_exc()
        print d["error"]
        return HttpResponse(json.dumps(d), content_type='application/json')


def recent_events(request):
    lis = [
        "motion_detected"
        ,"event_start"
        ,"event_end"
        ,"picture_save"
        ,"motion_detected"
        ,"area_detected"
        ,"movie_start"
        ,"movie_end"
        ,"camera_lost"
    ]
    d = {}
    folder = "/home/pi/data/motion_app"
    try:
        if "name" in request.GET:
            name = request.GET["name"]
            if name == "all":
                for name in lis:
                    if os.path.isfile(os.path.join(folder, name)):
                        f = file(os.path.join(folder, name), "r")
                        d[name] = f.read()
                        f.close()
                    else:
                        d['msg'] = d.get('msg', "") + "%s not found, " %name
            elif name in lis:
                if os.path.isfile(os.path.join(folder, name)):
                    f = file(os.path.join(folder, name), "r")
                    d[name] = f.read()
                    f.close()
                else:
                    raise BaseException('%s not found in environment variables' %name)
            else:
                raise BaseException('%s is not a valid variable to ask for' %name)
        else:
            raise BaseException('name parameter is required')
    except:
        d["error"] = traceback.format_exc()

    return HttpResponse(json.dumps(d), content_type='application/json')

def gantt_data(request):
    d={}
    try:

        #dbdata = [{'dt':datetime.datetime(2010,1,1) + datetime.timedelta(hours=7 * i+1), "event":["movie_start", "movie_end"][i%2]}for i in range(100)]
        dbdata = [ev for ev in [json_util.loads(e.data) for e in Event.objects.all()] if ev['label'] in ["movie_start", "movie_end"]]
        dbdata = sorted(dbdata, key=lambda x:x['dt'])
        #print dbdata
        lis=[]
        d = {}
        for p in dbdata:
            print p
            day = datetime.datetime(p['dt'].year, p['dt'].month, p['dt'].day, tzinfo=pytz.utc)
            if p["label"] == "movie_start":
                d = {'start': p['dt'], 'date': p['dt'].strftime('%Y%m%d'), 'startHour':((p['dt']-day).total_seconds()/3600.)}
            elif p["label"] == "movie_end":
                if "startHour" in d:
                    if p['dt'].date() == d['start'].date():
                        d['endHour'] = ((p['dt'] - day).total_seconds()/3600.)
                        d["status"] = "SUCCEEDED"
                        d.pop('start')
                        lis.append(d)
                    elif p['dt'].date() > d['start'].date():
                        d['endHour'] = 24
                        d.pop('start')
                        lis.append(d)
                        lis.append({'date': p['dt'].strftime('%Y%m%d'), 'startHour': 0, 'endHour': p['dt'].hour})
                    else:
                        print 'sdfsdddddddddddddddddddd'
                        raise BaseException('xx')
                d = {}
            else:
                continue

        now = datetime.datetime.utcnow()
        nowday = datetime.datetime(now.year, now.month, now.day)
        d = {'date': now.strftime('%Y%m%d'), 'startHour':((now - nowday).total_seconds()/3600.)}
        d['endHour'] = 24.
        d["status"] = "RUNNING"
        lis.append(d)

        dic = {}
        dic['data'] = lis

        return HttpResponse(json.dumps(dic), content_type='application/json')

    except:
        d = {}
        d["error"] = str(traceback.format_exc())
        print d["error"]
        return HttpResponse(json.dumps(d), content_type='application/json')

def getfile(request):
    try:
        path = request.GET["path"]
        f = file(path, "rb")
        s = f.read()
        b64 = base64.b64encode(s)

        return HttpResponse(json.dumps({'data': b64}), content_type='application/json')
    except:
        d = {}
        d["error"] = str(traceback.format_exc())
        print d["error"]
        return HttpResponse(json.dumps(d), content_type='application/json')
