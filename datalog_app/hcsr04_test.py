from time import sleep, time

try:
    import RPi.GPIO as GPIO
except:
    print ">>> datalog_app: !!could not load RPi.GPIO module"


try:
    import signal
except:
    print "signal cannot be imported"


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


def _read_hcsr04(pin_trig, pin_echo):
    """
    this is a sensor to measure distances
    """
    with Timeout(seconds=2.):
        GPIO.setmode(GPIO.BCM)

        #pin_trig = 23
        #pin_echo = 24

        GPIO.setup(pin_trig,GPIO.OUT)
        GPIO.setup(pin_echo,GPIO.IN)

        #sending the triger signal
        GPIO.output(pin_trig, False)
        sleep(0.5) #wait for sensor to settle
        GPIO.output(pin_trig, True)
        sleep(0.00001)
        GPIO.output(pin_trig, False)

        #reading the echo signal
        while GPIO.input(pin_echo) == 0:
            pass
        pulse_start = time()
        while GPIO.input(pin_echo) == 1:
            pass
        pulse_end = time()
        pulse_duration = pulse_end - pulse_start

        #measuring distance
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        distance = distance - 0.5
        if distance > 2 - 0.5 and distance < 400 -0.5:
            return distance
        else:
            raise BaseException('distance is out of acceptable range %s' %distance)




if True:
    pin_trig = 23
    pin_echo = 24
    while True:
        try:
            d = _read_hcsr04(pin_trig, pin_echo)
            print "distance = %s" %d
        except:
            print "fail"

        sleep(3)
