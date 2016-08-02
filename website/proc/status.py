import urllib2
import subprocess
import datetime
import json
import time
from website.models import Log
import traceback
from django.conf import settings
import website.processing
from bson import json_util
import re
from website.processing import Timeout

conf = website.processing.get_conf()

master_url = conf.get('master_url', settings.DEFAULT_MASTER_URL)

REQUIRED_TUNNELS = ['9001', '9005']
if (conf is not None) and 'motion_app' in conf.get('apps', {}):
    REQUIRED_TUNNELS.append('9002')

#tunneling
def get_tunnels():
    """
    get a list of tunnels that are open now
    """
    res = website.processing.execute(cmd="ps aux|grep 'sudo ssh'")
    dic = {}
    regex = re.compile(r'root(\s+)(?P<pid>\d+)(\s+)(.+):(?P<server_port>\d+):localhost:(?P<slave_port>\d+)(.+)@(?P<server_ip>[1-9.]+)')
    #re.compile(r'root(\s+)(?P<pid>\d+)(\s+)(.+):(?P<server_port>\d+):localhost:(?P<slave_port>\d+)(.+)@(?P<server_ip>[1-9.]+)').match("root      9842  0.0  0.3   4592  2508 pts/2    S+   09:46   0:00 sudo ssh -i /home/pi/tunnelonly -R *:59995:localhost:9001 -N ubuntu@52.24.252.161").groupdict()
    for ln in res.split('\n'):
        if ln.strip() == "":
            continue
        d = {}
        m = regex.match(ln)
        if m:
            # d is guaranteed to have port and pid as keys because it has matched
            d.update(m.groupdict())
            d['line'] = ln
            dic[d['slave_port']] = d
    return dic #OrderedDict([('59995', {'pid': '11601', 'port': '59995', 'line': 'tcp        0      0 0.0.0.0:59995           0.0.0.0:*               LISTEN      11601/sshd: ubuntu'})])

def new_tunnel_para(slave_port):
    """
    ask server to provide server_ip, server_port to connect reverse ssh to
    """
    full_url = master_url + conf['perm'] + "&para=new_tunnel&slave_port=%s" %slave_port #http://rpi-master.com/api/slave/?_perm=write&_slave=development+and+testing&_sig=b901abde&para=fwd_to_db&data=%7B%22Tamb-max%22%3A+0.0%2C+%22Tamb-min%22%3A+0.0%2C+%22timestamp%22%3A+%7B%22%24date%22%3A+1439128980000%7D%2C+%22Tamb-avg%22%3A+0.0%7D

    resp = urllib2.urlopen(full_url, timeout=15).read().strip()
    js_resp = json_util.loads(resp)
    return js_resp

def create_tunnel(slave_port, tunnel_para):
    with Timeout(seconds=30):
        website.processing.execute('sudo chmod 700 /home/pi/rpislave/tunnelonly')
        revssh_line = 'sudo ssh -o TCPKeepAlive=no -o ExitOnForwardFailure=yes -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ServerAliveCountMax=2 -i /home/pi/rpislave/tunnelonly -R \*:%s:localhost:%s -N ubuntu@%s' % (tunnel_para['server_port'], slave_port, tunnel_para['server_ip'])
        print ">> status: creating tunnel: %s" %revssh_line
        website.processing.execute(revssh_line, daemon=True)

def check_tunnels():
    internet_ison = check_internet()
    if not internet_ison:
        print ">> status: internet is off, no point checking tunnels"
        return None

    tunnels = get_tunnels()
    for port in REQUIRED_TUNNELS:
        if port in tunnels:
            print '>> status: tunnel %s is fine' %port
        else:
            print '>> status: fixing tunnel %s' %port
            #TODO: now, whenever there is no tunnel, new tunnel_para are asked from server, slave should try with old parameters,
            # and if it still doesnt work after 10 tries when internet is on, it would ask for new tunnel parameters
            tunnel_para = new_tunnel_para(slave_port=port)
            create_tunnel(slave_port=port, tunnel_para=tunnel_para)

#
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

