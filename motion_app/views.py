import io
import json
import base64
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
import traceback

try: import picamera
except: print "!!could not import picamera"


def home(request, template_name='motion_app/home.html'):
    return render_to_response(template_name, {}, context_instance=RequestContext(request))

def snapshot(request):
    d = {}
    try:
        camera = picamera.PiCamera()
        buf = io.BytesIO()
        camera.capture(buf, format='jpeg')

        d['image'] = "data:image/png;base64," + base64.b64encode(buf.getvalue())
        camera.close()
        return HttpResponse(json.dumps(d), content_type='application/json')
    except:
        d["error"] = traceback.format_exc()
        print d["error"]
        return HttpResponse(json.dumps(d), content_type='application/json')
