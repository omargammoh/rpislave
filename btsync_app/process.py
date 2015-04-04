import subprocess
from time import sleep
import traceback
import os

cmd = "./home/pi/btsync --webui.listen 0.0.0.0:9004"

def main():
    pid = None
    try:
        #make sure the data folder is there with the correct permissions
        if not os.path.isdir("/home/pi/data"):
            os.mkdir("/home/pi/data")
        _ = subprocess.Popen('sudo chmod -R 0777 "/home/pi/data"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()

        #run server
        pc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        pid = pc.pid
        s = pc.stdout.read()

        #keep this process alive
        while True:
            sleep(60)

    except KeyboardInterrupt:
        if pid:
            s = subprocess.Popen("sudo kill -INT %s" %pid, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
            print 'motion interrupted successfuly'
        else: print 'no pid'
        print "btsync_app exiting"

    except:
        print traceback.format_exc()
        raise


