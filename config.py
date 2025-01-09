import cv2
import logging
import sys
import os


log = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
log.addHandler(handler)
log.setLevel(logging.INFO)


class Config:
    
    SQUIRREL_MODEL_PATH  = os.path.join("squirrel_model", "detect.tflite")
    SQUIRREL_LABELS_PATH = os.path.join("squirrel_model", "labelmap.txt")
    
    MIN_CONF_THRESHHOLD = 0.9
    
    HANDS_MODEL_PATH = ""

    SERVO_PIN = 14
    OPEN_ANGLE = 90
    CLOSE_ANGLE = 0

    FRAME_SIZE = (640, 480)
    FPS = 20.0 # maybe 30?
    FOURCC = cv2.VideoWriter_fourcc(*"mp4v")

    UPLOAD_URL = "http://192.168.1.74:5000/upload"
    VIDEO_FOLDER = "videos"
