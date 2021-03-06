import datetime
import time
from website.models import Log
import traceback
from bson import json_util
import website.proc.status
import website.processing
from website.processing import Timeout
import urllib2

#check fake clock: cat /etc/fake-hwclock.data

def set_fakeclock_to_systemtime():
    try:
        website.processing.execute(cmd="""sudo sh -c 'date -u "+%Y-%m-%d %H:%M:%S" > /etc/fake-hwclock.data'""")
    except:
        print "timecheck set_fakeclock_to_systemtime: !!!error "

def get_hwclock():
    """
    gets the time from the real times clock
    """
    try:
        s = website.processing.execute(cmd="sudo hwclock -r") #s = "Wed 20 Jul 2016 18:26:58 UTC  -0.900994 seconds"
        s2 = " ".join(s.split(" ")[1:5])
        dt = datetime.datetime.strptime(s2, '%d %b %Y %H:%M:%S')
        return dt
    except:
        return None

def set_system_time(dt):
    try:
        res = website.processing.execute(cmd="date --set %s" %(dt.strftime('%Y-%m-%d')))
        res = website.processing.execute(cmd="date --set %s" %(dt.strftime('%H:%M:%S')))
    except:
        print "timecheck: error setting system time"

def set_system_time_to_hwclock():
    """
    reads rtc time, if its more recent than system time, then it sets system time to the rtc
    to be run once at startup
    """
    try:
        hwc = get_hwclock()
        sysc = datetime.datetime.utcnow()
        if hwc is None:
            print ">> timecheck: no rtc"
        #hwc is installed
        else:
            diff = (sysc - hwc).total_seconds()
            if hwc > sysc:
                sys_dt_old = datetime.datetime.utcnow()
                res = website.processing.execute(cmd = "sudo hwclock --hctosys")
                sys_dt_new = datetime.datetime.utcnow()

                logline = Log(data=json_util.dumps({"msg":"timecheck set-systemtime-to-hwclock",
                                                    "sys_dt_old" : sys_dt_old,
                                                    "sys_dt_new" : sys_dt_new,
                                                    "dt":datetime.datetime.utcnow(),
                                                    "diff": diff
                                                    }), meta="")
                logline.save()
                print ">> timecheck: system time set to the rtc time, diff = %s, was %s, now %s" %(diff, sysc, datetime.datetime.utcnow())
            elif hwc > (sysc - datetime.timedelta(seconds=2)):
                print ">> timecheck: system time set to the rtc time, diff = %s, was %s, now %s" %(diff, sysc, datetime.datetime.utcnow())
            else:
                logline = Log(data=json_util.dumps({"msg":"timecheck-warning rtc-time-is-older-than-system-time",
                                                    "dt":datetime.datetime.utcnow(),
                                                    "hwc_dt": hwc,
                                                    "sys_dt": datetime.datetime.utcnow(),
                                                    "diff": diff
                                                    }), meta="")
                logline.save()
                print ">> timecheck: !!!rtc time is older than system time by %s" %diff
    except:
        print ">> timecheck: !!! error in initialising hwclock %s" %traceback.format_exc()

def set_rtc_time():
    """
    sets the rtc time to the system time, after making sure that time error in system time is small
    to be run on every status loop until it returns True, do again every 1000 loops or so

    return: rtc_is_set
    """
    try:
        hwc = get_hwclock()
        if hwc is None:
            print ">> timecheck: no rtc to set its time"
            return False

        #hwc is installed
        else:
            try:
                time_error = get_time_error()
            except:
                time_error = None
                print ">> timecheck: dont know if system time is correct or not for setting rtc"
                return False

            if abs(time_error) < 15.:
                res = website.processing.execute(cmd="sudo hwclock --systohc")
                print ">> timecheck: system time is correct, rtc has been set to it"
                new_hwc = get_hwclock()
                diff = (new_hwc - hwc).total_seconds()
                logline = Log(data=json_util.dumps({"msg":"timecheck set-hwc-time-to-internet-and-sys-time",
                                    "dt":datetime.datetime.utcnow(),
                                    "old_hwc": hwc,
                                    "new_hwc": new_hwc,
                                    "time_error": time_error
                                    }), meta="")
                logline.save()

                return True
            else:
                print ">> timecheck: system time is not correct, rtc has been not been set"
                return False
    except:
        print ">> timecheck: !!! error in setting hwclock %s" %traceback.format_exc()
        return True

