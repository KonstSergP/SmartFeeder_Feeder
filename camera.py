from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera.outputs import FfmpegOutput
import cv2

from config import *

class Camera:
    def __init__(self):
        self.picam = Picamera2()
        self.picam.configure(self.picam.create_video_configuration(
                    main={"size": Config.FRAME_SIZE,
                          "format": Config.FORMAT}
                    ))

        self.capturing = False
        self.capture_stopped = False

    def get_frame(self):
        return self.picam.capture_array()

    def capture_video(self, video_name):
        self.capturing = True
        log.info("Capture started")
        self.picam.start_recording(H264Encoder(bitrate=Config.BITRATE), FfmpegOutput(video_name))
        
        while self.capturing: pass

        self.picam.stop_recording()
        self.capture_stopped = False

    def stop_capture(self):
        self.capture_stopped = True
        self.capturing = False
        while self.capture_stopped: pass
        log.info("Capture stopped")
