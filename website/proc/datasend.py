import traceback
import dateutil.parser
import pytz
import urllib2
from django.conf import settings

from datetime import datetime
from time import sleep, time
import urllib

import os, django
from bson import json_util

from website.processing import get_conf

from django.db.models import get_app, get_models

def _prepare_django():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'website.settings'
    django.setup()

def check_internet():
    """
    this is a duplicate from status.py
    """
    try:
        t1 = time()
        _ = urllib2.urlopen('http://www.google.com', timeout=10)
        time_needed = (time() - t1)
        internet_ison = True
        print ">> datasend: internet accessible, needed %s sec to ping google" % time_needed
    except:
        internet_ison = False
    return internet_ison

def sanitize_colname(label):
    if label == "":
        return ""
    if not(label[0].isalpha() or label[0] == "_"):
        label = "_" + label
    if label.startswith('system.') or label.startswith('objectlabs-system.'):
        label = "_" + label

    label = label.replace(' ', '_').lower()
    label = "".join([l if (l.isdigit() or l.isalpha() or l in ['_', '-', '.']) else '_' for l in label])
    if len(label)>50:
        label=label[:50]
    return label
    #The name you choose must begin with a letter or underscore and must not begin with 'system.' or 'objectlabs-system.'
    #. It also must have fewer than 80 characters and cannot have any spaces or special characters (hyphens, underscores and periods are OK) in it.

def _send_model_data(model, keep_period, db, conf_label, app_name, perm):
    """
    model: the actual model object
    """
    t1 = time()
    model_name = model.__name__

    if hasattr(model, "mode"):
        model_mode = model.mode
    else:
        model_mode = ""

    conf_label_san = sanitize_colname(conf_label)
    cnt = {'send-ok': 0, 'send-already': 0, 'send-fail': 0, 'del-nodel':0, 'del-ok':0, 'del-notyet':0, 'x': 0}

    #loop over each datapoint
    for ob in model.objects.all():

        #if there is a meta data then that's great
        try:
            meta = json_util.loads(ob.meta)
            sent = str(meta['sent']).lower()
        #else if no meta data, create them, dont save it yet
        except:
            meta = {}
            sent = 'false'

        #handle the unsent data
        try:
            #if not sent
            if sent == 'false':
                col_name = ".".join([conf_label_san, app_name, model_name])
                #try to send the data and save in the meta that it is sent
                try:
                    #send it though rpi-master
                    if perm is not None:

                        # this is to make sure the string is bson string and to remove any unnecessary spaces such as the ones found in config
                        data = json_util.dumps(json_util.loads(ob.data))

                        #data = '{"Tamb-max": 0.0, "Tamb-min": 0.0, "timestamp": {"$date": 1439128980000}, "Tamb-avg": 0.0}'
                        #perm = "_perm=write&_slave=development+and+testing&_sig=b901abde"
                        #col_name='development_and_testing_2.datalog_app.Reading'
                        full_url = settings.BASE_URL + perm + "&para=fwd_to_db&" + urllib.urlencode([('col_name', col_name), ('data', data)])#http://rpi-master.com/api/slave/?_perm=write&_slave=development+and+testing&_sig=b901abde&para=fwd_to_db&data=%7B%22Tamb-max%22%3A+0.0%2C+%22Tamb-min%22%3A+0.0%2C+%22timestamp%22%3A+%7B%22%24date%22%3A+1439128980000%7D%2C+%22Tamb-avg%22%3A+0.0%7D
                        resp = urllib2.urlopen(full_url, timeout=15).read().strip()

                        if not str(json_util.loads(resp)['data']).lower()=='true':
                            print 'fail'
                            raise BaseException ('server did not return data:true thing')

                    #or send it directly to db
                    elif db is not None:
                        col = db[col_name]
                        jdata = json_util.loads(ob.data)
                        col.insert(jdata)

                    else:
                        raise BaseException ('dont know how to send this')

                    #mark it as sent
                    meta['sent'] = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                    ob.meta = json_util.dumps(meta)
                    ob.save()
                    cnt['send-ok'] += 1

                #expection in sending the data or saving the meta
                except:
                    #mark it as not sent
                    meta['sent'] = "false"
                    meta['error'] = str(traceback.format_exc())
                    meta['dt_error'] = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                    ob.meta = json_util.dumps(meta)
                    ob.save()
                    cnt['send-fail'] += 1
                    print '>> datasend: !!model %s object id %s sending failed ' %(model_name, ob.id)


            #else if sent already,
            else:
                cnt['send-already'] += 1
                #do nothing
                pass
        #if exception in handeling unsent data
        except:
            print '>> datasend: !!sending data failed'
            print traceback.format_exc()
            cnt['x'] += 1

        #handle the sent data(do not delete data from website because config is there)
        try:
            meta = json_util.loads(ob.meta)
        except:
            meta = {'sent': "false"}

        # the part (type(meta['sent']) is str) is needed because previously there was meta['send'] = False
        if (not ("nodelete" in model_mode)) and (type(meta['sent']) is str) and len(meta['sent']) == 4+2+2+2+2+2 and meta['sent'].isdigit():
            sentdate = datetime.strptime(meta['sent'], "%Y%m%d%H%M%S")
            now = datetime.utcnow()
            #if this data point has been there for a short time, keep it
            if (now - sentdate).total_seconds() < keep_period:
                cnt['del-notyet'] += 1

            #if this data point has been there for a long time, delete it
            else:
                ob.delete()
                cnt['del-ok'] += 1
        else:
            cnt['del-nodel'] += 1

        #print some info every while
        if (cnt['send-ok']+cnt['send-fail']+cnt['del-ok']+cnt['x'] + 1) %30 == 0: # +1  so that it doesnt print when zero
            print ">> datasend: still processing the model %s, %s" %(model_name, cnt)


    t2 = time()
    print '>> datasend: model %s done, took %s sec, %s, mode %s' % (model_name, round(t2 - t1, 3), cnt, model_mode)

