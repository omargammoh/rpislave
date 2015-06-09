from website.processing import _get_conf
import traceback
import subprocess
from time import sleep

board_bmc = dict([(7,4),(11,17),(12,18),(13,27),(15,22),(16,23),(18,24),(22,25),(29,6),(31,12),(32,12),(33,13),(35,19),(36,16),(37,26),(38,20),(40,21)])

def get_para(pin_bcm, para):
    try:
        with open("/sys/class/gpio/gpio%s/%s" % (pin_bcm, para)) as pin:
            status = pin.read().strip()
    except:
        raise BaseException('could not get the parameter')

    return status

def set_para(pin_bcm, para, value):
    try:
        f = open("/sys/class/gpio/gpio%s/%s" % (pin_bcm, para), 'w')
        f.write(value)
        f.close()
    except:
        raise BaseException("Error setting parameter %s to %s" %(para,pin_bcm))

def export(pin_bcm):
    cmd = "echo %s > /sys/class/gpio/export" %pin_bcm
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
    print ">>> gpio_app:", cmd

def unexport(pin_bcm):
    cmd = "echo %s > /sys/class/gpio/unexport" %pin_bcm
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
    print ">>> gpio_app:", cmd

def main(pins):

    for bcmpin in board_bmc.values():
        export(bcmpin)

    pins = _get_conf()['apps']['gpio_app']['pins']

    for label, conf in pins.iteritems():
        try:
            pin_bcm = board_bmc[conf["pin"]]
            if conf["iou"] == "input":
                set_para(pin_bcm=pin_bcm, para="direction", value="in")
            elif conf["iou"] == "output":
                set_para(pin_bcm=pin_bcm, para="direction", value="out")
                if conf.get("start","low") == "high":
                    set_para(pin_bcm=pin_bcm, para="value", value="1")
                else:
                    set_para(pin_bcm=pin_bcm, para="value", value="0")

            elif conf["iou"] == "unset":
                #TODO: find a way to unset a pin
                pass
            else:
                raise BaseException('iou is not known %s' %conf["iou"] )
            print ">>> gpio_app: succesfuly done %s" %conf
        except:
            print ">>> gpio_app: !!failed setting up pin %s" %label
            #print traceback.format_exc()

    return None
