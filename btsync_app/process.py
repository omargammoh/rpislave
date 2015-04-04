import subprocess
import traceback
import os

cmd = "./btsync --nodaemon --webui.listen 0.0.0.0:9004"

def main():
    pid = None
    try:
        #make sure the data folder is there with the correct permissions
        if not os.path.isdir("/home/pi/data"):
            os.mkdir("/home/pi/data")
        pc = subprocess.Popen('sudo chmod -R 0777 "/home/pi/data"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        pc.communicate()

        #run server
        pc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=r'/home/pi')
        pid = pc.pid
        print "getsync_app started in pid %s" %pid
        pc.communicate()#when running, compiler is stuck here

    except KeyboardInterrupt:
        pc = subprocess.Popen("sudo pkill btsync", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        pc.communicate()
        print 'btsync_app: interrupted successfuly'

    except:
        print traceback.format_exc()
        raise



