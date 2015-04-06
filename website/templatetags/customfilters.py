from django import template
from random import randint
import re
from django.core.urlresolvers import reverse
from website.processing import _get_conf

register = template.Library()

@register.filter
def div( value, arg ):
    '''
    Divides the value; argument is the divisor.
    Returns empty string on any error.
    '''
    try:
        value = int( value )
        arg = int( arg )
        if arg: return value / arg
    except: pass
    return ''

@register.filter
def fieldspacer(value):
    """
    value could be something like
        "5 4", "5 5", "0 10", "5 5 2", "5 5   2"
    returns a list of space length, label length, field length, e.g [2, 2, 5], which sums up to 12
    """
    #make sure its a list of int
    try:
        lis = [int(x) for x in value.split()]
    except:
        return []


    #make sure length is 3
    if len(lis) == 2:
        lis.append(12 - sum(lis))
    elif len(lis) == 3:
        pass
    else:
        return []

    #make sure sum is 12, and there are no negative numbers
    if sum(map(abs,lis)) == 12:
        pass
    else:
        return []

    return lis

def _sanitizeid(value):

    #keep this info
    x = value.replace('+','_plus_').replace('-','_min_')
    #clear out all illegal characters
    x = ''.join([v for v in x if re.findall(r"[-A-Za-z0-9_:.]", v) ])
    #to lower
    x = x.lower()
    #checking the first digit and length
    if len(x) == 0:
        x = "x"
    if x[0].isdigit():
        x = "x" + x

    return x

@register.filter
def sanitizeid(value):
    return _sanitizeid(value)

@register.filter
def rng(value):
    lis = [int(v) for v in value.split()]
    return range(*lis)

@register.filter
def prependhttp(value):
    return 'http://' + value

try:
    import subprocess

    head = subprocess.Popen("cd /home/pi&&git rev-parse HEAD",
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    gitversion = head.stdout.readline().strip()
except:
    gitversion = u'?'

print "git version: ", gitversion

try:
    import subprocess

    head = subprocess.Popen("pip freeze",
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    pipfreeze = "<br>".join(sorted(head.stdout.readlines()))
except:
    pipfreeze = u'?'

@register.simple_tag()
def git_short_version():
    return gitversion[:3]

@register.simple_tag()
def pip_freeze():
    return pipfreeze


@register.simple_tag()
def randomanimtype():
    value="fadeInRight fadeInLeft fadeInUp fadeInDown"
    lis = value.split()
    res = lis[randint(0,len(lis)-1)]
    return res

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