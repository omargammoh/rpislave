from mng.processing import MP, _get_conf
import gpio_app.process
import json

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

def home(request, template_name='gpio_app/home.html'):
    return render_to_response(template_name, {}, context_instance=RequestContext(request))


import numpy as np
import os, django
from datetime import datetime, timedelta
from time import sleep, time
import traceback
from bson import json_util


def _Vs(Vth, t, RC, Rratio):
    ret = Vth / (1 + (Rratio - 1.) * np.exp( -1. * t / RC))
    return ret

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except:
    print "!!!no RPI.GPIO module"


if False:
    # Discharge capacitor
    GPIO.setup(gpio_pin, GPIO.OUT)
    GPIO.output(gpio_pin, GPIO.LOW)
    sleep(2.)
    # Count loops until voltage across
    # capacitor reads high on GPIO
    i = 0
    GPIO.setup(gpio_pin, GPIO.IN)
    t0 = time()
    (GPIO.input(gpio_pin) == GPIO.LOW)

