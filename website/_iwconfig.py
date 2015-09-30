import re
import subprocess
import time
import traceback

def execute(cmd, daemon=False):
    if daemon:
        _ = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return None
    else:
        return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()


while True:
    try:
        resp = execute("iwconfig")
        print "%0.f" %time.time(), "quality={0[q]} level={0[s]} noise={0[n]}".format(re.compile(r'(.+)Link Quality=(?P<q>\d+)(.+)Signal level=(?P<s>\d+)(.+)Noise level=(?P<n>\d+)(.+)', flags=re.DOTALL).match(resp).groupdict())
    except:
        print traceback.format_exc()
    time.sleep(1)

