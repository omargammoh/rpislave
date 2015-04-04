from django.shortcuts import render_to_response
from django.template import RequestContext

info = {
    "label": "BitTorrent-Sync",
    "desc": "Sync the data of the other apps with other devices"
}

def home(request, template_name='btsync_app/home.html'):
    btsync_server = 'http://' + request.get_host().lstrip('http://').split(':')[0] + ":9004"
    return render_to_response(template_name, {"info": info, "btsync_server":btsync_server}, context_instance=RequestContext(request))