def get_time_error():
    """
    gets time error in seconds
    """
    with Timeout(seconds=16):
        import dateutil.parser
        import pytz
        t1 = time.time()
        resp = urllib2.urlopen('http://www.timeapi.org/utc/now', timeout=15).read().strip()
        t2 = time.time()
        time_needed = (t2 - t1)

        correction = time_needed/2.

        dt_internet = dateutil.parser.parse(resp).astimezone(pytz.utc)
        seconds = (datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - dt_internet).total_seconds() - correction
        return seconds

def get_status():
    def gitcmd(cmd):
        r = website.processing.execute(cmd).strip()
            #"/bin/sh: 1: cd: can't cd to /home/pi/rpislave_conf\n"
            #'fatal: Not a git repository (or any of the parent directories): .git\n'
        if ("cd to " in r) or ("Not a git" in r):
            return '-'
        else:
            return r
    d = {}

    #TIME ERROR
    try:
        d['time_error'] = get_time_error()
    except:
        d['time_error'] = "-"
        pass

    try:
        resp = urllib2.urlopen('http://api.ipify.org?format=json').read()
        d['ip_wan'] = json.loads(resp)['ip']
    except:
        d['ip_wan'] = "-"
        pass

    #CPU
    try:
        with Timeout(seconds=10):
            resp = website.processing.execute("cat /proc/cpuinfo")
            d['serial'] = [x for x in resp.split("\n") if "Serial" in x][0].split()[-1]
    except:
        d['serial'] = "-"
        pass

    try:
        with Timeout(seconds=30):
            resp = website.processing.execute("cat /proc/cpuinfo")
            d['revision'] = [x for x in resp.split("\n") if "Revision" in x][0].split()[-1]
    except:
        d['revision'] = "-"
        pass

    #GIT
    try:
        with Timeout(seconds=30):
            d['git_rpislave'] = gitcmd("cd /home/pi/rpislave&&git rev-parse HEAD")
            d['gitbranch_rpislave'] = gitcmd("cd /home/pi/rpislave&&git rev-parse --abbrev-ref HEAD")
    except:
        d['git_rpislave'] = '-'
        d['gitbranch_rpislave'] = '-'



    #IP
    try:
        with Timeout(seconds=30):
            resp = website.processing.execute("ifconfig")
            d['ip_lan'] = "192.168.{0[p3]}.{0[p4]}".format(re.compile(r'(.+)inet addr:192\.168\.(?P<p3>\d+)\.(?P<p4>\d+)(.+)', flags=re.DOTALL).match(resp).groupdict())
    except:
        d['ip_lan'] = "-"

    try:
        with Timeout(seconds=30):
            resp = website.processing.execute("ifconfig")
            d['ip_vlan'] = "10.0.{0[p3]}.{0[p4]}".format(re.compile(r'(.+)inet addr:10\.0\.(?P<p3>\d+)\.(?P<p4>\d+)(.+)', flags=re.DOTALL).match(resp).groupdict())
    except:
        d['ip_vlan'] = "-"

    return d

def check_internet():
    try:
        t1 = time.time()
        _ = urllib2.urlopen('http://www.google.com', timeout=10)
        time_needed = (time.time() - t1)
        internet_ison = True
        print ">> status: internet accessible, needed %s sec to ping google" % time_needed
    except:
        internet_ison = False
    return internet_ison

def restart_networking():
    try:
        with Timeout(seconds=30):
            print ">> status: not connected to internet, will attempt to restart network"
            print '>> status: sudo /etc/init.d/networking stop'
            website.processing.execute('sudo /etc/init.d/networking stop')
            print '>> status: sudo /etc/init.d/networking start'
            website.processing.execute('sudo /etc/init.d/networking start')
            #execute("sudo sed -i '1s/^/nameserver 8.8.8.8\n/' /etc/resolv.conf")
            time.sleep(3)
    except:
        pass

def round_time_error(s):
    try:
        return round(float(s)/10)*10
    except:
        return None

