from website.processing import _get_conf
from gpio_app.process import set_para, get_para, board_bmc
import json

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from datetime import datetime

def home(request, template_name='gpio_app/home.html'):
    pins_conf = _get_conf()['apps']['gpio_app']['pins_conf']
    rev = {cf["pin"]: {"label": label, "desc": cf['desc']} for (label, cf) in pins_conf.iteritems()}

    gpio_list = []
    for pin, pin_bcm in board_bmc.iteritems():
        d = {"pin": pin}

        try: d["label"] = rev[pin]['label']
        except: d["label"] = "-"

        try: d["desc"] = rev[pin]['desc']
        except: d["desc"] = "-"

        d['iou'] = get_para(pin_bcm=pin_bcm, para="direction")

        if d['iou'] != "unset":
            d['lowhigh'] = get_para(pin_bcm=pin_bcm, para="value")

        gpio_list.append(d)
    print gpio_list
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

