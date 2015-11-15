import datetime
import time
import website.processing

def get_laststatusloop():
    try:
        f = file('/home/pi/data/laststatusloop','r')
        s = f.read()
        f.close()
        dt = datetime.datetime.strptime(s, '%Y%m%d%H%M%S')
        return dt
    except:
        print ">> rebooter: !!! failed to read last status loop"
        return None


def main():
    deviation_counter = 0
    while True:
        try:
            dt = get_laststatusloop()
            if dt is not None:
                now = datetime.datetime.utcnow()
                sec = (now - dt).total_seconds()
                if sec > 60: #600
                    print ">> rebooter: deviation counter +1"
                    deviation_counter += 1

                if deviation_counter >= 4:
                    print ">> rebooter: will reboot the device because the status process doesnt seem to have run in a while"
                    f = file('/home/pi/data/reboooter-' + now.strftime('%Y%m%d%H%M%S'),'w')
                    f.write('we have rebooted on %s' %str(now))
                    f.close()
                    website.processing.execute(cmd="sudo reboot")
                else:
                    print ">> rebooter: is fine"
        except:
            print ">> rebooter: !!! error"
            pass

        time.sleep(30)#500
