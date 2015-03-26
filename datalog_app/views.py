from django.shortcuts import render_to_response
from django.template import RequestContext

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import json
from bson import json_util
from datalog_app.models import Reading
import traceback


def home(request, template_name='datalog_app/home.html'):
    return render_to_response(template_name, {}, context_instance=RequestContext(request))



def recentdata(request):
    try:
        dic = {}
        dic["the last 20 recorded stamps in local DB"] = [str({'data':json_util.loads(ob.data), 'meta':json_util.loads(ob.meta)}) for ob in Reading.objects.all().order_by('-id')[:20]]
        jdic= json_util.dumps(dic)
    except:
        err = traceback.format_exc()
        jdic = json.dumps({"error": err})

    return HttpResponse(jdic, content_type='application/json')

