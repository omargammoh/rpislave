import subprocess
from time import sleep
from website.processing import _get_conf
import traceback


def get_motion_config():
    def last_detection_cmd(s):
        return "touch /home/pi/{0}&&echo `date +%Y-%m-%d:%H:%M:%S` > {0} &&echo {0}".format(s)
        #touch /home/pi/las_xxx && echo `date +%Y-%m-%d:%H:%M:%S` > /home/pi/las_xxx
    default_conf = {
        "control_localhost": "off",
        "webcam_localhost": "off",
        "target_dir": "/tmp/motion", #where videos and pictures are stored
        "webcam_maxrate": 3,# limiting speed 0..100
        "webcam_motion": "off",# if set to 'on' Motion sends slows down the webcam stream to 1 picture per second when no motion is detected. When motion is detected the stream runs as defined by webcam_maxrate. When 'off' the webcam stream always runs as defined by webcam_maxrate.
        "threshold": 1500,
        "minimum_motion_frames": 1,
        "gap": 60,
        "pre_capture": 0,
        "post_capture": 0,
        "ffmpeg_video_codec": "swf",
        "movie_filename": "%v-%Y%m%d%H%M%S",
        "webcam_port": 8081,
        "control_port": 8080,
        "ffmpeg_timelapse": 0,
        "snapshot_interval": 0,
        "snapshot_filename": "%v-%Y%m%d%H%M%S-snapshot",
        "output_normal": "on",
        "output_motion": "off",
        "on_motion_detected": last_detection_cmd("last_motion_detected"),
        "on_event_start": last_detection_cmd("last_event_start"),
        "on_event_end": last_detection_cmd("last_event_end"),
        "on_picture_save": last_detection_cmd("last_picture_save"),
        "on_motion_detected": last_detection_cmd("last_motion_detected"),
        "on_area_detected": last_detection_cmd("last_area_detected"),
        "on_movie_start": last_detection_cmd("last_movie_start"),
        "on_movie_end": last_detection_cmd("last_movie_end"),
        "on_camera_lost": last_detection_cmd("last_camera_lost")
    }
    conf = _get_conf()
    motion_conf = conf['apps']['motion_app']

    for k in motion_conf.keys():
        if not(k in default_conf.keys()):
            print "!!the inputed configuration parameter %s has no purpose" %k

    #update the default conf with the user conf
    default_conf.update(motion_conf)

    return default_conf

def write_motion_conf(motion_conf):
    newlines = []
    for line in lines:
        newlines.append(line.format(**motion_conf))

    fp = '/etc/motion/motion.conf'
    f = file(fp,"w+")

    f.write("\n".join(newlines))
    print "successfully written %s" %fp

