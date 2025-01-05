import cv2

class Config:
    
    SQUIRREL_MODEL_PATH = ""
    HANDS_MODEL_PATH = ""

    SERVO_PIN = 14

    FRAME_SIZE = (640, 480)
    FPS = 20.0
    FOURCC = cv2.VideoWriter_fourcc(*"MP4V")

    UPLOAD_URL = "http://yourserver.com/upload"
    VIDEO_FOLDER = "videos"
    