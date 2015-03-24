from mng.processing import MP
import record.process
import traceback
import json

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse


def home(request, template_name='record/home.html'):
    return render_to_response(template_name, {}, context_instance=RequestContext(request))

def manage(request):
    try:
        mp = MP(name='record', target=record.process.main, request=request)
        mp.process_command()
        dic = json.dumps(mp.dic)
    except:
        err = traceback.format_exc()
        dic = json.dumps({"error": err})
    return HttpResponse(dic, content_type='application/json')
