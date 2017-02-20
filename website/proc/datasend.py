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

from website.processing import get_conf, fix_malformed_db

from django.db.models import get_app, get_models
from website.processing import Timeout

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

def _send_model_data(model, keep_period, conf_label, app_name, perm, master_url, delete_cycle):
    """
    model: the actual model object
    """
    tm = time()
    t1 = time()

    model_name = model.__name__

    if hasattr(model, "mode"):
        model_mode = model.mode
    else:
        model_mode = ""

    conf_label_san = sanitize_colname(conf_label)

    cnt = {'send-ok': 0, 'send-fail': 0, "send-markfail": 0, "send-cantloads": 0, "send-skipfordeletecycle":0,
           'dontdelyet-ok': 0,
           'nodel-ok': 0,
           'del-ok': 0, 'del-fail': 0,
           'x': 0, 'no-idea': 0, 'exception': 0}

    bulk_sendlist = []
    bulk_thres = 20

    #loop over each datapoint
    try:
        list_ob = model.objects.all()
        len_total = len(list_ob)
    except: #if there is a problem reading the whole model, loop over and get the good readings only
        print ">>datasend: !!!error in getting all objects of model %s, trying to get the good part of the data" %model_name
        list_ob=[]
        ids = model.objects.values_list('id', flat=True)
        for i in ids:
            try:
                list_ob.append(model.objects.get(id=i))
            except:
                print "model %s id %s failed!!!!!!! continuing" %(model_name,i)
                print traceback.format_exc()
        len_total = len(list_ob)



    t2 = time()
    bulk_thres_estimated = False
    for i, ob in enumerate(list_ob):

        #if there is a meta data then that's great
        try:
            meta = json_util.loads(ob.meta)
            sent = str(meta['sent']).lower()
        #else if no meta data, create them, dont save it yet
        except:
            #default values when no meta is present
            meta = {'sent': "false"}
            sent = 'false'

        #handle the datapoint
        try:
            #if not sent
            if sent == 'false':
                if not delete_cycle:
                    #add to bulk to be sent later
                    bulk_sendlist.append(ob)
                else:
                    #skipping for the delete cycle:
                    cnt['send-skipfordeletecycle'] += 1

                #estimate the max number of datapoints that can be sent
                if not bulk_thres_estimated:
                    bulk_thres_estimated = True
                    try:
                        test_str = urllib.urlencode([('x', str(ob.data))])
                        max_length = 32000. #max url length the server can take
                        bulk_thres = min(500, int(max_length/len(test_str) * 0.7)) #0.7 is safety margin
                        print ">> datasend: decided on bulk thresold of %s" %bulk_thres
                    except:
                        print ">> datasend: could not decide on bulk length"
                        pass


            #elif sent
            elif len(str(meta['sent'])) == 4+2+2+2+2+2 and str(meta['sent']).isdigit():
                #nodelete
                if "nodelete" in model_mode:
                    cnt['nodel-ok'] += 1
                #deletable
                else:
                    sentdate = datetime.strptime(meta['sent'], "%Y%m%d%H%M%S")
                    now = datetime.utcnow()
                    #if this data point has been there for a short time, keep it
                    if (now - sentdate).total_seconds() < keep_period:
                        cnt['dontdelyet-ok'] += 1

                    #if this data point has been there for a long time, delete it
                    else:
                        try:
                            ob.delete()
                            cnt['del-ok'] += 1
                        except:
                            cnt['del-fail'] += 1

            #no idea whats going on
            else:
                cnt['no-idea'] += 1

        #if exception in handeling the datapoint write the exception in meta data
        except:

            tb = traceback.format_exc()
            if "DatabaseError: database disk image is malformed" in str(tb):
                print "datasend: !!!database is malformed, fixing it"
                fix_malformed_db()
            print tb
            print '>> datasend: !!handling datapoint failed'
            cnt['exception'] += 1

            try:
                #mark and save the error
                print '>> datasend: !!model %s object id %s handling failed ' %(model_name, ob.id)
                meta['error'] = str(tb)
                meta['dt_error'] = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                ob.meta = json_util.dumps(meta)
                ob.save()
                cnt['exception'] += 1

            #sending of bulk failed
            except:
                print ">> datasend: !!recording error failed"
                pass


        #bulk send threshold is reached  - or - last item, - then -  must send the bulk
        if (len(bulk_sendlist) >= bulk_thres) \
                or (i+1 == len_total and len(bulk_sendlist) != 0):

            #try to send the bulk
            try:
                col_name = ".".join([conf_label_san, app_name, model_name])
                #try to send the data and save in the meta that it is sent

                #send it though rpi-master
                if perm is not None:
                    good_data_points = []
                    good_model_points = []
                    for bulk_item in bulk_sendlist:
                        #see if its a parsable point
                        try:
                            #check if data is loadable
                            parsed_point = json_util.loads(bulk_item.data)
                            #append
                            good_data_points.append(parsed_point)
                            good_model_points.append(bulk_item)
                        #this is a bad point
                        except:
                            print ">> datasend: !! cant loads datapoint for sending"
                            cnt['send-cantloads'] += 1
                            #todo: save error

                    #get the data as string
                    data = json_util.dumps(good_data_points)

                    #data = '{"Tamb-max": 0.0, "Tamb-min": 0.0, "timestamp": {"$date": 1439128980000}, "Tamb-avg": 0.0}'
                    #perm = "_perm=write&_slave=development+and+testing&_sig=b901abde"
                    #col_name='development_and_testing_2.datalog_app.Reading'
                    full_url = master_url + perm + "&para=fwd_to_db&" + urllib.urlencode([('col_name', col_name), ('data', data)])#http://rpi-master.com/api/slave/?_perm=write&_slave=development+and+testing&_sig=b901abde&para=fwd_to_db&data=%7B%22Tamb-max%22%3A+0.0%2C+%22Tamb-min%22%3A+0.0%2C+%22timestamp%22%3A+%7B%22%24date%22%3A+1439128980000%7D%2C+%22Tamb-avg%22%3A+0.0%7D
                    print ">> datasend: sending %s datapoints..." %len(good_data_points)
                    resp = urllib2.urlopen(full_url, timeout=60).read().strip()

                    #server does not confirm everything is ok
                    if not str(json_util.loads(resp)['data']).lower()=='true':
                        print ">> datasend: !!failed sending group with %s items (url len %s)" %(len(good_data_points), len(full_url))
                        raise BaseException('server did not return data:true thing')
                    #server confirms everything is ok
                    else:
                        print ">> datasend: successfully sent %s items (url len %s)" %(len(good_data_points), len(full_url))
                        for ob in good_model_points:
                            try:
                                meta = json_util.loads(ob.meta)
                            except:
                                meta = {}

                            try:
                                #mark it as sent
                                meta['sent'] = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                                ob.meta = json_util.dumps(meta)
                                ob.save()
                                cnt['send-ok'] += 1
                            except:
                                cnt['send-markfail'] += 1
                                print ">> datasend: !!!!failed to mark point as sent!, this might lead to duplicates in the remote db"

                else:
                    print ">> datasend: dont know how to send data"
                    raise BaseException ('dont know how to send this')

            #expection in sending the data or saving the meta
            except:
                try:
                    #mark it as not sent
                    ex = str(traceback.format_exc())
                    for ob in good_model_points:
                        ob.meta = json_util.dumps({'sent': "false", 'error': ex, 'dt_error': datetime.utcnow().strftime('%Y%m%d%H%M%S')})
                        ob.save()
                        cnt['send-fail'] += 1
                    print '>> datasend: !!model %s object id %s sending failed ' %(model_name, ob.id)

                #sending of bulk failed
                except:
                    pass

            #resetting bulk sendliist
            bulk_sendlist=[]

        #print some info every while
        if time() - tm > 10.:
            tm = time()
            print ">> datasend: still working on model %s since %s min, %s" %(model_name, round(tm - t1, 1)/60.,{k:v for (k,v) in cnt.iteritems() if v != 0})


    t3 = time()
    print '>> datasend: model %s done, took %s+%s sec, mode %s, %s' % (model_name, round(t2 - t1, 3), round(t3 - t2, 3), model_mode, {k:v for (k,v) in cnt.iteritems() if v != 0})

