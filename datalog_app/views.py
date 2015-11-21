from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import json
from bson import json_util
from datalog_app.models import Reading
import traceback
from website.processing import get_conf
import numpy as np

info = {
    "label": "DATA-LOG",
    "desc": "Record data from RS485, i2c or spi devices"
}

conf = get_conf()
datalog_conf = conf['apps']['datalog_app']

def home(request, template_name='datalog_app/home.html'):
    return render_to_response(template_name, {"info": info}, context_instance=RequestContext(request))

def _getdata(start_id=None, end_id=None):
    """
    gets the data between and including start_id and end_id from the Readings table
    """
    if start_id is None: start_id = 0
    if end_id is None: end_id = 999999999999999
    obs = Reading.objects.filter(id__range=(start_id, end_id))
    if obs:
        mx = max([ob.id for ob in obs])
        mn = min([ob.id for ob in obs])
    else:
        mx = -1
        mn = -1
    return {'lis': [json_util.loads(ob.data) for ob in obs], 'mn':mn, 'mx':mx}

def _transform(data):
    """
    data is the parsed list of jsons
    """
    dic_trans_funs = {}
    for p_name, p_dic in datalog_conf['sensors'].iteritems():
        for pp in p_dic.get('pp',[]):
            d_name = "%s-%s" %(p_name, pp)
            if p_dic['type'] == "rs485":
                # Note: there is an extra lambda function in the line below that you might think is not neccessary, but it's important to make sure the p_dic parameters of the last iteration is not used
                if pp=="avg" or pp=="min" or pp=="max":
                    dic_trans_funs[d_name] = (lambda p_dic: (lambda x: (x*p_dic['m'] + p_dic['c'])))(p_dic)
                elif pp=="std":
                    dic_trans_funs[d_name] = (lambda p_dic: (lambda x: (x*p_dic['m'])))(p_dic)
            elif p_dic['type'] in ["mcp3008", "spi", "spi-ct"]:
                if pp=="avg" or pp=="min" or pp=="max":
                    dic_trans_funs[d_name] = (lambda p_dic: (lambda x: (x/1023.0 * p_dic['Vref'] * p_dic['m'] + p_dic['c'])))(p_dic)
                elif pp=="std":
                    dic_trans_funs[d_name] = (lambda p_dic: (lambda x: (x/1023.0 * p_dic['Vref'] * p_dic['m'])))(p_dic)
            else:
                pass

    data_t = []

    for dic in data:
        dic_t={}
        for k, v in dic.iteritems():
            #when this loops encounters the timestamp and cont , it leaves then as they are, thats why we have the get with default lambda x:x function
            dic_t[k] = dic_trans_funs.get(k, lambda x:x)(v)
        data_t.append(dic_t)

    return data_t

def getdata_transformed(request):
    try:
        jdic = json.dumps({'data': _transform(start_id=request.GET.get('start_id'), end_id=request.GET.get('end_id'))})
    except:
        err = traceback.format_exc()
        jdic = json.dumps({"error": err})
    return HttpResponse(jdic, content_type='application/json')

