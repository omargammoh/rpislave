import subprocess
from website.processing import get_conf
import traceback


def get_motion_config():
    def on_event(s):
        return "wget --spider http://127.0.0.1:9001/motion_app/register_event/?label={0}\&path=%f".format(s)

    default_conf = {
        "control_localhost": "off",
        "webcam_localhost": "off",
        "target_dir": "/home/pi/data/motion_app", #where videos and pictures are stored
        "webcam_maxrate": 30,# limiting speed 0..100
        "framerate": 5, # 2..100
        "webcam_motion": "on",# if set to 'on' Motion sends slows down the webcam stream to 1 picture per second when no motion is detected. When motion is detected the stream runs as defined by webcam_maxrate. When 'off' the webcam stream always runs as defined by webcam_maxrate.
        "text_changes": "on",#show the number of pixel changes
        "threshold": 300,
        "minimum_motion_frames": 1,
        "gap": 60,
        "pre_capture": 5,
        "post_capture": 20,
        "ffmpeg_video_codec": "mpeg4",
        "movie_filename": "movie/%Y%m%d/%H%M%S",
        "webcam_port": 9002,
        "control_port": 9003,
        "ffmpeg_timelapse": 0,
        "snapshot_interval": 0,
        "jpeg_filename": "picture/%Y%m%d/%H%M%S",
        "snapshot_filename": "snapshot/%Y%m%d/%H%M%S",
        "timelapse_filename": "timelapse/%Y%m%d/%H%M%S",
        "output_normal": "best",
        "output_motion": "off",
        "max_mpeg_time": 300,
        "on_motion_detected": "", #last_detection_cmd("motion_detected"),
        "on_event_start": "", #last_detection_cmd("event_start"),
        "on_event_end": "", #last_detection_cmd("event_end"),
        "on_picture_save": on_event("picture_save"),
        "on_motion_detected": "", #last_detection_cmd("motion_detected"),
        "on_area_detected": "", #last_detection_cmd("area_detected"),
        "on_movie_start": on_event("movie_start"),
        "on_movie_end": on_event("movie_end"),
        "on_camera_lost": "", #last_detection_cmd("camera_lost")
        "width": 640, #tested and working also:320, 240
        "height": 480, #
        "locate": "preview"
    }
    conf = get_conf()
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

        #set the rasppi camera will be set as the /tty/video0 ?, a folder will be created for the data
        cmd = "sudo modprobe bcm2835-v4l2&&sudo mkdir -p /home/pi/data/motion_app"
        print cmd
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()

        #set the rasppi camera will be set as the /tty/video0 ?
        cmd = "sudo motion"
        print cmd
        sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        sp.communicate()

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
 'width {width}',
 'height {height}',
 'framerate {framerate}',
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
 'max_mpeg_time {max_mpeg_time}',
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
 'locate {locate}',
 'text_right %Y-%m-%d\\n%T-%q',
 '; text_left CAMERA %t',
 'text_changes {text_changes}',
 'text_event %Y%m%d%H%M%S',
 'text_double off',
 'target_dir {target_dir}',
 'snapshot_filename {snapshot_filename}',
 'jpeg_filename {jpeg_filename}',
 'movie_filename {movie_filename}',
 'timelapse_filename {timelapse_filename}',
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