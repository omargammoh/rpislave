import subprocess
from time import sleep
import traceback
import os

cmd = "./btsync --webui.listen 0.0.0.0:9004"

def main():
    pid = None
    try:
        #make sure the data folder is there with the correct permissions
        if not os.path.isdir("/home/pi/data"):
            os.mkdir("/home/pi/data")
        _ = subprocess.Popen('sudo chmod -R 0777 "/home/pi/data"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()

        #run server
        pc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=r'/home/pi')
        pid = pc.pid
        s = pc.stdout.read()

        #keep this process alive
        while True:
            sleep(60)

    except KeyboardInterrupt:
        if pid:
            s = subprocess.Popen("sudo kill -INT %s" % pid, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
            print 'btsync_app interrupted successfuly'
        else: print 'btsync_app: no pid'

    except:
        print traceback.format_exc()
        raise


