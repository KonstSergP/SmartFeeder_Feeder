import pytest
from unittest.mock import MagicMock, patch
from feeder import SmartFeeder


@pytest.fixture
def mock_camera():
    with patch('feeder.Camera') as mock_camera_class:
        camera_instance = MagicMock()
        camera_instance.capturing = False
        mock_camera_class.return_value = camera_instance
        yield camera_instance


@pytest.fixture
def mock_servo():
    with patch('feeder.Servo') as mock_servo_class:
        servo_instance = MagicMock()
        servo_instance.cover_opened = False
        mock_servo_class.return_value = servo_instance
        yield servo_instance


@pytest.fixture
def mock_server_connection():
    with patch('feeder.ServerConnection') as mock_server_class:
        server_instance = MagicMock()
        mock_server_class.return_value = server_instance
        yield server_instance


@pytest.fixture
def mock_video_storage():
    with patch('feeder.VideoStorage') as mock_storage_class:
        storage_instance = MagicMock()
        mock_storage_class.return_value = storage_instance
        yield storage_instance


@pytest.fixture
def mock_detectors():
    with patch('feeder.DetectorsHandler') as mock_detectors_class:
        detectors_instance = MagicMock()
        mock_detectors_class.return_value = detectors_instance
        yield detectors_instance


@pytest.fixture
def feeder_with_mocks(mock_camera, mock_servo, mock_server_connection, 
                    mock_video_storage, mock_detectors):
    """Create a SmartFeeder instance with all dependencies mocked"""
    with patch('feeder.time.sleep'):
        return SmartFeeder()


class TestSmartFeeder:

    def test_init(self, feeder_with_mocks, mock_camera, mock_servo, 
                  mock_server_connection, mock_video_storage, mock_detectors):
        """Test successful initialization of the SmartFeeder"""

        feeder = feeder_with_mocks

        assert feeder.camera == mock_camera
        assert feeder.servo == mock_servo
        assert feeder.server_conn == mock_server_connection
        assert feeder.storage == mock_video_storage
        assert feeder.detectors == mock_detectors


    def test_cleanup(self, feeder_with_mocks, mock_camera, mock_servo, 
                    mock_server_connection, mock_video_storage):
        """Test the cleanup method properly cleans up all components"""

        feeder = feeder_with_mocks
        feeder.cleanup()

        assert mock_camera.cleanup.called
        assert mock_servo.cleanup.called
        assert mock_video_storage.cleanup.called
        assert mock_server_connection.cleanup.called


    def test_handle_capture_with_squirrel(self, mock_sleep, feeder_with_mocks, mock_detectors):
        """Test _handle_capture when squirrel continues to be detected"""

        feeder = feeder_with_mocks
        mock_detectors.detect_squirrel.return_value = True
        feeder._handle_capture()

        assert mock_detectors.detect_squirrel.called
        assert not feeder.camera.stop_capture.called
        assert not feeder.servo.close_cover.called
        assert not feeder.storage.go_to_next_video.called
        assert mock_sleep.called


    def test_handle_capture_without_squirrel(self, feeder_with_mocks, mock_detectors):
        """Test _handle_capture when squirrel is no longer detected"""

        feeder = feeder_with_mocks
        mock_detectors.detect_squirrel.return_value = False

        feeder._handle_capture()

        assert mock_detectors.detect_squirrel.called
        assert feeder.camera.stop_capture.called
        assert feeder.servo.close_cover.called
        assert feeder.storage.go_to_next_video.called


    def test_handle_cover_opened_with_hands(self, mock_sleep, feeder_with_mocks, mock_detectors):
        """Test _handle_cover_opened when hands continue to be detected"""

        feeder = feeder_with_mocks
        mock_detectors.detect_hands.return_value = True

        feeder._handle_cover_opened()

        assert mock_detectors.detect_hands.called
        assert not feeder.servo.close_cover.called
        assert mock_sleep.called


    def test_handle_cover_opened_without_hands(self, feeder_with_mocks, mock_detectors):
        """Test _handle_cover_opened when hands are no longer detected"""

        feeder = feeder_with_mocks
        mock_detectors.detect_hands.return_value = False

        feeder._handle_cover_opened()

        assert mock_detectors.detect_hands.called
        assert feeder.servo.close_cover.called


    def test_handle_cover_closed_with_hands(self, mock_sleep, feeder_with_mocks, mock_detectors):
        """Test _handle_cover_closed when hands are detected"""

        feeder = feeder_with_mocks
        mock_detectors.detect_hands.return_value = True

        feeder._handle_cover_closed()

        assert mock_detectors.detect_hands.called
        assert feeder.servo.open_cover.called
        assert mock_sleep.called
        assert not feeder.camera.capture_video.called


    def test_handle_cover_closed_with_squirrel(self, mock_sleep, 
                                              feeder_with_mocks, mock_detectors):
        """Test _handle_cover_closed when squirrel is detected"""

        feeder = feeder_with_mocks
        mock_detectors.detect_hands.return_value = False
        mock_detectors.detect_squirrel.return_value = True

        feeder._handle_cover_closed()

        assert mock_detectors.detect_hands.called
        assert mock_detectors.detect_squirrel.called
        assert feeder.servo.open_cover.called
        assert feeder.camera.capture_video.called
        assert mock_sleep.called


    def test_handle_cover_closed_no_detection(self, feeder_with_mocks, mock_detectors):
        """Test _handle_cover_closed when neither hands nor squirrel are detected"""

        feeder = feeder_with_mocks
        mock_detectors.detect_hands.return_value = False
        mock_detectors.detect_squirrel.return_value = False

        feeder._handle_cover_closed()

        assert mock_detectors.detect_hands.called
        assert mock_detectors.detect_squirrel.called
        assert not feeder.servo.open_cover.called
        assert not feeder.camera.capture_video.called


    def test_work_capturing_state(self, mock_sleep, feeder_with_mocks, mock_camera, mock_servo):
        """Test work method when in capturing state"""

        feeder = feeder_with_mocks
        mock_camera.capturing = True
        mock_servo.cover_opened = False

        feeder.work_iteration()

        assert feeder.detectors.update_frame.called
        assert feeder._handle_capture.called
        assert not feeder._handle_cover_opened.called
        assert not feeder._handle_cover_closed.called


    def test_work_cover_opened_state(self, mock_sleep, feeder_with_mocks, mock_camera, mock_servo):
        """Test work method when in cover opened state"""

        feeder = feeder_with_mocks
        mock_camera.capturing = False
        mock_servo.cover_opened = True

        feeder.work_iteration()

        assert feeder.detectors.update_frame.called
        assert not feeder._handle_capture.called
        assert feeder._handle_cover_opened.called
        assert not feeder._handle_cover_closed.called


    def test_work_cover_closed_state(self, mock_sleep, feeder_with_mocks, mock_camera, mock_servo):
        """Test work method when in cover closed state"""

        feeder = feeder_with_mocks
        mock_camera.capturing = False
        mock_servo.cover_opened = False

        feeder.work_iteration()

        assert feeder.detectors.update_frame.called
        assert not feeder._handle_capture.called
        assert not feeder._handle_cover_opened.called
        assert feeder._handle_cover_closed.called
