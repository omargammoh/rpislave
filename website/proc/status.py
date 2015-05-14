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
        import dateutil.parser
        import pytz
        resp = urllib2.urlopen('http://www.timeapi.org/utc/now', timeout=5).read().strip()
        dt_internet = dateutil.parser.parse(resp).astimezone(pytz.utc)
        seconds = (datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - dt_internet).total_seconds()
        d['time_error'] = seconds
    except:
        d['time_error'] = "-"
        pass

    try:
        resp = urllib2.urlopen('http://api.ipify.org?format=json').read()
        d['ip_wan'] = json.loads(resp)['ip']
    except:
        d['ip_wan'] = "-"
        pass

    try:
        resp = execute("cat /proc/cpuinfo")
        d['serial'] = [x for x in resp.split("\n") if "Serial" in x][0].split()[-1]
    except:
        d['serial'] = "-"
        pass

    try:
        resp = execute("cat /proc/cpuinfo")
        d['revision'] = [x for x in resp.split("\n") if "Revision" in x][0].split()[-1]
    except:
        d['revision'] = "-"
        pass

    try:
        resp = execute("cd /home/pi/rpislave&&git rev-parse HEAD")
        d['git_rpislave'] = resp.strip()
    except:
        d['git_rpislave'] = "-"
        pass

    try:
        resp = execute("cd /home/pi/rpislave_conf&&git rev-parse HEAD")
        d['git_rpislave_conf'] = resp.strip()
    except:
        d['git_rpislave_conf'] = "-"
        pass

    try:
        resp = execute("ip route get \"$(ip route show to 0/0 | grep -oP '(?<=via )\S+')\" | grep -oP '(?<=src )\S+'")
        d['ip_lan'] = resp.strip()
    except:
        d['ip_lan'] = "-"
        pass

    try:
        resp = execute("ip route")
        d['ip_vlan'] = [line for line in resp.split("\n") if "nrtap" in line][0].strip().split(' ')[-1].strip()
    except:
        d['ip_vlan'] = "-"
        pass

    try:
        d['dt'] = datetime.datetime.utcnow().__str__()
    except:
        d['dt'] = "-"

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
                            prev_status.get("ip_vlan", "") == new_status.get("ip_vlan", "") and \
                            prev_status.get("ip_lan", "") == new_status.get("ip_lan", "") and \
                            prev_status.get("ip_wan", "") == new_status.get("ip_wan", "")and \
                            prev_status.get("serial", "") == new_status.get("serial", "") and \
                            prev_status.get("git_rpislave", "") == new_status.get("git_rpislave", "") and \
                            prev_status.get("git_rpislave_conf", "") == new_status.get("git_rpislave_conf", ""):

                print ">> status: all params remain the same, ip_wan = %s" % prev_status.get("ip_wan","-")
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