def _highchart(start_id, end_id):
    raw = _getdata(start_id=start_id, end_id=end_id)
    lis_doc = _transform(data=raw['lis'])

    lis_para = []
    for p_name, p_dic in datalog_conf['sensors'].iteritems():
        for pp in p_dic.get('pp',[]):
            lis_para.append("%s-%s" %(p_name, pp))

    dic_ser = {}
    if len(lis_doc):
        for doc in lis_doc :
            dt = doc["timestamp"]
            ### get things provided in the json
            for k in lis_para:
                v = doc.get(k)
                if v is not None:
                    #name = label + "-" + k
                    name = k
                    if not name in dic_ser:
                        dic_ser[name]=[]
                    dic_ser[name].append([dt, v])

    ylabels = ", ".join(set(['-'.join(k.split('-')[:-1]) for k in dic_ser.keys() if '-' in k]))
    lis_ser_hc = []

    colors = ['#427FED', '#FF0040', '#5dff4f', '#f3e877', '#8a8587', '#810040', '#beffe3']
    para_color = {}
    i = 0
    for k in sorted(dic_ser.keys()):
        v = dic_ser[k]
        dat = [["$Date.UTC(%s,%s,%s,%s,%s,%s)$" %(vv[0].year, vv[0].month-1, vv[0].day, vv[0].hour, vv[0].minute, vv[0].second), vv[1] if np.isfinite(vv[1]) else "$null$"] for vv in v]
        s_dic = {"name": k, "data": dat}

        para = '-'.join(k.split('-')[:-1])

        #color
        if para in para_color:
            s_dic["color"] = para_color[para]
        else:
            s_dic["color"] = colors[i%len(colors)]
            para_color[para] = colors[i%len(colors)]
            i += 1

        v = dic_ser[k]
        if k.endswith('-avg'):
            pass
        elif k.endswith('-std'):
            s_dic["dashStyle"] = 'dash'
        else:
            s_dic["dashStyle"] = 'shortDot'
        lis_ser_hc.append(s_dic)


    js = {
            "chart": {
                "type": 'line',
                "zoomType": 'x',
                "events": {
                    "load" : "$(function () {\
                        var series = this.series;\
                        setInterval(function () {\
                            highchart_update(series);\
                        }, 2000);\
                    })$"
                }
            },
            "title": {
                "text": ''
            },
            "xAxis": {
                "type": 'datetime',
                "dateTimeLabelFormats": { # don't display the dummy year
                    "month": '%e. %b',
                    "year": '%b'
                },
                "title": {
                    "text": 'Date'
                }
            },
            "yAxis": {
                "title": {
                    "text": ylabels
                }
                #,"min": 0
            },
            "tooltip": {
                "headerFormat": '<b>{series.name}</b><br>',
                "pointFormat": '{point.x:%e %b %H:%M}, {point.y:.2f}'
            },

            "plotOptions": {
                "line": {
                    "marker": {
                        "enabled": len(lis_doc) < 50
                    }
                }
            },
            "series": lis_ser_hc

    }

    return {'data': json_util.dumps(js).replace('$"', "").replace('"$', ""), 'mn':raw['mn'], 'mx':raw['mx']}

def highchart(request):
    try:
        jdic = json.dumps(_highchart(start_id=request.GET.get('start_id'), end_id=request.GET.get('end_id')))
    except:
        err = traceback.format_exc()
        jdic = json.dumps({"error": err})
    return HttpResponse(jdic, content_type='application/json')

def highchart_update(request):
    raw = _getdata(start_id=request.GET.get('start_id'), end_id=request.GET.get('end_id'))
    lis_doc = _transform(data=raw['lis'])

    lis_para = []
    for p_name, p_dic in datalog_conf['sensors'].iteritems():
        for pp in p_dic.get('pp', []):
            lis_para.append("%s-%s" %(p_name, pp))

    dic_ser = {}
    if len(lis_doc):
        for doc in lis_doc :
            dt = doc["timestamp"]
            ### get things provided in the json
            for k in lis_para:
                v = doc.get(k)
                if v is not None:
                    #name = label + "-" + k
                    name = k
                    if not name in dic_ser:
                        dic_ser[name]=[]
                    dic_ser[name].append(["Date.UTC(%s,%s,%s,%s,%s,%s)" %(dt.year, dt.month-1, dt.day, dt.hour, dt.minute, dt.second), v])

    try:
        jdic = json.dumps({'data': dic_ser, "mn": raw['mn'], "mx": raw['mx']})
    except:
        err = traceback.format_exc()
        jdic = json.dumps({"error": err})
    return HttpResponse(jdic, content_type='application/json')

def highresmcp3008(request):
    try:
        import spidev
        import time
        n = min(int(request.GET.get("n", 200)), 2000)
        channel = int(request.GET.get("channel", 0))

        spi_client = spidev.SpiDev()
        spi_client.open(0, 0)

        def _read_spi(spi, channel):
            adc = spi.xfer2([1,(8+channel)<<4,0])
            data = ((adc[1]&3) << 8) + adc[2]
            return data

        t1 = time.time()
        lis_v = [_read_spi(spi_client, channel) for i in range(n)]
        t2 = time.time()
        sec = (t2 - t1)
        spi_client.close()

        dic = {'lis':lis_v, "period": sec}
        jdic= json_util.dumps(dic)
    except:
        err = traceback.format_exc()
        jdic = json.dumps({"error": err})

    return HttpResponse(jdic, content_type='application/json')

