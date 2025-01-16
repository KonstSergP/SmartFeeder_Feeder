import logging
import sys

from argument_parser import *


log = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
log.addHandler(handler)
log.setLevel(logging.DEBUG if args.debug else logging.INFO)


class Config:
    DEBUG = args.debug
    
    SQUIRREL_MODEL_PATH  = args.smp
    SQUIRREL_LABELS_PATH = args.slp
    
    MIN_CONF_THRESHHOLD  = args.min_conf_threshhold

    SERVO_PIN = args.servo_pin
    OPEN_ANGLE = 90
    CLOSE_ANGLE = 0
    
    SLEEP_TIME = 5

    FRAME_SIZE = (args.width, args.height)
    BITRATE = 10000000
    FORMAT = "RGB888"
    VIDEO_FILE_EXT = "mp4"

    SERVER_IP = args.server_ip
    SERVER_PORT = args.server_port
    UPLOAD_URL = f"http://{SERVER_IP}:{SERVER_PORT}/upload"
    VIDEO_FOLDER = "videos"
    CONN_TIMEOUT = 5