def _send_app_data(app_name, keep_period, db, conf_label, perm):
    app = get_app(app_name)
    for model in get_models(app):
        print ">> datasend: working on model %s" % model.__name__
        try:
            _send_model_data(model=model, keep_period=keep_period, db=db, conf_label=conf_label, app_name=app_name, perm=perm)
        except:
            print '>> datasend: !!model %s failed %s' %(model.__name__, traceback.format_exc())

def _get_time_error():
    try:
        resp = urllib2.urlopen('http://www.timeapi.org/utc/now', timeout=15).read().strip()
        dt_internet = dateutil.parser.parse(resp).astimezone(pytz.utc)
        time_error = (datetime.utcnow().replace(tzinfo=pytz.utc) - dt_internet).total_seconds()
    except:
        time_error = "-"
        pass
    return time_error

def main(send_period=60*2, keep_period=60*60*12, app_list=None):
    '''
    take data from db and send it to mongodb, if successfull, mark data as successfull and delete after a while (except for the website app)

    send_period: every how often should i send?
    keep_period: how long should i wait before i delete the sent items
    app_list: a list of apps to send their data, if None, then all apps in the conf will be done
    '''

    _prepare_django()

    conf = get_conf()

    if app_list is None:
        app_list = conf['apps'].keys()
    app_list.append("website")

    mongo_address = conf.get('mongo_address')
    perm = conf.get('perm')#looks like this "_perm=write&_slave=development+and+testing&_sig=b901ande"
    conf_label = conf['label']

    if (mongo_address is None) and (perm is None):
        return None

    sleep(10)
    i = 0

    if perm is not None:
        while True:
            print ">> datasend: loop, i=%s" % i

            internet_ison = check_internet()

            if internet_ison:
                #update the latestinfo collection
                try:
                    time_error = _get_time_error()

                    data_js = {
                              #"label": conf_label,
                              #"dt": datetime.utcnow(),
                              #"send_period": send_period,
                              "time_error": time_error
                           }
                    data_str = json_util.dumps(data_js)


                    #http://rpi-master.com/api/slave/
                        # ?_perm=write&_slave=development+and+testing&_sig=b901abde
                        # &para=fwd_to_db
                        # &data=%7B%22Tamb-max%22%3A+0.0%2C+%22Tamb-min%22%3A+0.0%2C+%22timestamp%22%3A+%7B%22%24date%22%3A+1439128980000%7D%2C+%22Tamb-avg%22%3A+0.0%7D
                    full_url = settings.BASE_URL + perm + "&para=fwd_to_db&" + urllib.urlencode([('col_name', 'latestinfo'), ('data', data_str)])#http://rpi-master.com/api/slave/?_perm=write&_slave=development+and+testing&_sig=b901abde&para=fwd_to_db&data=%7B%22Tamb-max%22%3A+0.0%2C+%22Tamb-min%22%3A+0.0%2C+%22timestamp%22%3A+%7B%22%24date%22%3A+1439128980000%7D%2C+%22Tamb-avg%22%3A+0.0%7D
                    #print ">> datasend: %s" %full_url
                    resp = urllib2.urlopen(full_url, timeout=15).read().strip()

                    if not str(json_util.loads(resp)['data']).lower() == 'true':
                        print 'fail', resp
                        raise BaseException ('server did not return data:true')


                    print ">> datasend: sent latest info"
                except:
                    print ">> !!datasend: error sending latest info %s" %traceback.format_exc()

                # send the data of the apps
                for app_name in app_list:
                    try:
                        print ">> datasend: working on app %s (perm)" % app_name
                        _send_app_data(app_name=app_name, keep_period=keep_period, db=None, conf_label=conf_label, perm=perm)
                    except:
                        print '>> datasend: !! _send_app_data for %s failed' % app_name
                        print traceback.format_exc()
            else:
                print ">> datasend: internet is off"

            i += 1
            #waiting for next sending time
            print ">> datasend: next iteration is after %s sec" %send_period
            sleep(send_period)

    return None
