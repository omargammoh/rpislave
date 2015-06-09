from django import template
from random import randint
import re
from django.core.urlresolvers import reverse
from website.processing import _get_conf
import subprocess

register = template.Library()

try:
    gitversion = subprocess.Popen("cd /home/pi/rpislave&&git rev-parse HEAD",shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.readline().strip()
    gitbranch = subprocess.Popen("cd /home/pi/rpislave&&git rev-parse --abbrev-ref HEAD",shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.readline().strip()
except:
    gitversion = u'?'
    gitbranch = u'?'

try:
    confgitversion = subprocess.Popen("cd /home/pi/rpislave_conf&&git rev-parse HEAD", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.readline().strip()
    confgitbranch = subprocess.Popen("cd /home/pi/rpislave_conf&&git rev-parse --abbrev-ref HEAD", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.readline().strip()
except:
    confgitversion = u'?'
    confgitbranch = u'?'

try:
    conf = _get_conf()
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
        return _get_conf()['label']
    except:
        return '-'

from django.template.base import add_to_builtins
add_to_builtins('website.templatetags.customfilters')