def interrupt_process():
    s = subprocess.Popen("ps aux", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
    lis = [line for line in s.split("\n") if line.split()[-2:]==['sudo', 'motion'] and not('bin/sh' in line)]
    if len(lis) != 1:
        print 'could not stop process len(lis) = %s' %len(lis)
        for l in lis:
            print l
        return None
    pid = lis[0].split()[1]
    print 'sending INT signal to the motion process...'
    s = subprocess.Popen("sudo kill -INT %s" %pid, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()

def start_process():
    import subprocess
    subprocess.Popen("sudo motion", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()


def main():
    try:
        motion_conf = get_motion_config()
        write_motion_conf(motion_conf)

        #set the rasppi camera will be set as the /tty/video0 ?
        cmd = "sudo modprobe bcm2835-v4l2"
        print cmd
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()

        #set the rasppi camera will be set as the /tty/video0 ?
        cmd = "sudo motion"
        print cmd
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()

        #keep process alive
        while True:
            sleep(60)

    except KeyboardInterrupt:
        interrupt_process()
        print 'motion interrupted successfuly'
    except:
        print traceback.format_exc()
        raise

lines = ['daemon off',
 'process_id_file /var/run/motion/motion.pid',
 'setup_mode off',
 'videodevice /dev/video0',
 'v4l2_palette 8',
 '; tunerdevice /dev/tuner0',
 'input 8',
 'norm 0',
 'frequency 0',
 'rotate 0',
 'width 320',
 'height 240',
 'framerate 2',
 'minimum_frame_time 0',
 '; netcam_url value',
 '; netcam_userpass value',
 '; netcam_http 1.0',
 '; netcam_proxy value',
 'netcam_tolerant_check off',
 'auto_brightness off',
 'brightness 0',
 'contrast 0',
 'saturation 0',
 'hue 0',
 'roundrobin_frames 1',
 'roundrobin_skip 1',
 'switchfilter off',
 'threshold {threshold}',
 'threshold_tune off',
 'noise_level 32',
 'noise_tune on',
 'despeckle EedDl',
 '; area_detect value',
 '; mask_file value',
 'smart_mask_speed 0',
 'lightswitch 0',
 'minimum_motion_frames {minimum_motion_frames}',
 'pre_capture {pre_capture}',
 'post_capture {post_capture}',
 'gap {gap}',
 'max_mpeg_time 0',
 'output_all off',
 'output_normal {output_normal}',
 'output_motion {output_motion}',
 'quality 75',
 'ppm off',
 'ffmpeg_cap_new on',
 'ffmpeg_cap_motion off',
 'ffmpeg_timelapse {ffmpeg_timelapse}',
 'ffmpeg_timelapse_mode daily',
 'ffmpeg_bps 500000',
 'ffmpeg_variable_bitrate 0',
 'ffmpeg_video_codec {ffmpeg_video_codec}',
 'ffmpeg_deinterlace off',
 'snapshot_interval {snapshot_interval}',
 'locate off',
 'text_right %Y-%m-%d\\n%T-%q',
 '; text_left CAMERA %t',
 'text_changes off',
 'text_event %Y%m%d%H%M%S',
 'text_double off',
 'target_dir {target_dir}',
 'snapshot_filename {snapshot_filename}',
 'jpeg_filename %v-%Y%m%d%H%M%S-%q',
 'movie_filename {movie_filename}',
 'timelapse_filename %Y%m%d-timelapse',
 'webcam_port {webcam_port}',
 'webcam_quality 50',
 'webcam_motion {webcam_motion}',
 'webcam_maxrate {webcam_maxrate}',
 'webcam_localhost {webcam_localhost}',
 'webcam_limit 0',
 'control_port {control_port}',
 'control_localhost {control_localhost}',
 'control_html_output on',
 '; control_authentication username:password',
 'track_type 0',
 'track_auto off',
 '; track_port value',
 'track_motorx 0',
 'track_motory 0',
 'track_maxx 0',
 'track_maxy 0',
 'track_iomojo_id 0',
 'track_step_angle_x 10',
 'track_step_angle_y 10',
 'track_move_wait 10',
 'track_speed 255',
 'track_stepsize 40',
 'quiet on',
 'on_event_start {on_event_start} ',
 'on_event_end {on_event_end}',
 'on_picture_save {on_picture_save}',
 'on_motion_detected {on_motion_detected}',
 'on_area_detected {on_area_detected}',
 'on_movie_start {on_movie_start}',
 'on_movie_end {on_movie_end}',
 'on_camera_lost {on_camera_lost}',
 'sql_log_image on',
 'sql_log_snapshot on',
 'sql_log_mpeg off',
 'sql_log_timelapse off',
 "sql_query insert into security(camera, filename, frame, file_type, time_stamp, event_time_stamp) values('%t', '%f', '%q', '%n', '%Y-%m-%d %T', '%C')",
 '; mysql_db value',
 '; mysql_host value',
 '; mysql_user value',
 '; mysql_password value',
 '; pgsql_db value',
 '; pgsql_host value',
 '; pgsql_user value',
 '; pgsql_password value',
 '; pgsql_port 5432',
 '; video_pipe value',
 '; motion_video_pipe value',
 '; thread /usr/local/etc/thread1.conf',
 '; thread /usr/local/etc/thread2.conf',
 '; thread /usr/local/etc/thread3.conf',
 '; thread /usr/local/etc/thread4.conf',
 '']