from django import template
from random import randint
import re
from django.core.urlresolvers import reverse
from website.processing import _get_conf

register = template.Library()

try:
    import subprocess

    head = subprocess.Popen("cd /home/pi/rpislave&&git rev-parse HEAD",
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    gitversion = head.stdout.readline().strip()
except:
    gitversion = u'?'
print "git version: ", gitversion


try:
    import subprocess

    head = subprocess.Popen("cd /home/pi/rpislave_conf&&git rev-parse HEAD",
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    confgitversion = head.stdout.readline().strip()
except:
    confgitversion = u'?'
print "conf git version: ", gitversion

@register.simple_tag()
def git_short_version():
    return "%s-%s" %(gitversion[:2], confgitversion[:2])

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