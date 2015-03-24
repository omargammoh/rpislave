from mng.processing import MP
import datasend_app.process
import traceback
import json
from django.http import HttpResponse

def manage(request):
    try:
        mp = MP(name='datasend_app', target=datasend_app.process.main, request=request)
        mp.process_command()
        dic = json.dumps(mp.dic)
    except:
        err = traceback.format_exc()
        dic = json.dumps({"error": err})
    return HttpResponse(dic, content_type='application/json')
