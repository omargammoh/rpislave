from bson import json_util
import multiprocessing
from website.models import Conf
from time import time, sleep
import inspect
import subprocess
import json

try:
    import signal
except:
    print "signal cannot be imported"


def execute(cmd, daemon=False):
    if daemon:
        _ = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return None
    else:
        return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()

def fix_corrupt_db():
    conf = get_conf()
    write_json_file(conf, "/home/pi/data/conf")
    execute('sudo rm /home/pi/rpislave/db.sqlite3')
    execute('sudo reboot')
    return None

def read_json_file(fp):
    try:
        f = file(fp, "r")
        s = f.read()
        f.close()
        js = json.loads(s)
    except:
        js = None
    return js

def write_json_file(js, fp):
    f = file(fp, "w")
    f.write(json.dumps(js))
    f.close()

class Timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise BaseException(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.setitimer(signal.ITIMER_REAL, self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

def filter_kwargs(func, kwargs_input):
    """
    creates the kwargs of func from kwargs_input
    func: function to inspect
    """
    argnames,_,_,defaults = inspect.getargspec(func)
    if defaults is None: defaults=[]
    required_args = set(argnames[:len(argnames)-len(defaults)])
    optional_args = set(argnames[len(argnames)-len(defaults):])
    kwargs_needed = {k:v for (k,v) in kwargs_input.iteritems() if k in required_args.union(optional_args) }
    return kwargs_needed

def get_pid(command):
    """
    gets the pid of the process using the command column in the ps aux table
    """
    s = subprocess.Popen("ps aux", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
    lines = [line.split(None, 10) for line in s.split("\n") if line.lstrip() != ""]
    matches = [line for line in lines if line[-1] == command]
    if len(matches)==0:
        print "no maches found"
        return None
    elif len(matches)>1:
        print "multiple matches found"
        return None
    else:
        pid = matches[0][1]
    return pid

def get_conf():
    for ob in Conf.objects.all():
        try:
            js = json_util.loads(ob.data)
            if not ("label" in js):
                raise BaseException('no label in conf')
            return js
        except:
            print "!!was not able to parse and get label of a configuration row, skipping"
            pass
    return None

def fix_malformed_db():
    try:
        #get conf
        print 'fix_malformed_db >> getting conf'
        conf_x = get_conf()

        #save it on a text file
        print 'fix_malformed_db >> saving conf as text'
        f = file('/home/pi/rpislave/conf.json', 'w')
        f.write(json_util.dumps(conf_x))
        f.close()

        #remove db
        import os
        print 'fix_malformed_db >> deleting db'
        os.remove('/home/pi/rpislave/db.sqlite3')

        #keep a note as a file
        print 'fix_malformed_db >> saving log as text'
        from datetime import datetime
        now = datetime.utcnow()
        f = file('/home/pi/data/dbdelete-' + now.strftime('%Y%m%d%H%M%S'),'w')
        f.write('we have taken a copy of conf, saved it on disk, deleted the database and restarted. %s' %str(now))
        f.close()

        #restart
        print 'fix_malformed_db >> rebooting'
        os.system('sudo reboot')
    except:
        print "error while trying to fix malformed db"

class MP():
    def __init__(self, name, target, request, cmd=None):
        self.t1 = time()
        self.name = name
        self.target = target
        self.request = request
        self.cmd = cmd if cmd else request.GET.get("cmd", None)
        self.dic = {}

    def start(self):
        app_conf = get_conf()['apps'][self.name]
        p = multiprocessing.Process(name=self.name, target=self.target, kwargs=filter_kwargs(func=self.target, kwargs_input=app_conf))
        p.start()


    def ison(self):
        ac = [m for m in multiprocessing.active_children() if m.name == self.name ]
        if len(ac) == 0:
            return False
        else:
            #return ac[0].is_alive() #this line does not work when switching to uwsgi and gives the error: can only test a child process, this is due to the fact that uwsgi has many workers
            return True

    def stop(self):
        ac = [m for m in multiprocessing.active_children() if self.name == m.name][0]
        if ac:
            if ac.pid:
                kill_command = "sudo kill -INT %s" % ac.pid
                print "stopping process in the good way: %s" % kill_command
                s = subprocess.Popen(kill_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
            else:
                print "stopping process in in the hard way"
                ac.terminate()
            sleep(0.5)
            return True
        else:
            return False

    def process_command(self):
        lis = []
        print "%s" %(self.name)
        ison_at_start = self.ison()

        if self.cmd is None:
            lis.append('no cmd has provided')

        elif self.cmd == 'start':
            if ison_at_start:
                lis.append('process was already running')
            else:
                self.start()
                lis.append('process has been started')
        elif self.cmd == 'stop':
            if self.stop():
                lis.append('terminated process')
            else:
                lis.append('process was not running')

        elif self.cmd == 'status':
            self.dic["%s" %self.name] = get_conf()['apps'][self.name]

        else:
            lis.append("we didnt understand your cmd")

        #respond with some info
        self.dic['log'] = lis
        self.dic['ison'] = self.ison()
        self.dic['took'] = "%s seconds" %(time()-self.t1)
