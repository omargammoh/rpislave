import urllib2
import subprocess
import datetime
import json
import time
from website.models import Log
from website.processing import _get_conf
import traceback

def execute(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()

def get_status():
    d = {}
    try:
        resp = urllib2.urlopen('http://api.ipify.org?format=json').read()
        d['ip'] = json.loads(resp)['ip']
    except:
        pass
    try:
        resp = execute("cat /proc/cpuinfo")
        d['serial'] = [x for x in execute("cat /proc/cpuinfo").split("\n") if "Serial" in x][0].split()[-1]
    except:
        pass
    d['dt'] = datetime.datetime.utcnow().__str__()
    return d

def main():
    conf = _get_conf()
    while True:
        print ">>> status: starting loop"
        try:
            fp = '/home/pi/data/status'

            #try get previous ip
            try:
                f = file(fp, "r")
                s = f.read()
                f.close()
                prev_status = json.loads(s)
                oldip = prev_status["ip"]
            except:
                oldip = None
                print ">>> status: previous status not loadable"

            #get new status
            new_status = get_status()

            #if they are the same the do nothing
            if oldip == new_status["ip"]:
                print ">>> status: ip remains the same as before %s" % oldip
                pass

            #if different or none then
            else:
                #create status file
                f = file(fp, "w")
                f.write(json.dumps(new_status))
                f.close()
                new_status["msg"] = "updated status file"

                #if noip info is there
                if "status" in conf and set(["noip_username", "noip_password", "noip_hostname"]).issubset(set(conf["status"].keys())):
                    #update noip.com
                    conf["status"]["ip"] = new_status["ip"]
                    new_status["req"] = 'http://{username}:{password}@dynupdate.no-ip.com/nic/update?hostname={hostname}&myip={ip}'.format(**{conf["status"]})
                    new_status["resp"] = urllib2.urlopen(new_status["req"]).read()
                    new_status["msg"] += ", updated noip"
                    print ">>> status: updated noip, response = %s" % new_status["resp"]
                #else just print something
                else:
                    print ">>> status: no data to update noip"

                #write log
                logline = Log(data=json.dumps(new_status), meta="")
                logline.save()
                print ">>> status: wrote %s" % new_status

        except:
            print traceback.format_exc()
            print ">>> status: error"
            pass

        print ">>> status: ending loop"
        time.sleep(30)
