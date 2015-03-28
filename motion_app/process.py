import subprocess
from time import sleep
from website.processing import _get_conf
import traceback

def write_motion_conf(motion_conf):
    fp = '/etc/motion/motion.conf'
    f = file(fp,"w+")

    newlines = []
    for line in lines:
        newlines.append(line.format(**motion_conf))
    f.writelines(newlines)
    print "successfully written %s" %fp

def interrupt_process():
    s = subprocess.Popen("ps aux", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
    lis = [line for line in s.split("\n") if "motion" in line]
    if len(lis) != 1:
        print 'could not stop process len(lis) = %s' %len(lis)
        return None
    pid = lis[0].split()[1]
    s = subprocess.Popen("sudo -INT kill %s" %pid, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()

def start_process():
    import subprocess
    subprocess.Popen("sudo motion", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()


def main():
    try:
        conf = _get_conf()
        motion_conf = conf['apps']['motion_app']
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
        print 'KKKEEEYYBOOARDDDDD !!!!!'
        interrupt_process()
    except:
        print traceback.format_exc()
        raise
    

lines = [
     "daemon on"
    ,"process_id_file /var/run/motion/motion.pid"
    ,"setup_mode off"
    ,";logfile /tmp/motion.log"
    ,"log_level 6"
    ,"log_type all"
    ,"videodevice /dev/video0"
    ,"v4l2_palette 17"
    ,"; tunerdevice /dev/tuner0"
    ,"input -1"
    ,"norm 0"
    ,"frequency 0"
    ,"rotate 0"
    ,"width 320"
    ,"height 240"
    ,"framerate 2"
    ,"minimum_frame_time 0"
    ,"; netcam_url value"
    ,"; netcam_userpass value"
    ,"netcam_keepalive off"
    ,"; netcam_proxy value"
    ,"netcam_tolerant_check off"
    ,"auto_brightness off"
    ,"brightness 0"
    ,"contrast 0"
    ,"saturation 0"
    ,"hue 0"
    ,"roundrobin_frames 1"
    ,"roundrobin_skip 1"
    ,"switchfilter off"
    ,"threshold 1500"
    ,"threshold_tune off"
    ,"noise_level 32"
    ,"noise_tune on"
    ,"despeckle_filter EedDl"
    ,"; area_detect value"
    ,"; mask_file value"
    ,"smart_mask_speed 0"
    ,"lightswitch 0"
    ,"minimum_motion_frames 1"
    ,"pre_capture 0"
    ,"post_capture 0"
    ,"event_gap 60"
    ,"max_movie_time 0"
    ,"emulate_motion off"
    ,"# Image File Output"
    ,"output_pictures on"
    ,"output_debug_pictures off"
    ,"quality 75"
    ,"picture_type jpeg"
    ,"# FFMPEG related options"
    ,"ffmpeg_output_movies on"
    ,"ffmpeg_output_debug_movies off"
    ,"ffmpeg_timelapse 0"
    ,"ffmpeg_timelapse_mode daily"
    ,"ffmpeg_bps 500000"
    ,"ffmpeg_variable_bitrate 0"
    ,"ffmpeg_video_codec mpeg4"
    ,"ffmpeg_deinterlace off"
    ,"# SDL Window"
    ,"sdl_threadnr 0"
    ,"# External pipe to video encoder"
    ,"use_extpipe off"
    ,";extpipe mencoder -demuxer rawvideo -rawvideo w=320:h=240:i420 -ovc x264 -x264encopts bframes=4:frameref=1:subq=1:scenecut=-1:nob_adapt:threads=1:keyint=1000:8x8dct:vbv_bufsize=4000:crf=24:partitions=i8x8,i4x4:vbv_maxrate=800:no-chroma-me -vf denoise3d=16:12:48:4,pp=lb -of   avi -o %f.avi - -fps %fps"
    ,"# Snapshots (Traditional Periodic Webcam File Output)"
    ,"snapshot_interval 0"
    ,"# Text Display"
    ,"locate_motion_mode off"
    ,"locate_motion_style box"
    ,"text_right %Y-%m-%d\n%T-%q"
    ,"; text_left CAMERA %t"
    ,"text_changes off"
    ,"text_event %Y%m%d%H%M%S"
    ,"text_double off"
    ,";exif_text %i%J/%K%L"
    ,"# Target Directories and filenames For Images And Films"
    ,"target_dir /usr/local/apache2/htdocs/cam1"
    ,"snapshot_filename %v-%Y%m%d%H%M%S-snapshot"
    ,"picture_filename %v-%Y%m%d%H%M%S-%q"
    ,"movie_filename %v-%Y%m%d%H%M%S"
    ,"timelapse_filename %Y%m%d-timelapse"
    ,"ipv6_enabled off"
    ,"stream_port 8081"
    ,"stream_quality 50"
    ,"stream_motion off"
    ,"stream_maxrate 1"
    ,"stream_localhost on"
    ,"stream_limit 0"
    ,"stream_auth_method 0"
    ,"; stream_authentication username:password"
    ,"# HTTP Based Control"
    ,"webcontrol_port 8080"
    ,"webcontrol_localhost on"
    ,"webcontrol_html_output on"
    ,"; webcontrol_authentication username:password"
    ,"# Tracking (Pan/Tilt)"
    ,"track_type 0"
    ,"track_auto off"
    ,";track_port /dev/ttyS0"
    ,";track_motorx 0"
    ,";track_motorx_reverse 0"
    ,";track_motory 1"
    ,";track_motory_reverse 0"
    ,";track_maxx 200"
    ,";track_minx 50"
    ,";track_maxy 200"
    ,";track_miny 50"
    ,";track_homex 128"
    ,";track_homey 128"
    ,"track_iomojo_id 0"
    ,"track_step_angle_x 10"
    ,"track_step_angle_y 10"
    ,"track_move_wait 10"
    ,"track_speed 255"
    ,"track_stepsize 40"
    ,"# External Commands, Warnings and Logging:"
    ,"quiet on"
    ,"; on_event_start value"
    ,"; on_event_end value"
    ,"; on_picture_save value"
    ,"; on_motion_detected value"
    ,"; on_area_detected value"
    ,"; on_movie_start value"
    ,"; on_movie_end value"
    ,"; on_camera_lost value"
    ,"# Common Options for database features."
    ,"; sql_log_picture on"
    ,"; sql_log_snapshot on"
    ,"; sql_log_movie off"
    ,"; sql_log_timelapse off"
    ,"; sql_query insert into security(camera, filename, frame, file_type, time_stamp, event_time_stamp) values('%t', '%f', '%q', '%n', '%Y-%m-%d %T', '%C')"
    ,"# Database Options"
    ,"; database_type value"
    ,"; database_dbname value"
    ,"; database_host value"
    ,"; database_user value"
    ,"; database_password value"
    ,"; database_port value"
    ,"# Database Options For SQLite3"
    ,"; sqlite3_db value"
    ,"# Video Loopback Device (vloopback project)"
    ,"; video_pipe value"
    ,"; motion_video_pipe value"
    ,"# Thread config files - One for each camera."
    ,"; thread /usr/local/etc/thread1.conf"
    ,"; thread /usr/local/etc/thread2.conf"
    ,"; thread /usr/local/etc/thread3.conf"
    ,"; thread /usr/local/etc/thread4.conf"
    ]
