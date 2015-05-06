import urllib2
import subprocess
import datetime
import json
import time
from website.models import Log
import traceback

def execute(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()

def get_status():
    d = {}
    try:
        resp = urllib2.urlopen('http://api.ipify.org?format=json').read()
        d['ip'] = json.loads(resp)['ip']
    except:
        d['ip'] = "-"
        pass

    try:
        resp = execute("cat /proc/cpuinfo")
        d['serial'] = [x for x in execute("cat /proc/cpuinfo").split("\n") if "Serial" in x][0].split()[-1]
    except:
        d['serial'] = "-"
        pass

    try:
        resp = execute("cat /proc/cpuinfo")
        d['revision'] = [x for x in execute("cat /proc/cpuinfo").split("\n") if "Revision" in x][0].split()[-1]
    except:
        d['revision'] = "-"
        pass

    try:
        ver = execute("cd /home/pi/rpislave&&git rev-parse HEAD")
        d['git_rpislave'] = ver.strip()
    except:
        d['git_rpislave'] = "-"
        pass

    try:
        ver = execute("cd /home/pi/rpislave_conf&&git rev-parse HEAD")
        d['git_rpislave_conf'] = ver.strip()
    except:
        d['git_rpislave_conf'] = "-"
        pass

    try:
        ipint = execute("ip route get \"$(ip route show to 0/0 | grep -oP '(?<=via )\S+')\" | grep -oP '(?<=src )\S+'")
        d['ip_lan'] = ipint.strip()
    except:
        d['ip_lan'] = "-"
        pass

    d['dt'] = datetime.datetime.utcnow().__str__()

    return d

def check_internet():
    try:
        t1 = time.time()
        _ = urllib2.urlopen('http://www.google.com', timeout=10)
        time_needed = (time.time() - t1)
        internet_ison = True
        print ">> status: connected to internet needed %s sec to ping google" % time_needed
    #if not connected
    except:
        internet_ison = False
    return internet_ison

def restart_networking():
    try:
        print ">> status: not connected to internet, will attempt to restart network"
        print '>> status: sudo /etc/init.d/networking stop'
        execute('sudo /etc/init.d/networking stop')
        print '>> status: sudo /etc/init.d/networking start'
        execute('sudo /etc/init.d/networking start')
        time.sleep(3)
    except:
        pass

def main(status_period=30):
    while True:
        print ">> status: starting loop"

        #checking internet connectivity and trying to reconnect if not connected
        if True:
            internet_ison = check_internet()

            if internet_ison:
                print ">> status: internet already on"

            #if not on
            else:
                #try to restart the networking
                restart_networking()

                #now see if the internet is connected after that we have corrected it is restarted
                internet_ison = check_internet()

                if internet_ison:
                    print ">> status: connected to internet after network restart"
                else:
                    print ">> status: could not connected to internet even after network restart"

        try:
            fp = '/home/pi/data/status'

            #try get previous ip
            try:
                f = file(fp, "r")
                s = f.read()
                f.close()
                prev_status = json.loads(s)
            except:
                prev_status = None
                print ">> status: previous status not loadable"

            #get new status
            new_status = get_status()

            #if prev_status  is loadable and is equal to new_status
            if (prev_status is not None) and \
                            prev_status.get("ip_lan", "") == new_status.get("ip_lan", "") and \
                            prev_status.get("ip", "") == new_status.get("ip", "")and \
                            prev_status.get("serial", "") == new_status.get("serial", "") and \
                            prev_status.get("git_rpislave", "") == new_status.get("git_rpislave", "") and \
                            prev_status.get("git_rpislave_conf", "") == new_status.get("git_rpislave_conf", ""):

                print ">> status: all params remain the same, ip = %s" % prev_status.get("ip_lan","-")
                pass

            #if None or different
            else:
                #create status file
                f = file(fp, "w")
                f.write(json.dumps(new_status))
                f.close()
                new_status["msg"] = "status update"

                #write log
                logline = Log(data=json.dumps(new_status), meta="")
                logline.save()
                print ">> status: wrote %s" % new_status

        except:
            # TODO: if internet is off, exception is raised, but this should not be the case, we should handle this case gracefully
            print ">> status: error: %s" %traceback.format_exc()

        print ">> status: ending loop"
        time.sleep(status_period)



