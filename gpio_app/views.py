from website.processing import _get_conf
import gpio_app.process
import json

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from datetime import datetime

gpio_pins = sorted(set([4,16,27,23,22,24,25,5,6,12,13,19,4,26,20,21]))

pins_conf = _get_conf()['apps']['gpio_app']['pins_conf']

def home(request, template_name='gpio_app/home.html'):
    rev = {cf["pin"]: {"label": label, "desc": cf['desc']} for (label, cf) in pins_conf.iteritems()}
    gpio_list = []
    for pin in gpio_pins:
        d = {}

        try: d["label"] = rev[pin]['label']
        except: d["label"] = "-"

        try: d["desc"] = rev[pin]['desc']
        except: d["desc"] = "-"

        d.update({"pin": pin, "iou": ["input", 'output', 'unset'][pin % 3], "status": "HIGH"})
        gpio_list.append(d)
    return render_to_response(template_name, {"gpio_list":gpio_list }, context_instance=RequestContext(request))


def pins(request):
    try:
        iou = request.GET["iou"]
        cmd = request.GET["cmd"]
        pin = request.GET["pin"]
        lowhigh = request.GET.get("lowhigh", None)
        dic = {"msg":"x"}

        if iou == "in":
            if cmd == "unset":
                pass
            elif cmd == "refresh":
                pass
            else:
                raise BaseException('unknown cmd %s for %s' %(cmd,iou))

        elif iou == "out":
            if cmd == "unset":
                pass
            elif cmd == "refresh":
                pass
            elif cmd == "sethigh":
                pass
            elif cmd == "setlow":
                pass
            else:
                raise BaseException('unknown cmd %s for %s' %(cmd, iou))

        elif iou == "unset":
            if cmd == "setasinput":
                pass
            elif cmd == "setasoutput":
                pass
            else:
                raise BaseException('unknown cmd %s for %s' %(cmd, iou))

        else:
            raise BaseException('inout should be either in or out')

        dic['msg'] = "done, inout %s pin %s cmd %s" %(iou, pin, cmd)
        dic['lowhigh'] = ["high", "low"][datetime.now().minute%2]
        jdic= json_util.dumps(dic)
    except:
        err = traceback.format_exc()
        jdic = json.dumps({"error": err})

    return HttpResponse(jdic, content_type='application/json')







import numpy as np
import os, django
from datetime import datetime, timedelta
from time import sleep, time
import traceback
from bson import json_util

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except:
    print "!!!no RPI.GPIO module"


if False:
    # Discharge capacitor
    GPIO.setup(gpio_pin, GPIO.OUT)
    GPIO.output(gpio_pin, GPIO.LOW)
    sleep(2.)
    # Count loops until voltage across
    # capacitor reads high on GPIO
    i = 0
    GPIO.setup(gpio_pin, GPIO.IN)
    t0 = time()
    (GPIO.input(gpio_pin) == GPIO.LOW)
