import subprocess
import os
import shutil
import time
from website.models import Log
import json
import datetime

def execute(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()

def get_usage_ratio():
    s=execute('df -h')
    line = [sl for sl in map(lambda x:x.split(), s.split('\n')) if len(sl) > 5 and sl[0]=='rootfs'][0]
    str_perc = line[-2].strip('%')
    flt_perc = float(str_perc)/100.
    return flt_perc

def delete_oldest_day():
    dir = "/home/pi/data/motion_app/movie"
    todel = sorted(os.listdir(dir))[0]
    path_to_del = os.path.join(dir, todel)
    shutil.rmtree(path_to_del)
    print "deleted %s" %path_to_del
    return path_to_del

def main():
    while True:
        try:
            print ">>> clear: starting loop"
            r = get_usage_ratio()
            if r > 0.95:
                path = delete_oldest_day()
                r2 = get_usage_ratio()
                s = json.dumps({'dt': str(datetime.datetime.utcnow())
                            , 'proc': "clear"
                            , "msg": "deleted %s, usage before = %s, usage after = %s" %(path, r, r2)})

                newconf = Log(data=s, meta="")
                newconf.save()
            else:
                print ">>> clear: usage ratio is still small (%s)" %r
        except:
            print ">>> clear: error"
            pass
        time.sleep(60)
