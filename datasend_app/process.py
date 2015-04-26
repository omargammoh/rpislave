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

def _send_model_data(model, keep_period, db, conf_label, app_name):
    """
    model: the actual model object
    """
    t1 = time()
    model_name = model.__name__
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
                col = db["%s_%s_%s" %(conf_label, app_name, model_name)]
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
            print '    !!sending data to mongodb failed'
            print traceback.format_exc()

        #handle the sent data(do not delete data from website because config is there)
        meta = json_util.loads(ob.meta)
        if app_name != "website" and len(meta['sent']) == 4+2+2+2+2+2 and meta['sent'].isdigit():
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
    print '    sent model data for %s, took %s sec to process db with %s' % (model_name, round(t2 - t1, 3), cnt)


def _send_app_data(app_name, keep_period, db, conf_label):
    app = get_app(app_name)
    for model in get_models(app):
        print "_send_model_data for %s" % model.__name__
        _send_model_data(model=model, keep_period=keep_period, db=db, conf_label=conf_label, app_name=app_name)


def main(send_period, keep_period, mongo_address, app_list=None):
    '''
    send_period: every how often should i send?
    keep_period: how long should i wait before i delete the sent items
    take data from db and send it to mongodb, if successfull, mark data as successfull and delete after a while
    '''

    _prepare_django()
    import datalog_app.models

    conf = _get_conf()
    if app_list is None:
        app_list = conf['apps'].keys()

    app_list.append("website")

    conf_label = conf['label']
    connected = False
    sleep(10)
    i = 0
    while True:
        print '-'*30
        print "\n>>>> datasend_app loop, i=%s" %i
        #waiting to have a connection
        t1 = time()
        j = 0
        while not connected:
            try:
                client = pymongo.MongoClient(mongo_address)
                db = client.get_default_database()
            except:
                pass
                #print '!! connecting to mongodb failed %s' %mongo_address
                #print traceback.format_exc()

            try:
                connected = client.alive()
            except:
                connected = False

            if not connected:
                #keep trying
                retryin = min(20 * (j + 1), 60*60)
                print "    !!couldnt connect at j=%s, retrying in %s" % (j, retryin)
                sleep(retryin)
            j += 1
        t2 = time()
        print '    connected to mongo, took %s sec, and %s trials to connect' % (round(t2 - t1, 3), j)

        #when connection is good
        if connected:
            # send the data of the apps
            for app_name in app_list:
                try:
                    print "_send_app_data for %s" % app_name
                    _send_app_data(app_name=app_name, keep_period=keep_period, db=db, conf_label=conf_label)
                except:
                    print '!! _send_app_data for %s failed' % app_name
                    print traceback.format_exc()


        i += 1
        #waiting for next sending time
        print "    next iteration is after %s sec" %send_period
        print '<<<< s'
        sleep(send_period)

    return None
