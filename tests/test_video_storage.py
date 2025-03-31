import pytest
import os
import threading
import time
from unittest.mock import patch, MagicMock, call, mock_open

from video_storage import VideoStorage
from server_connection import ServerConnection


@pytest.fixture
def mock_os():
    with patch('video_storage.os') as mock_os:
        mock_os.path.exists.return_value = False
        mock_os.path.join = os.path.join
        mock_os.listdir.return_value = []
        yield mock_os


@pytest.fixture
def mock_threading():
    with patch('video_storage.threading') as mock_threading:
        mock_thread = MagicMock()
        mock_threading.Thread.return_value = mock_thread
        mock_lock = MagicMock()
        mock_threading.Lock.return_value = mock_lock
        yield mock_threading


@pytest.fixture
def mock_requests():
    with patch('video_storage.requests') as mock_requests:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response
        yield mock_requests


@pytest.fixture
def mock_server_connection():
    mock_conn = MagicMock(spec=ServerConnection)
    mock_conn.connected = True
    mock_conn.feeder_id = "test_feeder_id"
    yield mock_conn


@pytest.fixture
def mock_settings():
    with patch('video_storage.settings') as mock_settings:
        mock_settings.video_folder = "test_videos"
        mock_settings.video_file_ext = "mp4"
        mock_settings.connection_timeout = 5
        yield mock_settings


@pytest.fixture
def mock_log():
    with patch('video_storage.log') as mock_log:
        yield mock_log


@pytest.fixture
def mock_get_socket_address():
    with patch('video_storage.get_socket_address') as mock_get_addr:
        mock_get_addr.return_value = "test_server:5000"
        yield mock_get_addr


class TestVideoStorage:
    
    def test_init_creates_directory(self, mock_os, mock_threading, mock_settings):
        storage = VideoStorage()

        mock_os.path.exists.assert_called_once_with(mock_settings.video_folder)
        mock_os.makedirs.assert_called_once_with(mock_settings.video_folder)

        assert storage.last_id == 0
        assert storage.server_connection is None
        assert storage.lock == mock_threading.Lock.return_value


    def test_init_with_existing_directory(self, mock_os, mock_threading, mock_settings):
        mock_os.path.exists.return_value = True
        storage = VideoStorage()

        mock_os.path.exists.assert_called_once_with(mock_settings.video_folder)
        mock_os.makedirs.assert_not_called()


    def test_init_with_server_connection(self, mock_os, mock_threading, mock_server_connection):
        storage = VideoStorage(mock_server_connection)
        assert storage.server_connection == mock_server_connection


    def test_go_to_next_video(self, mock_threading):
        storage = VideoStorage()
        initial_id = storage.last_id

        storage.go_to_next_video()

        assert storage.last_id == initial_id + 1
        mock_threading.Thread.assert_called_once_with(
            target=storage.send_to_server, 
            daemon=True)
        mock_threading.Thread.return_value.start.assert_called_once()


    def test_cleanup_waits_for_lock(self, mock_threading):
        storage = VideoStorage()
        mock_threading.Lock.return_value.locked.side_effect = [True, False]

        storage.cleanup()

        assert mock_threading.Lock.return_value.locked.call_count == 2


    def test_send_to_server_no_connection(self, mock_server_connection, mock_threading):
        mock_server_connection.connected = False
        storage = VideoStorage(mock_server_connection)
        
        storage.send_to_server()

        mock_threading.Lock.return_value.__enter__.assert_not_called()


    def test_send_to_server_already_locked(self, mock_threading, mock_server_connection):
        storage = VideoStorage(mock_server_connection)

        mock_threading.Lock.return_value.locked.return_value = True
        
        storage.send_to_server()

        mock_threading.Lock.return_value.__enter__.assert_not_called()


    def test_send_to_server_no_files(self, mock_os, mock_server_connection, mock_log):
        mock_os.listdir.return_value = []
        storage = VideoStorage(mock_server_connection)
        storage.send_to_server()

        mock_os.listdir.assert_called_once()
        mock_log.debug.assert_called_with("Sending files: ")


    def test_send_to_server_skip_current_recording(self, mock_os, mock_server_connection, 
                                                mock_settings, mock_requests):
        mock_os.listdir.return_value = ["1.mp4", "2.mp4", "0.mp4"]
        mock_settings.video_file_ext = "mp4"
        storage = VideoStorage(mock_server_connection)

        with patch('builtins.open', mock_open(read_data='test data')) as mock_file:
            storage.send_to_server()

            assert mock_file.call_count == 2
            mock_file.assert_has_calls([
                call(os.path.join(mock_settings.video_folder, "1.mp4"), "rb"),
                call(os.path.join(mock_settings.video_folder, "2.mp4"), "rb"),
            ], any_order=True)


    def test_send_to_server_successful_upload(self, mock_os, mock_server_connection, 
                                            mock_settings, mock_requests, mock_log,
                                            mock_get_socket_address):
        mock_os.listdir.return_value = ["1.mp4", "2.mp4"]
        mock_settings.video_file_ext = "mp4"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response
        storage = VideoStorage(mock_server_connection)

        with patch('builtins.open', mock_open(read_data='test data')) as mock_file:
            storage.send_to_server()
        

            assert mock_file.call_count == 2
            assert mock_requests.post.call_count == 2
            assert mock_os.remove.call_count == 2
            mock_os.remove.assert_has_calls([
                call(os.path.join(mock_settings.video_folder, "1.mp4")),
                call(os.path.join(mock_settings.video_folder, "2.mp4"))
            ], any_order=True)


    def test_send_to_server_upload_failure(self, mock_os, mock_server_connection, 
                                          mock_settings, mock_requests, mock_log,
                                          mock_get_socket_address):
        mock_os.listdir.return_value = ["1.mp4"]
        mock_settings.video_file_ext = "mp4"
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_requests.post.return_value = mock_response
        
        storage = VideoStorage(mock_server_connection)

        with patch('builtins.open', mock_open(read_data='test data')) as mock_file:
            storage.send_to_server()

        mock_os.remove.assert_not_called()
        mock_log.error.assert_called_once()

    
    def test_send_to_server_general_exception(self, mock_os, mock_server_connection, 
                                             mock_settings, mock_requests, mock_log):
        mock_os.listdir.return_value = ["1.mp4"]
        mock_settings.video_file_ext = "mp4"
        mock_requests.post.side_effect = Exception()
        storage = VideoStorage(mock_server_connection)

        with patch('builtins.open', mock_open(read_data='test data')) as mock_file:
            storage.send_to_server()

        mock_os.remove.assert_not_called()
        mock_log.error.assert_called_once()
