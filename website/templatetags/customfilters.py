from django import template
from random import randint
import re
from django.core.urlresolvers import reverse
from website.processing import get_conf
import subprocess

register = template.Library()

def gitcmd(cmd):
    r = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.readline().strip()
        #"/bin/sh: 1: cd: can't cd to /home/pi/rpislave_conf\n"
        #'fatal: Not a git repository (or any of the parent directories): .git\n'
    if ("cd to " in r) or ("Not a git" in r):
        return '-'
    else:
        return r

try:
    gitversion = gitcmd("cd /home/pi/rpislave&&git rev-parse HEAD")
    gitbranch = gitcmd("cd /home/pi/rpislave&&git rev-parse --abbrev-ref HEAD")
except:
    gitversion = u'?'
    gitbranch = u'?'

try:
    confgitversion = gitcmd("cd /home/pi/rpislave_conf&&git rev-parse HEAD", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    confgitbranch = gitcmd("cd /home/pi/rpislave_conf&&git rev-parse --abbrev-ref HEAD", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
except:
    confgitversion = u'?'
    confgitbranch = u'?'

try:
    conf = get_conf()
except:
    conf = None

@register.simple_tag()
def git_info():
    return "rpis-%s-%s, conf-%s-%s" %(gitbranch, gitversion[:2], confgitbranch, confgitversion[:2])

@register.filter()
def rev(value):
    return reverse(value)

@register.simple_tag()
def conflabel():
    try:
        return get_conf()['label']
    except:
        return '-'

from django.template.base import add_to_builtins
add_to_builtins('website.templatetags.customfilters')