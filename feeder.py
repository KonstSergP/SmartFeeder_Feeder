import time

from camera import Camera
from detection import DetectorsHandler
from servo import Servo
from video_storage import VideoStorage
from server_connection import ServerConnection

from settings.config import *


class SmartFeeder:
    """
    Main controller class for the feeder.\n
    Coordinates interactions between hardware components (camera, servo motor)
    and software systems (computer vision detectors, server connection, video storage).
    """
    def __init__(self) -> None:
        self.camera      = Camera()

        if settings.enable_servo:
            self.servo = Servo()
        else:
            self.servo = None
            log.warning("Servo motor is disabled.")

        self.server_conn = ServerConnection(self.camera.start_stream, self.camera.stop_stream)
        self.storage     = VideoStorage(self.server_conn)
        self.detectors   = DetectorsHandler()
        log.info("Smart feeder init")


    def cleanup(self) -> None:
        """
        Release all resources and cleanup components.
        Must be called when the system is shutting down or in case of errors.
        """
        self.camera.cleanup()
        if self.servo:
            self.servo.cleanup()
        self.storage.cleanup()
        self.server_conn.cleanup()


    def work(self) -> None:
        while True:
            self.work_iteration()

    
    def work_iteration(self) -> None:
        """
        Captures frames, updates detectors, and handles state transitions.
        The feeder operates in one of three states:
        1. Capturing video, when a squirrel is detected
        2. Cover opened, not squirrel but hands detected
        3. Cover closed, default state
        """
        self.detectors.update_frame(self.camera.get_frame())
        log.debug("Next iteration")
        
        if self.camera.capturing:
            self._handle_capture()
        elif self.servo and self.servo.cover_opened:
            self._handle_cover_opened()
        else:
            self._handle_cover_closed()

        


    def _handle_capture(self) -> None:
        """Handle the state when the system is capturing video."""
        if not self.detectors.detect_squirrel():
            self.camera.stop_capture()
            if self.servo:
                self.servo.close_cover()
            self.storage.go_to_next_video() # Prepare for next video and upload current
        else:
            log.info("Capture continues")
            time.sleep(settings.sleep_time)


    def _handle_cover_opened(self) -> None:
        """Handle the state when the feeder cover is open."""
        if not self.detectors.detect_hands():
            if self.servo:
                self.servo.close_cover()
        else:
            log.info("Cover is still open")
            time.sleep(settings.sleep_time)


    def _handle_cover_closed(self) -> None:
        """
        Handle the default state when the feeder cover is closed.\n
        If hands are detected it will open the feeder cover.\n
        If a squirrel is detected it will open the feeder cover
        and start video recording
        """
        if self.detectors.detect_hands():
            if self.servo:
                self.servo.open_cover()
            time.sleep(settings.sleep_time)

        elif self.detectors.detect_squirrel():
            if self.servo:
                self.servo.open_cover()
            self.camera.capture_video(self.storage.get_new_video_name())
            time.sleep(settings.sleep_time)
