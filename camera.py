from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

from config import *

class Camera:
    def __init__(self):
        try:
            self._picam = Picamera2()
        except:
            log.error("Can\'t turn on camera", exc_info=True)
            exit(1)
        self._picam.configure(self._picam.create_video_configuration(
                    main={"size":   Config.FRAME_SIZE,
                          "format": Config.FORMAT}
                    ))
        self._picam.start()

        self._capture_encoder = H264Encoder(bitrate=Config.BITRATE)
        self._stream_encoder  = H264Encoder(bitrate=Config.BITRATE)

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

    def get_frame(self):
        return self._picam.capture_array()

    def capture_video(self, video_name):
        self._capture_encoder.output = FfmpegOutput(video_name)
        self._picam.start_encoder(self._capture_encoder)
        log.info("Capture started")

    def stop_capture(self):
        if not self.capturing:
            return
        self._picam.stop_encoder(self._capture_encoder)
        log.info("Capture stopped")

    def start_stream(self, port, path):
        self._stream_encoder.output = FfmpegOutput(f"-f rtp_mpegts rtp://{Config.SERVER_IP}:{port}/{path}")
        self._picam.start_encoder(self._stream_encoder)
        log.info("Stream started")

    def stop_stream(self):
        if not self.streaming:
            return
        self._picam.stop_encoder(self._stream_encoder)
        log.info("Stream stopped")
