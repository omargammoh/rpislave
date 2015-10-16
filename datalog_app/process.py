from time import sleep,time
from datetime import datetime, timedelta
import numpy as np
import itertools
import sys
from website.processing import Timeout


import os, django
from bson import json_util
import traceback
import re

try:
    from pymodbus.client.sync import ModbusSerialClient as MSC
    from pymodbus.transaction import ModbusRtuFramer
except:
    print ">>> datalog_app: !!could not load pymodbus module"

try:
    import spidev
except:
    print ">>> datalog_app: !!could not load spidev module"

def __read_spi(spi, channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data

def _read_spi(spi, channel):
    t0 = time()
    lis_v = []
    while True:
        v = __read_spi(spi, channel)
        lis_v.append(v)
        if time() - t0 > 0.1:
            break
    data = np.average(lis_v)
    return data

def _read_ds18b20(id):
    with Timeout(seconds=1.1):
        base_dir = '/sys/bus/w1/devices'
        device_folder = base_dir + '/' + id
        reading_file = device_folder + '/' + 'w1_slave'
        f = open(reading_file, 'r')
        text = f.read()#text = 'd5 01 55 00 7f ff 0c 10 11 : crc=11 YES\nd5 01 55 00 7f ff 0c 10 11 t=29312\n'
        if not ("YES" in text):
            raise BaseException('YES is not in text')
        f.close()
        raw = re.compile(r'(.+)t=(?P<raw>[-+]?\d+)(.+)', flags=re.DOTALL).match(text).groupdict()['raw']
        return float(raw)/1000. #this number is in celsuis, could be positive or negative

def _pretty_time_delta(seconds):
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%dd%dh%dm%ds' % (days, hours, minutes, seconds)
    elif hours > 0:
        return '%dh%dm%ds' % (hours, minutes, seconds)
    elif minutes > 0:
        return '%dm%ds' % (minutes, seconds)
    else:
        return '%ds' % (seconds,)

def _prepare_django():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'website.settings'
    django.setup()

def _decide_start(data_period, dt):
    safety = timedelta(seconds = 5)
    noms = datetime(*list((dt + safety).timetuple())[:6])#add safety margin, remove milliseconds
    today = datetime(*list(dt.timetuple())[:3])

    totalsec = (noms - today).total_seconds()

    def ceil(x,base):
        return np.ceil(x/base) * base

    if (data_period<60) and (60%data_period == 0):
        print ">>> datalog_app: _decide_start: periodic seconds"
    elif (data_period<3600) and (3600%data_period == 0):
        print ">>> datalog_app: _decide_start: periodic minutes"
    elif (data_period<=86400) and (86400%data_period == 0):
        print ">>> datalog_app: _decide_start: periodic hours"
    else:
        raise BaseException('this stamp period cannot be periodic over minutes, hours or days %s' %data_period)

    shift = ceil(totalsec, data_period)
    starton = today + timedelta(seconds=shift)
    print ">>> datalog_app: _decide_start: %s %s %s, totalsec = %s, shift = %s" %(dt, data_period, starton, totalsec, shift)
    return starton

def _get_mb_client(rs485):
    rs485["framer"]=ModbusRtuFramer
    client = MSC(**rs485) ##  port = "COM3",  client = MSC(port=port ,method='rtu', baudrate=9600, stopbits=1 ,bytesize=8, parity='N' ,retries=1000, rtscts=True,framer=ModbusRtuFramer, timeout = 0.05)
    return client

def _get_point(mb_client, spi_client, sensors_conf):
    dic = {}

    #for each sensor
    for label, conf in sensors_conf.iteritems():
        try:
            if conf['active']:
                if conf['type'] == "rs485":
                    #read
                    reg = mb_client.read_input_registers(conf['register'],unit=conf['address'])
                    #process number
                    value = float(reg.registers[0])# * conf['m'] + conf['c']
                    dic[label] = value
                elif conf['type'] == "mcp3008":
                    raw = _read_spi(spi=spi_client, channel=conf['channel']) #this number is between 0 and 1023#voltageatpin = float(raw) /1023.0 * conf['Vref']#value = voltageatpin * conf['m'] + conf['c']
                    dic[label] = float(raw)
                elif conf['type'].lower() == "ds18b20":
                    raw = _read_ds18b20(id = conf['id'])
                    dic[label] = float(raw)
                else:
                    raise BaseException("unknown sensor type %s" %conf['type'])

            else:
                pass
        except:
            print '>>> datalog_app: !!_get_point: sensor %s failed' %label
            pass

    #return a dic which looks like {'Tamb':21.0, 'Tmod'=30.0, 'G':946.5}
    return dic

def _get_stamp(sample_period, data_period, mb_client, spi_client, sensors_conf):
    count = int(float(data_period)/sample_period)
    starton = datetime.utcnow()
    i = 0

    res = {}
    while (i < count) :
        midstamp = starton + timedelta(seconds = (i + 0.5) * sample_period) #middle ts

        wait = (midstamp - datetime.utcnow()).total_seconds()
        if wait >= 0:
            #print "wait %s seconds" %wait
            sleep(wait)
        else:
            print ">>> datalog_app: !!_get_stamp: point missed by %s, skipping to next" %wait
            #res[midstamp] = None
            i += 1
            continue

        vals = _get_point(mb_client, spi_client, sensors_conf)

        i += 1
        res[midstamp] = vals

    return res #{datetime(): {'Tamb':21.0, 'Tmod':30.0, 'G':946.5}
            # , datetime():{'Tamb':21.0, 'Tmod':30.0, 'G':946.5}, ...}

def _process_data(data, sensors_conf):
    '''
    process the data
    '''

    merged = sorted(list(itertools.chain(*[d.items() for d in data.values()])), key=lambda x:x[0])#it has to be sorted in order for groupby to work, its strange
    res = {}

    #if there is no data for a sensor, it wont be here
    for key, group in itertools.groupby(merged, lambda x: x[0]):
        lis = [thing[1] for thing in list(group)]#lis has always one value at least
        for func in sensors_conf[key]['pp']:
            if func=='avg':
                agg = np.average(lis)
            elif func=='min':
                agg = np.min(lis)
            elif func=='max':
                agg = np.max(lis)
            elif func=='std':
                agg = np.std(lis)
            else:
                print ">>> datalog_app: !!the function %s if unknown, choose between min,max,avg and std" %func
                pass
            res['%s-%s' %(key,func)] = round(agg,2)

    return res #{'Tamb-avg' : 5., 'Tamb-min' : 1., 'G-min' : 60.}

def main(sample_period, data_period, sensors, rs485=None):
    _prepare_django()
    import datalog_app.models


    #check if a modbus client is needed and create it
    rs485_present = any([(sensor['active'] and sensor['type'].lower() == "rs485") for (_,sensor) in sensors.iteritems()])
    if rs485_present:
        try:
            mb_client = _get_mb_client(rs485)
        except:
            print traceback.format_exc()
            mb_client = None
    else:
        mb_client = None

    #check if a spi client is needed and create it
    mcp3008_present = any([(sensor['active'] and sensor['type'].lower() == "mcp3008") for (_,sensor) in sensors.iteritems()])
    if mcp3008_present:
        try:
            spi_client = spidev.SpiDev()
        except:
            print traceback.format_exc()
            spi_client = None
    else:
        spi_client = None

    #check if 1-wire sensor is installed, and import required libraries if it is needed
    onewire_present = any([(sensor['active'] and (sensor['type'].lower() == ["ds18b20", "you can add here more one wire sensor types"])) for (_,sensor) in sensors.iteritems()])
    if onewire_present:
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

    #decide on start
    now = datetime.utcnow()
    starton = _decide_start(data_period, now)

    i = 0
    print ">>> datalog_app: starton %s" %starton

    #loop forever, each loop is a timestamp
    while (True) :
        print '>>> datalog_app: loop, i= %s, t= %s ' %(i, _pretty_time_delta(i * data_period))
        j = 0

        #initialize with not ok
        mb_client_ok = False
        spi_ok = False

        #if at least one [is needed and is [not ok]]
        while (rs485_present and not(mb_client_ok)) or (mcp3008_present and not(spi_ok)):

            t1 = time()

            #connect if mb_client if present and not ok (it will always be not ok in the first loop)
            if rs485_present and not(mb_client_ok):
                try:
                    mb_client.close()#this is important to restablish the connection in another loop
                    mb_client_ok = mb_client.connect()
                except:
                    mb_client_ok = False
            else:
                mb_client_ok = True

            #connect if spi_client if present and not ok (it will always be not ok in the first loop)
            if mcp3008_present and not(spi_ok):
                try:
                    spi_client.close()#this is important, otherwise too many files exception is raised after a whime
                    spi_client.open(0, 0)
                    spi_ok = True
                except:
                    print ">>> datalog: first attempt to spi_client.open(0, 0) failed"
                    try:
                        spi_client = spidev.SpiDev()
                        spi_client.open(0, 0)
                        spi_ok = True
                        print ">>> datalog: spi connected after recreating client"
                    except:
                        print ">>> datalog: !!could not connect to spi even after recreating client"
                        print traceback.format_exc()
                        spi_client = None
                        spi_ok = False
            else:
                spi_ok = True

            t2 = time()

            #if at least one [is needed and is ok]
            if (rs485_present and (mb_client_ok)) or (mcp3008_present and (spi_ok)):
                print '>>>'
                #break this while loop and go get the data, we dont want one broken client to stop the other working client from doing its job
                break

            else:
                #sleep before trying again
                retryin = 10
                print ">>> datalog_app rs485_present %s mb_client_ok %s mcp3008_present %s spi_ok %s" %(rs485_present, mb_client_ok, mcp3008_present, spi_ok)
                print ">>> datalog_app:    !!couldnt connect spi_client or mb_client at j=%s, retrying in %s seconds" % (j,retryin)
                sleep(retryin)
            j += 1

        try:
            print ">>> datalog_app:    mb_client_ok %s, spi_ok %s, at j=%s, took %s sec" %(mb_client_ok,spi_ok,j,round(t2-t1,4))
        except:
            print ">>> datalog_app:    mb or spi not needed"

        #calculate the time for stamp and waiting period, and skip if this stamp is already passed
        stamp = starton + timedelta(seconds = i * data_period)#beginning ts
        wait = (stamp - datetime.utcnow()).total_seconds()
        if wait >= 0:
            print '>>> datalog_app:    wait %s sec before getting samples' %wait
            sleep(wait)
        else:
            skipi = int(abs(wait)/data_period) + 1
            i += skipi
            print '>>> datalog_app:    !! stamp missed by %s seconds, stamp = %s' %(wait, stamp)
            print '>>> datalog_app:    skipping i by %s' %(skipi)
            continue

        #get the data of the stamp
        try:
            #raise exception if there is no data at all, if there is just one sensor not working, dont fail
            print '>>> datalog_app:    getting samples now...'
            dic_samples = _get_stamp(sample_period, data_period, mb_client, spi_client, sensors)
            processed = _process_data(dic_samples, sensors)
            print '>>> datalog_app:    [%s] now = %s' %(stamp, datetime.utcnow())
            print '>>> datalog_app:    %s' %(processed)

        except KeyboardInterrupt:
            print "Good bye from the datalog process"
            sys.exit()
        except:
            dic_samples = None
            processed = None
            print traceback.format_exc()

        #add one to 1
        i += 1

        #if there is data, save it in the local db
        if processed:
            try:
                processed['timestamp']=stamp
                datalog_app.models.Reading(data=json_util.dumps(processed)
                        ,meta=json_util.dumps({'sent':'false', 'quality':'?'})).save()
                print ">>> datalog_app:    data saved in db"

            except:
                print '>>> datalog_app:    !!could not send data to local DB'
                print traceback.format_exc()
        else:
            print ">>> datalog_app:    no data saved in db"

        print '>>> datalog_app: finished loop'
    return None












