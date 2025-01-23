import time
import threading

from camera import Camera
from squirrel_detection import SquirrelDetector
from hands_detection import HandsDetector
from servo import Servo
from video_storage import VideoStorage
from server_connection import ServerConnection

from config import *


class SmartFeeder:
    def __init__(self):
        self.camera      = Camera()
        self.servo       = Servo()
        self.server_conn = ServerConnection()
        self.storage     = VideoStorage(self.server_conn)
        self.squirrel_detector  = SquirrelDetector()
        self.hands_detector     = HandsDetector()
        log.info("Smart feeder init")
    
    def cleanup(self):
        self.camera.cleanup()
        self.servo.cleanup()
        self.storage.cleanup()

    def work(self):
        while True:
            log.debug("Next iteration")
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
            self.storage.go_to_next_video()
        else:
            log.info("Capture continues")
            time.sleep(Config.SLEEP_TIME)

    def _handle_cover_opened(self):
        if not self.hands_detector.detect(self.camera.get_frame()):
            self.servo.close_cover()
        else:
            log.info("Cover is still open")
            time.sleep(Config.SLEEP_TIME)

    def _handle_cover_closed(self):
        if self.hands_detector.detect(self.camera.get_frame()):
            self.servo.open_cover()
            time.sleep(Config.SLEEP_TIME)

        elif self.squirrel_detector.detect(self.camera.get_frame()):
            self.servo.open_cover()
            self.camera.capture_video(self.storage.get_new_video_name())
            time.sleep(Config.SLEEP_TIME)
