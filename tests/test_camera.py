import pytest
from unittest.mock import MagicMock, patch
from camera.camera import Camera


@pytest.fixture
def mock_picamera():
    with patch('camera.camera.Picamera2') as mock_picam:
        mock_instance = mock_picam.return_value
        mock_instance.create_video_configuration.return_value = {"config": "test"}
        yield mock_instance


@pytest.fixture
def mock_encoder():
    with patch('camera.camera.H264Encoder') as mock_encoder_class:
        mock_encoder = MagicMock()
        mock_encoder.running = False
        mock_encoder_class.return_value = mock_encoder
        yield mock_encoder


@pytest.fixture
def mock_mode_controller():
    with patch('camera.camera.CameraModeController') as mock_controller_class:
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        yield mock_controller


@pytest.fixture
def mock_settings():
    with patch('camera.camera.settings') as mock_settings:
        mock_settings.enable_camera_mode_control = False
        mock_settings.fps = 30
        mock_settings.width = 640
        mock_settings.height = 480
        mock_settings.format = "RGB888"
        mock_settings.bitrate = 10000000
        yield mock_settings


class TestCamera:
    
    def test_init_success(self, mock_picamera):
        camera = Camera()

        assert camera._picam == mock_picamera
        assert mock_picamera.start.called
        assert mock_picamera.configure.called
        assert camera._capture_encoder is not None
        assert camera._stream_encoder is not None


    @patch('camera.camera.exit')
    def test_init_camera_failure(self, mock_exit, mock_picamera):
        mock_picamera.side_effect = Exception("Camera init failed")
        
        with patch('camera.camera.log') as mock_log:
            Camera()
            assert mock_log.error.called
            assert mock_exit.called


    def test_configure_camera_with_mode_control(self, mock_settings, mock_picamera, mock_mode_controller):
        
        camera = Camera()
        
        assert camera.camera_mode_controller is not None
        assert mock_picamera.create_video_configuration.called

        call_args = mock_picamera.create_video_configuration.call_args
        assert call_args[1]['main']['size'] == [mock_settings.width, mock_settings.height]
        assert call_args[1]['main']['format'] == mock_settings.format


    def test_cleanup(self, mock_settings, mock_picamera, mock_encoder):
        mock_encoder.running = True

        camera = Camera()
        camera.cleanup()

        assert mock_picamera.stop.called


    def test_get_frame(self, mock_settings, mock_picamera, mock_encoder):
        camera = Camera()
        camera.get_frame()

        assert mock_picamera.capture_array.called


    def test_capture_video(self, mock_settings, mock_picamera, mock_encoder):
        with patch('camera.camera.CaptureAndStreamOutput') as mock_output:
            camera = Camera()
            camera.capture_video("test.mp4")

            assert mock_output.called
            assert mock_output.call_args[0][0] == "test.mp4"
            assert mock_picamera.start_encoder.called


    def test_stop_capture(self, mock_settings, mock_picamera, mock_encoder):
        mock_encoder.running = True

        camera = Camera()
        camera.stop_capture()

        assert mock_picamera.stop_encoder.called


    def test_start_stream(self, mock_settings, mock_picamera, mock_encoder):
        mock_settings.server_host = "192.168.1.1"
        
        with patch('camera.camera.CaptureAndStreamOutput') as mock_output:
            camera = Camera()
            camera.start_stream(8554, "test_path")

            assert mock_output.called
            cmd_str = mock_output.call_args[0][0]
            assert "rtp://" in cmd_str
            assert "8554" in cmd_str
            assert "test_path" in cmd_str
            assert mock_picamera.start_encoder.called


    def test_stop_stream_when_running(self, mock_settings, mock_picamera, mock_encoder):
        mock_encoder.running = True

        camera = Camera()
        camera.stop_stream()

        assert mock_picamera.stop_encoder.called
