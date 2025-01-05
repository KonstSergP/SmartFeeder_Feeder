import time
import threading

from camera import Camera
from detection import SquirrelDetector, HandsDetector
from servo import Servo
from video_storage import VideoStorage
from config import *


class SmartFeeder:
    def __init__(self):
        self.camera     = Camera()
        self.servo      = Servo()
        self.storage    = VideoStorage()
        self.squirrel_detector  = SquirrelDetector()
        self.hands_detector     = HandsDetector()

    def work(self):
        while True:
            if self.camera.capturing:
                self._handle_capture()
            elif self.servo.cover_opened:
                self._handle_cover_opened()
            else:
                self._handle_cover_closed()

    def _handle_capture(self):
        if not self.squirrel_detector.detect(self.camera.get_frame()):
            self.camera.stop_capture()
            self.servo.close_cover()
            self.storage.go_to_next()
            threading.Thread(self.storage.send_to_server(), daemon=True).start()

    def _handle_cover_opened(self):
        self.camera.update_frame()
        if not self.hands_detector.detect(self.camera.get_frame()):
            self.servo.close_cover()

    def _handle_cover_closed(self):
        self.camera.update_frame()
        if self.hands_detector.detect(self.camera.get_frame()):
            self.servo.open_cover()
            time.sleep(10)
            
        elif self.squirrel_detector.detect(self.camera.get_frame()):
            self.servo.open_cover()
            threading.Thread(
                self.camera.capture_video,
                args=[self.storage.get_new_video_name()],
                daemon=True,
            ).start()
            time.sleep(10)
