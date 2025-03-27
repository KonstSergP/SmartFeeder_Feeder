import time

from camera import Camera
from detection import DetectorsHandler
from servo import Servo
from video_storage import VideoStorage
from server_connection import ServerConnection

from settings.config import *


class SmartFeeder:
    def __init__(self):
        self.camera      = Camera()
        self.servo       = Servo()
        self.server_conn = ServerConnection(self.camera.start_stream, self.camera.stop_stream)
        self.storage     = VideoStorage(self.server_conn)
        self.detectors   = DetectorsHandler()
        log.info("Smart feeder init")


    def cleanup(self):
        self.camera.cleanup()
        self.servo.cleanup()
        self.storage.cleanup()
        self.server_conn.cleanup()


    def work(self):
        while True:
            self.detectors.update_frame(self.camera.get_frame())
            log.debug("Next iteration")
            
            if self.camera.capturing:
                self._handle_capture()
            elif self.servo.cover_opened:
                self._handle_cover_opened()
            else:
                self._handle_cover_closed()


    def _handle_capture(self):
        if not self.detectors.detect_squirrel():
            self.camera.stop_capture()
            self.servo.close_cover()
            self.storage.go_to_next_video()
        else:
            log.info("Capture continues")
            time.sleep(settings.sleep_time)


    def _handle_cover_opened(self):
        if not self.detectors.detect_hands():
            self.servo.close_cover()
        else:
            log.info("Cover is still open")
            time.sleep(settings.sleep_time)


    def _handle_cover_closed(self):
        if self.detectors.detect_hands():
            self.servo.open_cover()
            time.sleep(settings.sleep_time)

        elif self.detectors.detect_squirrel():
            self.servo.open_cover()
            self.camera.capture_video(self.storage.get_new_video_name())
            time.sleep(settings.sleep_time)
