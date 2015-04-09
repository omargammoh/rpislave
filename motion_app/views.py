import json
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
import traceback
import subprocess
import os
from itertools import groupby
from motion_app.process import get_motion_config
from motion_app.models import Event
from bson import json_util
import datetime
import pytz

info = {
    "label": "MOTION",
    "desc": "Record videos, take pictures, create timelapse files and stream videos using a camera"
}


lis_signals = [
      {"name": "SIGHUP", "btn": "hangup",  "desc": "The config file will be reread.	This is a very useful signal when you experiment with settings in the config file"}
    , {"name": "SIGTERM", "btn": "terminate", "desc": "If needed motion will create an mpeg file of the last event and exit"}
    , {"name": "SIGUSR1", "btn": "usr1", "desc": "Motion will create an mpeg file of the current event"}
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
    motion_conf = {k: {"h" : "<code>%s</code> (currently %s)" %(k, v), "v": v} for (k,v) in conf.iteritems()}
    d = {"motion_conf": motion_conf, "lis_signals": lis_signals, "info": info}
    d["stream_address"] = 'http://' + request.get_host().lstrip('http://').split(':')[0] + ":" + str(conf["webcam_port"])
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
        ev = Event(data=json_util.dumps(data))
        ev.save()
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

        dbdata = [{'dt':datetime.datetime(2010,1,1) + datetime.timedelta(hours=7 * i+1), "event":["movie_start", "movie_end"][i%2]}for i in range(100)]
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
                        lis.append(d)
                    elif p['dt'].date() > d['start'].date():
                        d['endHour'] = 24
                        lis.append(d)
                        lis.append({'date': p['dt'].strftime('%Y%m%d'), 'startHour': 0, 'endHour': p['dt'].hour})
                    else:
                        print 'sdfsdddddddddddddddddddd'
                        raise BaseException('xx')
                d = {}
            else:
                continue

        for l in lis:
            if 'start' in l:
                l.pop('start')
            print l

        #d['data'] = [{"date":"group %s" %(i/3), "startHour": 1, "endHour":5, "status":"SUCCEEDED"} for i in range(20)]
        d['data'] = lis

        return HttpResponse(json.dumps(d), content_type='application/json')

    except:
        d = {}
        d["error"] = str(traceback.format_exc())
        print d["error"]
        return HttpResponse(json.dumps(d), content_type='application/json')

