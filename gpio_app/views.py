from website.processing import _get_conf
import json

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from datetime import datetime

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD)
except:
    print "!!could not import RPi.GPIO"

def detect_iou(pin):
    try:
        v = GPIO.input(pin)
        try:
            GPIO.output(pin, v)
            return "output"
        except:
            return "input"
    except:
        return "unset"


def home(request, template_name='gpio_app/home.html'):
    pins_conf = _get_conf()['apps']['gpio_app']['pins_conf']
    rev = {cf["pin"]: {"label": label, "desc": cf['desc']} for (label, cf) in pins_conf.iteritems()}
    gpio_pins = sorted(set([4,16,27,23,22,24,25,5,6,12,13,19,4,26,20,21]))

    gpio_list = []
    for pin in gpio_pins:
        d = {"pin": pin}

        try: d["label"] = rev[pin]['label']
        except: d["label"] = "-"

        try: d["desc"] = rev[pin]['desc']
        except: d["desc"] = "-"

        d['iou'] = detect_iou(pin)

        if d['iou'] != "unset":
            d['lowhigh'] = GPIO.input(gpio_pin)

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



if False:


    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD)

    gpio_pin = 11
    GPIO.input(gpio_pin) == GPIO.LOW

    GPIO.setup(gpio_pin, GPIO.IN)

    GPIO.setup(gpio_pin, GPIO.OUT)
    GPIO.output(gpio_pin, GPIO.input(gpio_pin))
    # Discharge capacitor
    sleep(2.)
    # Count loops until voltage across
    # capacitor reads high on GPIO
    i = 0
    t0 = time()
    (GPIO.input(gpio_pin) == GPIO.LOW)

