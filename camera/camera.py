from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from .picamera2_fix.CaptureAndStreamOutput import CaptureAndStreamOutput
from .camera_mode_controller import CameraModeController


from settings.config import *


class Camera:
    def __init__(self) -> None:
        """
        Manages the Raspberry Pi camera for video capture and streaming.\n
        Handles both local video recording and remote streaming capabilities,
        with support for day/night mode switching through the IR filter control.
        Uses separate encoders for recording and streaming.
        """
        self.camera_mode_controller = None

        # Initialize and configure camera using Picamera2 library
        try:
            self._picam = Picamera2()
        except:
            log.error("Can\'t turn on camera", exc_info=True)
            exit(1)

        self.configure_camera()
        self._picam.start()

        self._capture_encoder = H264Encoder(bitrate=settings.bitrate)
        self._stream_encoder  = H264Encoder(bitrate=settings.bitrate)


    def configure_camera(self) -> None:
        """Configure the camera based on the current settings.\n"""
        # Initialize day/night mode controller if it can be enabled
        if settings.enable_camera_mode_control:
            self.camera_mode_controller = CameraModeController()

        frame_duration = int(1000000 / settings.fps)

        config = self._picam.create_video_configuration(
                    main={
                        "size":   [settings.width, settings.height],
                        "format": settings.format},
                    controls={
                        "FrameDurationLimits": (frame_duration, frame_duration)}
                    )

        self._picam.configure(config)


    @property
    def capturing(self) -> None:
        return self._capture_encoder.running


    @property
    def streaming(self) -> None:
        return self._stream_encoder.running


    def cleanup(self) -> None:
        """Release all camera resources."""
        if self.capturing:
            self.stop_capture()
        if self.streaming:
            self.stop_stream()
        self._picam.stop()
        if self.camera_mode_controller:
            self.camera_mode_controller.cleanup()


    def get_frame(self) -> None:
        return self._picam.capture_array()


    def capture_video(self, video_name: str) -> None:
        """
        Start capturing video to a local file.\n
        Uses the CaptureAndStreamOutput which is a slightly adjusted FfmpegOutput
        """
        self._capture_encoder.output = CaptureAndStreamOutput(video_name,
                                                              audio=settings.enable_audio)
        self._picam.start_encoder(self._capture_encoder)
        log.info("Capture started")


    def stop_capture(self) -> None:
        if not self.capturing:
            return
        self._picam.stop_encoder(self._capture_encoder)
        log.info("Capture stopped")


    def start_stream(self, port: int, path: str) -> None:
        """
        Start streaming video to a remote server.\n
        Uses RTP (Real-time Transport Protocol) to stream H264 encoded video
        to the server.
        Args:
            port: Port number to stream to
            path: Stream path
        """
        self._stream_encoder.output = CaptureAndStreamOutput(f"-preset fast -tune zerolatency -f rtp_mpegts rtp://{settings.server_host}:{port}/{path}",
                                                             audio=settings.enable_audio)
        self._picam.start_encoder(self._stream_encoder)
        log.info(f"Stream started: rtp://{settings.server_host}:{port}/{path}")


    def stop_stream(self) -> None:
        """Stop the current video stream if active, do nothing else"""
        if not self.streaming:
            return
        self._picam.stop_encoder(self._stream_encoder)
        log.info("Stream stopped")
