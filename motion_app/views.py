import json
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
import traceback
import subprocess
import os
from itertools import groupby
from motion_app.process import get_motion_config


info = {
    "label": "MOTION",
    "desc": "Record videos, take pictures, create timelapse files and stream videos using a camera"
}


lis_signals = [
     {"name": "SIGHUP", "btn": "hangup",  "desc": "The config file will be reread.	This is a very useful signal when you experiment with settings in the config file"}
    ,{"name": "SIGTERM", "btn": "terminate", "desc": "If needed motion will create an mpeg file of the last event and exit"}
    ,{"name": "SIGUSR1", "btn": "usr1", "desc": "Motion will create an mpeg file of the current event"}
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
    motion_conf = {k: {"h" : "<code>%s</code> (currently %s)" %(k, v), "v": v} for (k,v) in get_motion_config().iteritems()}
    d = {"motion_conf": motion_conf, "lis_signals": lis_signals, "info": info}
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

def recent_events(request):
    lis = [
        "last_motion_detected"
        ,"last_event_start"
        ,"last_event_end"
        ,"last_picture_save"
        ,"last_motion_detected"
        ,"last_area_detected"
        ,"last_movie_start"
        ,"last_movie_end"
        ,"last_camera_lost"
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
