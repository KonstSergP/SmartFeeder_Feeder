from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import threading

from config import *

class Camera:
    def __init__(self):
        try:
            self.picam = Picamera2()
        except:
            log.error("Can\'t turn on camera", exc_info=True)
            exit(1)
        self.picam.configure(self.picam.create_video_configuration(
                    main={"size":   Config.FRAME_SIZE,
                          "format": Config.FORMAT}
                    ))
        self.picam.start()

        self.capturing = False
        self.capturing_c = threading.Condition()
    
    def cleanup(self):
        if self.capturing:
            self.stop_capture()

    def get_frame(self):
        return self.picam.capture_array()

    def capture_video(self, video_name):
        self.capturing = True
        log.info("Capture started")
        output = FfmpegOutput(video_name)
        self.picam.start_recording(H264Encoder(bitrate=Config.BITRATE), output)
        
        with self.capturing_c:
            self.capturing = True
            self.capturing_c.wait()
            self.capturing = False

        self.picam.stop_recording()
        log.info("Capture stopped")
        self.picam.start()

    def stop_capture(self):
        with self.capturing_c:
            self.capturing_c.notify()
