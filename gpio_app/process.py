from website.processing import _get_conf
import traceback
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD)
except:
    print "!!could not import RPi.GPIO"


def main(pins_conf):
    print ""
    pins_conf = _get_conf()['apps']['gpio_app']['pins_conf']
    #gpio_pins = sorted(set([4,16,27,23,22,24,25,5,6,12,13,19,4,26,20,21]))

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

    return None
