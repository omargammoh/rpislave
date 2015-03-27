from website.processing import _get_conf
import traceback
import subprocess
from time import sleep

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD)
except:
    print "!!could not import RPi.GPIO"

board_bmc = dict([(7,4),(11,17),(12,18),(13,27),(15,22),(16,23),(18,24),(22,25),(29,6),(31,12),(32,12),(33,13),(35,19),(36,16),(37,26),(38,20),(40,21)])

def main(pins_conf):

    print ""
    for bcmpin in board_bmc.values():
        print subprocess.Popen("echo %s > /sys/class/gpio/export" %bcmpin, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()

    pins_conf = _get_conf()['apps']['gpio_app']['pins_conf']

    for label, conf in pins_conf.iteritems():
        try:
            if conf["iou"] == "input":
                GPIO.setup(conf["pin"], GPIO.IN)
            elif conf["iou"] == "output":
                GPIO.setup(conf["pin"], GPIO.OUT)
                if conf.get("start","low") == "high":
                    GPIO.output(conf["pin"], GPIO.HIGH)
                else:
                    GPIO.output(conf["pin"], GPIO.LOW)
            elif conf["iou"] == "unset":
                #TODO: find a way to unset a pin
                pass
            else:
                raise BaseException('iou is not known %s' %conf["iou"] )
            print "succesfuly done %s" %conf
        except:
            print "!!failed setting up pin %s" %label
            print traceback.format_exc()

    #keep running
    while True:
        sleep(10)

    return None
