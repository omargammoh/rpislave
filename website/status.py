import urllib2
import subprocess
import datetime
import json
import time

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
    return json.dumps(d)

def main():
    while True:
        print ">>> status: starting loop"
        try:
            s = get_status()
            f = file('/home/pi/data/status', "w")
            f.write(s)
            f.close()
            print ">>> status: wrote %s" %s
        except:
            print ">>> status: error"
            pass
        print ">>> status: ending loop"
        time.sleep(60)
