from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from .picamera2_fix.CaptureAndStreamOutput import CaptureAndStreamOutput
from .camera_mode_controller import CameraModeController


from settings.config import *


class Camera:
    def __init__(self):
        self.camera_mode_controller = None

        if settings.enable_camera_mode_control:
            self.camera_mode_controller = CameraModeController()

        try:
            self._picam = Picamera2()
        except:
            log.error("Can\'t turn on camera", exc_info=True)
            exit(1)
        self._picam.configure(self._picam.create_video_configuration(
                    main={
                        "size":   [settings.width, settings.height],
                        "format": settings.format},
                    controls={
                        "FrameDurationLimits": (50000, 50000)}
                    ))
        self._picam.start()

        self._capture_encoder = H264Encoder(bitrate=settings.bitrate)
        self._stream_encoder  = H264Encoder(bitrate=settings.bitrate)


    @property
    def capturing(self):
        return self._capture_encoder.running


    @property
    def streaming(self):
        return self._stream_encoder.running


    def cleanup(self):
        if self.capturing:
            self.stop_capture()
        if self.streaming:
            self.stop_stream()
        self._picam.stop()
        if self.camera_mode_controller:
            self.camera_mode_controller.cleanup()


    def get_frame(self):
        return self._picam.capture_array()


    def capture_video(self, video_name):
        self._capture_encoder.output = CaptureAndStreamOutput(video_name, audio=True)
        self._picam.start_encoder(self._capture_encoder)
        log.info("Capture started")


    def stop_capture(self):
        if not self.capturing:
            return
        self._picam.stop_encoder(self._capture_encoder)
        log.info("Capture stopped")


    def start_stream(self, port, path):
        self._stream_encoder.output = CaptureAndStreamOutput(f"-f rtp_mpegts rtp://{settings.server_ip}:{port}/{path}", audio=True)
        self._picam.start_encoder(self._stream_encoder)
        log.info(f"Stream started: rtp://{settings.server_ip}:{port}/{path}")


    def stop_stream(self):
        if not self.streaming:
            return
        self._picam.stop_encoder(self._stream_encoder)
        log.info("Stream stopped")
