from common import MP
import send.process
import traceback
import json
from django.http import HttpResponse

def manage(request):
    try:
        mp = MP(name='send', target=send.process.main, request=request)
        mp.process_command()
        dic = json.dumps(mp.dic)
    except:
        err = traceback.format_exc()
        dic = json.dumps({"error": err})
    return HttpResponse(dic, content_type='application/json')
