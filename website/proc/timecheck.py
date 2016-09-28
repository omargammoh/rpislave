import datetime
import time
from website.models import Log
import traceback
from bson import json_util

#main
def main(timecheck_period=30):
    loop_counter = 0
    prev_dt_loop = None

    while True:
        #check if system time has changed
        try:
            dt_loop = datetime.datetime.utcnow()
            if prev_dt_loop is None:
                loop_time_change = None
            else:
                loop_time_change = (dt_loop - prev_dt_loop).total_seconds() - timecheck_period
                if abs(loop_time_change) < 20.:
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


        prev_dt_loop = dt_loop
        print ">> timecheck: ending loop"
        time.sleep(timecheck_period)
        loop_counter += 1

