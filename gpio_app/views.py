from website.processing import _get_conf
from gpio_app.process import set_para, get_para, board_bmc, export, unexport
import json
from bson import json_util
import traceback
from time import time

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from datetime import datetime

info = {
    "label": "GPIO",
    "desc": "Control and observe the GPIO (input output) pins of your rpi slave"
}

def home(request, template_name='gpio_app/home.html'):
    pins_ = _get_conf()['apps']['gpio_app']['pins']
    rev = {cf["pin"]: {"label": label, "desc": cf['desc']} for (label, cf) in pins_.iteritems()}

    gpio_list = []
    for pin, pin_bcm in board_bmc.iteritems():
        d = {"pin": pin}

        try: d["label"] = rev[pin]['label']
        except: d["label"] = "-"

        try: d["desc"] = rev[pin]['desc']
        except: d["desc"] = "-"

        try: d['iou'] = get_para(pin_bcm=pin_bcm, para="direction")
        except: d['iou'] = "unset"

        if d['iou'] != "unset": d['lowhigh'] = get_para(pin_bcm=pin_bcm, para="value")
        else: d['lowhigh'] = "x"
        gpio_list.append(d)
    return render_to_response(template_name, {"gpio_list": gpio_list, "info": info }, context_instance=RequestContext(request))


def _control(request):
    t1 = time()
    try:
        pins_ = _get_conf()['apps']['gpio_app']['pins']
        rev = {cf["pin"]: {"label": label, "desc": cf['desc']} for (label, cf) in pins_.iteritems()}

        pin = int(request.GET["pin"])
        iou = request.GET["iou"]
        cmd = request.GET["cmd"]
        lowhigh = request.GET.get("lowhigh", None)

        d = {"msg": "x"}

        try: d["label"] = rev[pin]['label']
        except: d["label"] = "-"

        try: d["desc"] = rev[pin]['desc']
        except: d["desc"] = "-"

        pin_bcm = board_bmc[pin]

        if iou == "in":
            if cmd == "unset":
                unexport(pin_bcm=pin_bcm)
                d['msg'] = "done unexporting"
            elif cmd == "refresh":
                pass #the variables are updates later on anyway
            else:
                raise BaseException('unknown cmd %s for %s' %(cmd,iou))

        elif iou == "out":
            if cmd == "unset":
                unexport(pin_bcm=pin_bcm)
            elif cmd == "refresh":
                pass #the variables are updates later on anyway
            elif cmd == "sethigh":
                set_para(pin_bcm=pin_bcm, para="value", value="1")
            elif cmd == "setlow":
                set_para(pin_bcm=pin_bcm, para="value", value="0")
            else:
                raise BaseException('unknown cmd %s for %s' %(cmd, iou))

        elif iou == "unset":
            if cmd == "setasinput":
                export(pin_bcm=pin_bcm)
                set_para(pin_bcm=pin_bcm, para="direction", value="in")
            elif cmd == "setasoutput":
                export(pin_bcm=pin_bcm)
                set_para(pin_bcm=pin_bcm, para="direction", value="out")
            else:
                raise BaseException('unknown cmd %s for %s' %(cmd, iou))

        else:
            raise BaseException('inout should be either in or out')

        d['pin'] = pin

        try: d['iou'] = get_para(pin_bcm=pin_bcm, para="direction")
        except: d['iou'] = "x"

        try: d['lowhigh'] = get_para(pin_bcm=pin_bcm, para="value")
        except:d['lowhigh'] = "x"

        t2 = time()

        d['msg'] = "done at %s, took %0.2f sec" %(datetime.now().strftime('%Y-%m-%d %H:%M %S'), (t2 - t1))

        datetime.utcnow()

        jdic= json_util.dumps(d)
    except:
        err = traceback.format_exc()
        jdic = json.dumps({"error": err})

    return HttpResponse(jdic, content_type='application/json')

def control(request):
    t1 = time()
    try:
        pin = int(request.GET["pin"])
        cmd = request.GET["cmd"]

        pin_bcm = board_bmc[pin]

        if cmd == "unset":
            unexport(pin_bcm=pin_bcm)
        elif cmd == "setasinput":
            export(pin_bcm=pin_bcm)
            set_para(pin_bcm=pin_bcm, para="direction", value="in")
        elif cmd == "setasoutput":
            export(pin_bcm=pin_bcm)
            set_para(pin_bcm=pin_bcm, para="direction", value="out")
        elif cmd == "sethigh":
            #only for output:
            set_para(pin_bcm=pin_bcm, para="value", value="1")
        elif cmd == "setlow":
            #only for output:
            set_para(pin_bcm=pin_bcm, para="value", value="0")
        elif cmd == "refresh":
            pass
        else:
            raise BaseException('cmd not recognised %s' % cmd)

        d = {}
        try: d['iou'] = get_para(pin_bcm=pin_bcm, para="direction")
        except: d['iou'] = "-"

        try: d['lowhigh'] = get_para(pin_bcm=pin_bcm, para="value")
        except:d['lowhigh'] = "-"

        t2 = time()
        d['msg'] = "done at %s, took %0.2f sec" %(datetime.now().strftime('%Y-%m-%d %H:%M %S'), (t2 - t1))

        jdic= json_util.dumps(d)
    except:
        err = traceback.format_exc()
        jdic = json.dumps({"error": err})

    return HttpResponse(jdic, content_type='application/json')

