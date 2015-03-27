import subprocess
from time import sleep

def main(port=8554):
    #SETTING UP CAMERA STREAM:
    #http://www.raspberry-projects.com/pi/pi-hardware/raspberry-pi-camera/streaming-video-using-vlc-player
    #sudo apt-get update
    #sudo apt-get install -y vlc

    cmd = "raspivid -o - -t 0 -n | cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:%s/}' :demux=h264" %port

    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()

    #keep process alive
    while True:
        sleep(60)

    return None
