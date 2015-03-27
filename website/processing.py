from bson import json_util
import multiprocessing
from website.models import Conf
from django.conf import settings
from time import time, sleep
import inspect

def _get_conf():
    for ob in Conf.objects.all():
        try:
            js = json_util.loads(ob.data)
            if js['label'] == settings.CONF_LABEL:
                return js
        except:
            print "!!was not able to parse and get label of a configuration row, skipping"
            pass
    raise BaseException('could not find the configuration %s' %settings.CONF_LABEL)


class MP():
    def __init__(self, name, target, request, cmd=None):
        self.t1 = time()
        self.name = name
        self.target = target
        self.request = request
        self.cmd = cmd if cmd else request.GET.get("cmd", None)
        self.dic = {}
        self.conf_label = settings.CONF_LABEL

    def start(self):
        conf = _get_conf()['apps'][self.name]

        #not all the parameters in the conf are needed in the target, trim to our needs
        argnames,_,_,defaults = inspect.getargspec(self.target)
        if defaults is None: defaults=[]
        required_args=set(argnames[:len(argnames)-len(defaults)])
        optional_args=set(argnames[len(argnames)-len(defaults):])
        trimmed_conf = {k:v for (k,v) in conf.iteritems() if k in required_args.union(optional_args) }

        p = multiprocessing.Process(name=self.name, target=self.target, kwargs=trimmed_conf)
        p.start()


    def ison(self):
        ac = [m for m in multiprocessing.active_children() if m.name == self.name ]
        if len(ac) == 0:
            return False
        else:
            return ac[0].is_alive()

    def stop(self):
        ac = [m for m in  multiprocessing.active_children() if self.name == m.name]
        if ac:
            ac[0].terminate()
            sleep(0.5)
            return True
        else:
            return False

    def process_command(self):
        lis = []

        print "%s conf = %s" %(self.name, self.conf_label)
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
            self.dic["%s" %self.name] = _get_conf()['apps'][self.name]

        else:
            lis.append("we didnt understand your cmd")

        #respond with some info
        self.dic['log'] = lis
        self.dic['ison'] = self.ison()
        self.dic['took'] = "%s seconds" %(time()-self.t1)