def _send_app_data(app_name, keep_period, conf_label, perm, master_url, delete_cycle):
    app = get_app(app_name)
    for model in get_models(app):
        print ">> datasend: working on model %s" % model.__name__
        try:
            _send_model_data(model=model, keep_period=keep_period, conf_label=conf_label, app_name=app_name, perm=perm, master_url=master_url, delete_cycle=delete_cycle)
        except:
            #if dataabase is malformed, then try to fix it
            #
            tb = traceback.format_exc()
            print '%s>> datasend: !!model %s failed' %(tb, model.__name__)

            if "DatabaseError: database disk image is malformed" in str(tb):
                print "datasend: !!!database is malformed for %s, trying to fix it" % model.__name__
                fix_malformed_db()


def _get_time_error():
    """
    gets time error in seconds
    """
    try:
        with Timeout(seconds=16):
            t1 = time()

            resp = urllib2.urlopen(r'https://script.google.com/macros/s/AKfycbyd5AcbAnWi2Yn0xhFRbyzS4qMq1VucMVgVvhul5XqS9HkAyJY/exec', timeout=15).read().strip()
            jresp = json_util.loads(resp)
            if not (jresp['timezone'].lower()=="utc"):
                print ">> timecheck: !!!Time error might not be UTC"
                raise BaseException('')
            t2 = time()
            time_needed = (t2 - t1)

            correction = time_needed/2.

            dt_internet = dateutil.parser.parse(jresp['fulldate']).astimezone(pytz.utc)
            seconds = (datetime.utcnow().replace(tzinfo=pytz.utc) - dt_internet).total_seconds() - correction
            return seconds
    except:
        print ">> datasend: could not get time_error"
        return "-"











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
        app_list = conf.get('apps', {}).keys()
    app_list.append("website")

    mongo_address = conf.get('mongo_address')
    perm = conf.get('perm')#looks like this "_perm=write&_slave=development+and+testing&_sig=b901ande"
    conf_label = conf['label']
    master_url = conf.get('master_url', settings.DEFAULT_MASTER_URL)


    if (mongo_address is None) and (perm is None):
        return None

    sleep(10)
    i = 0

    time_interneton = time()
    need_delete_cycle_soon = False

    if perm is not None:
        while True:
            print ">> datasend: loop, i=%s" % i

            internet_ison = check_internet()

            need_delete_cycle_now = not internet_ison \
                                        and need_delete_cycle_soon \
                                        and ((time() - time_interneton) > (keep_period)) #go through the database to delete items and not send
            if need_delete_cycle_now:
                print ">> datasend: running a delete cycle"
                need_delete_cycle_soon = False

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
                    full_url = master_url + perm + "&para=fwd_to_db&" + urllib.urlencode([('col_name', 'latestinfo'), ('data', data_str)])#http://rpi-master.com/api/slave/?_perm=write&_slave=development+and+testing&_sig=b901abde&para=fwd_to_db&data=%7B%22Tamb-max%22%3A+0.0%2C+%22Tamb-min%22%3A+0.0%2C+%22timestamp%22%3A+%7B%22%24date%22%3A+1439128980000%7D%2C+%22Tamb-avg%22%3A+0.0%7D
                    #print ">> datasend: %s" %full_url
                    resp = urllib2.urlopen(full_url, timeout=15).read().strip()

                    if not str(json_util.loads(resp)['data']).lower() == 'true':
                        print 'fail', resp
                        raise BaseException ('server did not return data:true')


                    print ">> datasend: sent latest info"
                except:
                    print "%s>> !!datasend: error sending latest info " %traceback.format_exc()

            if internet_ison or need_delete_cycle_now:
                # send the data of the apps
                for app_name in app_list:
                    try:
                        if need_delete_cycle_now:
                            print ">> datasend: delete cycle..."
                        print ">> datasend: working on app %s (perm)" % app_name
                        _send_app_data(app_name=app_name, keep_period=keep_period, conf_label=conf_label, perm=perm, master_url=master_url, delete_cycle=need_delete_cycle_now)
                    except:
                        print traceback.format_exc()
                        print '>> datasend: !! _send_app_data for %s failed' % app_name
            else:
                print ">> datasend: internet is off"

            i += 1

            #waiting for next sending time
            if internet_ison:
                need_delete_cycle_soon = True
                time_interneton = time()


            if internet_ison:
                #if internet is on, wait for send_period
                sleeptime = send_period
            else:
                #if internet is of, wait less time so that we connect quickly when internet is present
                sleeptime = send_period/4

            print ">> datasend: next iteration is after %s sec" %sleeptime
            sleep(sleeptime)


    return None
