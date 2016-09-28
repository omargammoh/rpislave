import datetime
import time
from website.models import Log
import traceback
from bson import json_util
import website.proc.status
import website.processing

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

def set_system_time():
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
            if hwc > sysc:
                res = website.processing.execute(cmd = "sudo hwclock --hctosys")
                diff = hwc - sysc
                print ">> timecheck: system time set to the rtc time, diff = %s, was %s, now %s" %(diff, sysc, datetime.datetime.utcnow())

                logline = Log(data=json_util.dumps({"msg":"timecheck setsystemtime",
                                                    "dt":datetime.datetime.utcnow(),
                                                    "hwc": hwc,
                                                    "sysc": sysc
                                                    }), meta="")
                logline.save()

            else:
                logline = Log(data=json_util.dumps({"msg":"timecheck warning: rtc time is older than system time",
                                                    "dt":datetime.datetime.utcnow(),
                                                    "hwc": hwc,
                                                    "sysc": sysc
                                                    }), meta="")
                logline.save()
                print ">> timecheck: rtc time is older than system time, will not set system time"
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
                time_error = website.proc.status.get_time_error()
            except:
                time_error = None
                print ">> timecheck: dont know if system time is correct or not"
                return False

            if abs(time_error) < 10.:
                res = website.processing.execute(cmd="sudo hwclock --systohc")
                print ">> timecheck: system time is correct, rtc has been set to it"
                logline = Log(data=json_util.dumps({"msg":"timecheck setrtctime",
                                    "dt":datetime.datetime.utcnow(),
                                    "hwc": hwc,
                                    "time_error": time_error
                                    }), meta="")
                logline.save()

                return True
            else:
                return False
                print ">> timecheck: system time is not correct, rtc has been not been set"
    except:
        print ">> timecheck: !!! error in setting hwclock %s" %traceback.format_exc()
        return True


#main
def main(timecheck_period=30):
    loop_counter = 0
    prev_dt_loop = None
    rtc_is_set = False

    while True:
        #check if system time has changed
        try:
            dt_loop = datetime.datetime.utcnow()
            if prev_dt_loop is None:
                loop_time_change = None
            else:
                loop_time_change = (dt_loop - prev_dt_loop).total_seconds() - timecheck_period
                if abs(loop_time_change) < 30.: #taking into account the timout of the get_time_error function which runs later in this loop
                    print ">> timecheck: all is fine"
                else:
                    print ">> timecheck: !!!time seems to have changed by %s seconds" %loop_time_change
                    dic = {}
                    dic["msg"] = "timecheck timechange"
                    dic["dt"] = datetime.datetime.utcnow()
                    dic["dt_loop"] = dt_loop
                    dic["prev_dt_loop"] = prev_dt_loop
                    dic["time_change"] = loop_time_change
                    dic["loop_counter"] = loop_counter

                    logline = Log(data=json_util.dumps(dic), meta="")
                    logline.save()
                    print ">> timecheck: wrote log %s" % dic

        except:
            print ">> timecheck: !!!something wrong with system time change check %s " % traceback.format_exc()


        #setting system time
        try:
            if loop_counter == 0:
                set_system_time()
        except:
            print ">> timecheck: !!!something wrong with setting system time"


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
        loop_counter += 1

