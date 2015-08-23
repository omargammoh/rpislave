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

conf = website.processing.get_conf()

REQUIRED_TUNNELS = ['9001', '9005']
if 'motion_app' in conf['apps']:
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
    full_url = settings.BASE_URL + conf['perm'] + "&para=new_tunnel&slave_port=%s" %slave_port #http://rpi-master.com/api/slave/?_perm=write&_slave=development+and+testing&_sig=b901abde&para=fwd_to_db&data=%7B%22Tamb-max%22%3A+0.0%2C+%22Tamb-min%22%3A+0.0%2C+%22timestamp%22%3A+%7B%22%24date%22%3A+1439128980000%7D%2C+%22Tamb-avg%22%3A+0.0%7D

    resp = urllib2.urlopen(full_url, timeout=15).read().strip()
    js_resp = json_util.loads(resp)
    return js_resp

def create_tunnel(slave_port, tunnel_para):
    website.processing.execute('sudo chmod 700 /home/pi/rpislave/tunnelonly')
    revssh_line = 'sudo ssh -o ExitOnForwardFailure=yes -o StrictHostKeyChecking=no -i /home/pi/rpislave/tunnelonly -R \*:%s:localhost:%s -N ubuntu@%s' % (tunnel_para['server_port'], slave_port, tunnel_para['server_ip'])
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

#networking
def check_vlan(status):
    #if vlan is not working, try to fix it
    try:
        if status.get('ip_vlan', "-") == "-":
            print ">> status: no vlan, attempting to reconnect to vlan"
            #print ">> status: ", execute("sudo /etc/init.d/nrservice.sh start").strip()
            #TODO: here the neorouter parameters are hard coded, they should be taken from configuration!!!
            with website.processing.Timeout(seconds=10):
                #in the normal behaviour, timeout is reached, this is just a workaround to stop the process
                website.processing.execute("sudo /usr/bin/nrclientcmd -d rpimaster -u pi -p raspberry")
    except:
        print ">> status: !! error while trying to fix the ip_vlan"

def get_status():
    d = {}

    #TIME ERROR
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

    #CPU
    try:
        resp = website.processing.execute("cat /proc/cpuinfo")
        d['serial'] = [x for x in resp.split("\n") if "Serial" in x][0].split()[-1]
    except:
        d['serial'] = "-"
        pass

    try:
        resp = website.processing.execute("cat /proc/cpuinfo")
        d['revision'] = [x for x in resp.split("\n") if "Revision" in x][0].split()[-1]
    except:
        d['revision'] = "-"
        pass

    #GIT
    try:
        d['git_rpislave'] = website.processing.execute("cd /home/pi/rpislave&&git rev-parse HEAD").strip()
        d['gitbranch_rpislave'] = website.processing.execute("cd /home/pi/rpislave&&git rev-parse --abbrev-ref HEAD").strip()
    except:
        d['git_rpislave'] = '-'
        d['gitbranch_rpislave'] = '-'

    try:
        d['git_rpislave_conf'] = website.processing.execute("cd /home/pi/rpislave_conf&&git rev-parse HEAD").strip()
        d['gitbranch_rpislave_conf'] = website.processing.execute("cd /home/pi/rpislave_conf&&git rev-parse --abbrev-ref HEAD").strip()
    except:
        d['git_rpislave_conf'] = '-'
        d['gitbranch_rpislave_conf'] = '-'


    #IP
    try:
        resp = website.processing.execute("ip route get \"$(ip route show to 0/0 | grep -oP '(?<=via )\S+')\" | grep -oP '(?<=src )\S+'")
        d['ip_lan'] = resp.strip()
    except:
        d['ip_lan'] = "-"
        pass

    try:
        resp = website.processing.execute("ip route")
        d['ip_vlan'] = [line for line in resp.split("\n") if "nrtap" in line][0].strip().split(' ')[-1].strip()
    except:
        d['ip_vlan'] = "-"
        pass

    #DT
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
        print ">> status: internet accessible, needed %s sec to ping google" % time_needed
    except:
        internet_ison = False
    return internet_ison

def restart_networking():
    try:
        print ">> status: not connected to internet, will attempt to restart network"
        print '>> status: sudo /etc/init.d/networking stop'
        website.processing.execute('sudo /etc/init.d/networking stop')
        print '>> status: sudo /etc/init.d/networking start'
        website.processing.execute('sudo /etc/init.d/networking start')
        #execute("sudo sed -i '1s/^/nameserver 8.8.8.8\n/' /etc/resolv.conf")
        time.sleep(3)
    except:
        pass

#main
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
                            prev_status.get("git_rpislave_conf", "") == new_status.get("git_rpislave_conf", "") and \
                            prev_status.get("gitbranch_rpislave_conf", "") == new_status.get("gitbranch_rpislave_conf", ""):

                print ">> status: all params remain the same, ip_wan = %s" % prev_status.get("ip_wan","-")
                pass

            #status is None or different
            else:
                #write it on disk
                website.processing.write_json_file(js=new_status, fp=fp)

                #write log to db
                new_status["msg"] = "status update"
                logline = Log(data=json.dumps(new_status), meta="")
                logline.save()
                print ">> status: wrote %s" % new_status

            #checking vlan
            check_vlan(status=new_status)

            #checking revssh
            check_tunnels()

        except:
            print ">> status: !! error: %s" %traceback.format_exc()

        print ">> status: ending loop"
        time.sleep(status_period)