def mark_loop():
    try:
        f = file('/home/pi/data/laststatusloop','w')
        f.write(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S'))
        f.close()
    except:
        print ">> status: !!! failed to mark loop"

def set_system_time():
    """
    reads rtc time, if its more recent than system time, then it sets system time to the rtc
    to be run once at startup
    """
    try:
        hwc = get_hwclock()
        sysc = datetime.datetime.utcnow()
        if hwc is None:
            print ">> status: no rtc"
        #hwc is installed
        else:
            if hwc > sysc:
                res = website.processing.execute(cmd = "sudo hwclock --hctosys")
                diff = hwc - sysc
                print ">> status: system time set to the rtc time, diff = %s, was %s, now %s" %(diff, sysc, datetime.datetime.utcnow())
            else:
                print ">> status: rtc time is older than system time, will not set system time"
    except:
        print ">> status: !!! error in initialising hwclock %s" %traceback.format_exc()

def set_rtc_time():
    """
    sets the rtc time to the system time, after making sure that time error in system time is small
    to be run on every status loop until it returns True, do again every 1000 loops or so
    """
    try:
        hwc = get_hwclock()
        if hwc is None:
            print ">> status: no rtc to set its time"
            return True
        #hwc is installed
        else:
            time_error = get_time_error()
            if abs(time_error) < 10:
                res = website.processing.execute(cmd="sudo hwclock --systohc")
                print ">> status: system time is correct, rtc has been set to it"
                return True
            else:
                return False
                print ">> status: system time is not correct, rtc has been not been set"
    except:
        print ">> status: !!! error in setting hwclock %s" %traceback.format_exc()
        return True

#main
def main(status_period=30):
    loop_counter = 0
    rtc_is_set = False
    while True:
        print ">> status: starting loop"

        try:
            #set system datetime to rtc if appropriate
            if loop_counter == 0:
                set_system_time()

            #set rtc if we know the time
            if not rtc_is_set:
                rtc_is_set = set_rtc_time()

            #
            if loop_counter % 10000 == 0:
                rtc_is_set = False
        except:
            print ">> status: !!!something wrong with the time functions"

        #checking internet connectivity and trying to reconnect if not connected
        if True:
            internet_ison = check_internet()

            if internet_ison:
                print ">> status: internet already on"

            #if not on
            else:
                #try to restart the networking
                restart_networking()

                # see if the internet is connected after that we have corrected it is restarted
                internet_ison = check_internet()

                if internet_ison:
                    print ">> status: connected to internet after network restart"
                else:
                    print ">> status: could not connected to internet even after network restart"

        try:

            if loop_counter == 0:
                dicx = {'start': datetime.datetime.utcnow()}
                logline = Log(data=json_util.dumps(dicx), meta="")
                logline.save()
                print ">> status: wrote start %s" % dicx


            #file where status is saved
            fp = '/home/pi/data/status'

            #get previous status
            prev_status = website.processing.read_json_file(fp=fp)

            if prev_status is None:
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
                            prev_status.get("gitbranch_rpislave", "") == new_status.get("gitbranch_rpislave", "") and \
                            (new_status.get("time_error", "-") == "-" or round_time_error(prev_status.get("time_error", "")) == round_time_error(new_status.get("time_error", ""))):

                print ">> status: all params remain the same"
                pass

            #status is None or different
            else:
                if prev_status is None:
                    prev_status = {}
                dic_diff = dict(set(new_status.items()) - set(prev_status.items()))

                #if not much change in time-error
                if round_time_error(prev_status.get("time_error", "")) == round_time_error(new_status.get("time_error", "")):
                    if 'time_error' in dic_diff:
                        # discard it
                        dic_diff.pop('time_error')

                #write it on disk
                website.processing.write_json_file(js=new_status, fp=fp)

                #write log to db
                dic_diff["msg"] = "status update"
                dic_diff["dt"] = datetime.datetime.utcnow()
                logline = Log(data=json_util.dumps(dic_diff), meta="")
                logline.save()
                print ">> status: wrote changes %s" % dic_diff

            #checking revssh
            check_tunnels()

            #mark loop
            mark_loop()

        except:
            print ">> status: !! error: %s" %traceback.format_exc()

        print ">> status: ending loop"
        time.sleep(status_period)
        loop_counter += 1