def get_time_error():
    """
    gets time error in seconds
    """
    try:
        with Timeout(seconds=16):
            import dateutil.parser
            import pytz
            import ssl
            t1 = time.time()
            #resp = urllib2.urlopen(r'https://script.google.com/macros/s/AKfycbyd5AcbAnWi2Yn0xhFRbyzS4qMq1VucMVgVvhul5XqS9HkAyJY/exec', timeout=15).read().strip()
            resp = urllib2.urlopen(urllib2.Request('https://script.google.com/macros/s/AKfycbyd5AcbAnWi2Yn0xhFRbyzS4qMq1VucMVgVvhul5XqS9HkAyJY/exec'), context=ssl._create_unverified_context()).read()
            jresp = json_util.loads(resp)
            if not (jresp['timezone'].lower()=="utc"):
                print ">> timecheck: !!!Time error might not be UTC"
                raise BaseException('')
            t2 = time.time()
            time_needed = (t2 - t1)
            correction = time_needed/2.
            dt_internet = dateutil.parser.parse(jresp['fulldate']).astimezone(pytz.utc)
            seconds = (datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - dt_internet).total_seconds() - correction
            return seconds
    except:
        print ">> timecheck: could not get time_error"
        return None

#main
def main(timecheck_period=30):
    loop_counter = 0
    prev_dt_loop = None
    last_recorded_time_error = None
    rtc_is_set = False

    while True:
        dt_loop = datetime.datetime.utcnow()

        #setting initial system time to hwclock if hwclock date is not older, stop the ntp because we will sync clock by ourselves
        try:
            if loop_counter == 0:
                res = website.processing.execute(cmd="sudo service ntp stop")
                set_system_time_to_hwclock()
        except:
            print ">> timecheck: !!!something wrong with setting system time"

        #get time error, to be used later
        try:
            time_error = get_time_error()
        except:
            time_error = None

        #set system time if timeerror is big
        try:
            if (time_error is not None) and abs(time_error) > 15.:
                old_dt = datetime.datetime.utcnow()
                print ">> timecheck: setting system time to internet time"
                set_system_time(datetime.datetime.utcnow() - datetime.timedelta(seconds = time_error))
                new_dt = datetime.datetime.utcnow()
                dic = {}
                dic["msg"] = "timecheck set-system-time-to-internet-time"
                dic["dt"] = datetime.datetime.utcnow()
                dic["sys_dt_old"] = old_dt
                dic["sys_dt_new"] = new_dt
                dic["time_error_old"] = time_error
                dic["loop_counter"] = loop_counter
                logline = Log(data=json_util.dumps(dic), meta="")
                logline.save()
        except:
            print ">> timecheck set-system-time-to-internet-time: !!! something wrong"

        # check time error change and log it
        try:
            try:
                time_error_has_changed = abs(time_error - last_recorded_time_error) > 10.
            except:
                time_error_has_changed = False

            # if this is the first time we estimate a time error                 or time_error_has_changed
            if ((time_error is not None) and (last_recorded_time_error is None)) or time_error_has_changed :
                print ">> timecheck: time error changed from %s to %s" %(last_recorded_time_error, time_error)
                dic = {}
                dic["msg"] = "timecheck time-error-change"
                dic["dt"] = datetime.datetime.utcnow()
                dic["time_error_old"] = last_recorded_time_error
                dic["time_error_new"] = time_error
                dic["loop_counter"] = loop_counter
                logline = Log(data=json_util.dumps(dic), meta="")
                logline.save()
                last_recorded_time_error = time_error

        except:
            print ">> timecheck: !!!something wrong while estimating time error"



        #check if system time has changed
        try:
            if prev_dt_loop is None:
                loop_time_change = None
            else:
                loop_time_change = (dt_loop - prev_dt_loop).total_seconds() - timecheck_period
                if abs(loop_time_change) < 30.: #taking into account the timout of the get_time_error function which runs later in this loop
                    print ">> timecheck: all is fine"
                else:
                    print ">> timecheck: !!!time seems to have changed by %s seconds" %loop_time_change
                    dic = {}
                    dic["msg"] = "timecheck time-change"
                    dic["dt"] = datetime.datetime.utcnow()
                    dic["dt_loop"] = dt_loop
                    dic["dt_loop_old"] = prev_dt_loop
                    dic["time_change"] = loop_time_change
                    dic["loop_counter"] = loop_counter

                    logline = Log(data=json_util.dumps(dic), meta="")
                    logline.save()
                    print ">> timecheck: wrote log %s" % dic

        except:
            print ">> timecheck: !!!something wrong with system time change check %s " % traceback.format_exc()


        #setting rtc time
        try:
            #to force to check the rtc time every while
            if loop_counter % 10000 == 0:
                rtc_is_set = False
            #set rtc if we know the time
            if not rtc_is_set:
                rtc_is_set = set_rtc_time()
        except:
            print ">> status: !!!something wrong with setting rtc time"


        prev_dt_loop = dt_loop
        time.sleep(timecheck_period)
        set_fakeclock_to_systemtime()
        loop_counter += 1

