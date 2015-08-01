import pymongo
import traceback

from datetime import datetime
from time import sleep, time

import os, django
from bson import json_util

from website.processing import _get_conf

from django.db.models import get_app, get_models

def _prepare_django():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'website.settings'
    django.setup()

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


def _send_model_data(model, keep_period, db, conf_label, app_name):
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
    cnt = {'del': 0, 'send': 0}
    for ob in model.objects.all():

        #if there is a meta data then that's great
        try:
            meta = json_util.loads(ob.meta)
            sent = meta['sent']
        except:
            meta = {}
            sent = 'false'

        #handle the unsent data
        try:
            #if not sent
            if sent == 'false':

                #send it
                col = db[".".join([conf_label_san, app_name, model_name])]
                jdata = json_util.loads(ob.data)
                col.insert(jdata)

                #mark it as sent
                meta['sent'] = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                ob.meta = json_util.dumps(meta)
                ob.save()
                cnt['send'] += 1
            #else if sent already,
            else:
                #do nothing
                pass
        except:
            print '>> datasend: !!sending data to mongodb failed'
            print traceback.format_exc()

        #handle the sent data(do not delete data from website because config is there)
        meta = json_util.loads(ob.meta)
        if (not ("nodelete" in model_mode)) and len(meta['sent']) == 4+2+2+2+2+2 and meta['sent'].isdigit():
            sentdate = datetime.strptime(meta['sent'], "%Y%m%d%H%M%S")
            now = datetime.utcnow()
            #if this data point has been there for a short time, keep it
            if (now - sentdate).total_seconds() < keep_period:
                pass
            #if this data point has been there for a long time, delete it
            else:
                ob.delete()
                cnt['del'] += 1
    t2 = time()
    print '>> datasend: model %s done, took %s sec, %s, mode %s' % (model_name, round(t2 - t1, 3), cnt, model_mode)

def _send_app_data(app_name, keep_period, db, conf_label):
    app = get_app(app_name)
    for model in get_models(app):
        print ">> datasend: working on model %s" % model.__name__
        _send_model_data(model=model, keep_period=keep_period, db=db, conf_label=conf_label, app_name=app_name)

def main(send_period=60*2, keep_period=60*60*24*7, app_list=None):
    '''
    take data from db and send it to mongodb, if successfull, mark data as successfull and delete after a while (except for the website app)

    send_period: every how often should i send?
    keep_period: how long should i wait before i delete the sent items
    app_list: a list of apps to send their data, if None, then all apps in the conf will be done
    '''

    _prepare_django()

    conf = _get_conf()

    if app_list is None: app_list = conf['apps'].keys()
    mongo_address = conf.get('mongo_address')
    if mongo_address is None:
        return None

    app_list.append("website")

    conf_label = conf['label']
    connected = False
    sleep(10)
    i = 0
    while True:
        print ">> datasend: loop, i=%s" % i
        #waiting to have a connection
        t1 = time()
        j = 0

        try:
            connected = client.alive()
        except:
            connected = False

        while not connected:
            try:
                client = pymongo.MongoClient(mongo_address)
                db = client.get_default_database()
            except:
                pass

            try:
                connected = client.alive()
            except:
                connected = False

            if not connected:
                #keep trying
                retryin = min(20 * (j + 1), 60*10)
                print ">> datasend: !!couldnt connect at j=%s, retrying in %s" % (j, retryin)
                sleep(retryin)
            j += 1
        t2 = time()
        print '>> datasend:    connected to mongo, took %s sec, and %s trials to connect' % (round(t2 - t1, 3), j)

        #when connection is good
        if connected:
            # send the data of the apps
            for app_name in app_list:
                try:
                    print ">> datasend: working on app %s" % app_name
                    _send_app_data(app_name=app_name, keep_period=keep_period, db=db, conf_label=conf_label)
                except:
                    print '>> datasend: !! _send_app_data for %s failed' % app_name
                    print traceback.format_exc()

        if connected:
            try:
                try:
                    import dateutil.parser
                    import pytz
                    import urllib2
                    resp = urllib2.urlopen('http://www.timeapi.org/utc/now', timeout=15).read().strip()
                    dt_internet = dateutil.parser.parse(resp).astimezone(pytz.utc)
                    time_error = (datetime.utcnow().replace(tzinfo=pytz.utc) - dt_internet).total_seconds()
                except:
                    time_error = "-"
                    pass

                li_conf = db['latestinfo']
                li_conf.update(
                   { "label": conf_label },
                   {
                      "label": conf_label,
                      "dt": datetime.utcnow(),
                      "send_period": send_period,
                      "time_error": time_error
                   },
                   upsert = True
                )
                print ">> datasend: sent latest info"
            except:
                print ">> !!datasend: error sending latest info"


        i += 1
        #waiting for next sending time
        print ">> datasend: next iteration is after %s sec" %send_period
        sleep(send_period)

    return None
