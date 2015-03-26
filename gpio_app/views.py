from mng.processing import MP, _get_conf
import gpio_app.process
import json

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from datetime import datetime
gpio_pins = sorted(set([4,16,27,23,22,24,25,5,6,12,13,19,4,26,20,21]))
def home(request, template_name='gpio_app/home.html'):
    gpio_list = [{"pin":i, "io":["input", 'output'][i%2], "status":"HIGH"} for i in gpio_pins]
    return render_to_response(template_name, {"gpio_list":gpio_list }, context_instance=RequestContext(request))



def pins(request):
    try:
        inout = request.GET["inout"]
        cmd = request.GET["cmd"]
        pin = request.GET["pin"]
        lowhigh = request.GET.get("lowhigh", None)
        dic = {"msg":"x"}

        if inout == "in":
            if cmd == "setasoutput":
                pass
            elif cmd == "refresh":
                pass
            else:
                raise BaseException('unknown cmd %s for %s' %(cmd,inout))

        elif inout == "out":
            if cmd == "setasinput":
                pass
            elif cmd == "refresh":
                pass
            elif cmd == "sethigh":
                pass
            elif cmd == "setlow":
                pass
            else:
                raise BaseException('unknown cmd %s for %s' %(cmd,inout))

        else:
            raise BaseException('inout should be either in or out')

        dic['msg'] = "done, inout %s pin %s cmd %s" %(inout, pin, cmd)
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


def _Vs(Vth, t, RC, Rratio):
    ret = Vth / (1 + (Rratio - 1.) * np.exp( -1. * t / RC))
    return ret

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

