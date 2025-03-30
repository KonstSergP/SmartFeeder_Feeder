import pytest
from unittest.mock import MagicMock, patch, call
from server_connection import ServerConnection


@pytest.fixture
def mock_socketio():
    with patch('server_connection.socketio.Client') as mock_client:
        socketio_instance = MagicMock()
        mock_client.return_value = socketio_instance
        yield socketio_instance


@pytest.fixture
def mock_log():
    with patch('server_connection.log') as mock_log:
        yield mock_log


@pytest.fixture
def mock_get_feeder_id():
    with patch('server_connection.get_feeder_id') as mock_get_id:
        mock_get_id.return_value = "test_feeder_id"
        yield mock_get_id


@pytest.fixture
def mock_set_feeder_id():
    with patch('server_connection.set_feeder_id') as mock_set_id:
        yield mock_set_id


@pytest.fixture
def mock_get_socket_address():
    with patch('server_connection.get_socket_address') as mock_get_addr:
        mock_get_addr.return_value = "test_server:5000"
        yield mock_get_addr


@pytest.fixture
def mock_thread():
    with patch('server_connection.threading.Thread') as mock_thread:
        thread_instance = MagicMock()
        mock_thread.return_value = thread_instance
        yield mock_thread


class TestServerConnection:

    def test_init_online_mode(self, mock_socketio, mock_log, mock_get_feeder_id, mock_thread):
        with patch('server_connection.settings.online_mode', True):
            stream_start = MagicMock()
            stream_stop = MagicMock()
            server_conn = ServerConnection(stream_start, stream_stop)

            assert server_conn.feeder_id == mock_get_feeder_id.return_value
            assert mock_socketio.on.call_count == 5
            mock_socketio.on.assert_has_calls([
                call("connect", server_conn._on_connection),
                call("disconnect", server_conn._on_disconnection),
                call("stream start", server_conn._on_stream_start),
                call("stream stop", server_conn._on_stream_stop),
                call("assign id", server_conn._on_assigning_id)
            ], any_order=True)

            mock_thread.assert_called_once_with(
                target=server_conn._connect_to_server, 
                daemon=True)
            mock_thread.return_value.start.assert_called_once()

            assert server_conn.stream_start_handler == stream_start
            assert server_conn.stream_stop_handler == stream_stop


    def test_init_offline_mode(self, mock_socketio, mock_log, mock_get_feeder_id, mock_thread):
        with patch('server_connection.settings.online_mode', False):
            server_conn = ServerConnection()

            assert mock_socketio.on.call_count == 0
            mock_thread.assert_not_called()


    def test_connect_to_server_with_id(self, mock_socketio, mock_get_feeder_id, mock_get_socket_address):
        with patch('server_connection.settings.online_mode', True):
            with patch('server_connection.settings.client_type', 'feeder'):
                server_conn = ServerConnection()
                mock_socketio.reset_mock()

                server_conn._connect_to_server()

                mock_socketio.connect.assert_called_once_with(
                    f"http://{mock_get_socket_address.return_value}",
                    auth={"type": "feeder", "id": "test_feeder_id"},
                    retry=True)


    def test_connect_to_server_without_id(self, mock_socketio, mock_get_socket_address):
        with patch('server_connection.settings.online_mode', True):
            with patch('server_connection.settings.client_type', 'feeder'):
                mock_get_feeder_id = None
                server_conn = ServerConnection()
                mock_socketio.reset_mock()

                server_conn._connect_to_server()

                mock_socketio.connect.assert_called_once_with(
                    f"http://{mock_get_socket_address.return_value}",
                    auth={"type": "feeder", "need id": "true"},
                    retry=True)


    def test_connect_to_server_error(self, mock_socketio, mock_log, mock_get_socket_address):
        with patch('server_connection.settings.online_mode', True):
            mock_socketio.connect.side_effect = Exception("Connection error")
            
            server_conn = ServerConnection()
            mock_socketio.reset_mock()
            mock_log.reset_mock()
            server_conn._connect_to_server()

            mock_log.error.assert_called_once_with("Can\'t connect to server", exc_info=True)


    def test_cleanup(self, mock_socketio, mock_log):
        with patch('server_connection.settings.online_mode', True):
            server_conn = ServerConnection()
            mock_socketio.connected = True

            server_conn.cleanup()

            mock_socketio.disconnect.assert_called_once()


    def test_on_stream_start_success(self, mock_socketio):
        with patch('server_connection.settings.online_mode', True):
            stream_start = MagicMock()
            server_conn = ServerConnection(stream_start_handler=stream_start)
            server_conn.feeder_id = "test_id"

            result = server_conn._on_stream_start({"port": 8554})

            stream_start.assert_called_once_with(8554, "test_id")
            assert result == {"success": True}


    def test_on_stream_start_no_handler(self, mock_socketio):
        with patch('server_connection.settings.online_mode', True):
            server_conn = ServerConnection(stream_start_handler=None)

            result = server_conn._on_stream_start({"port": 8554})

            assert result == {"success": False, "Error": "no stream start handler"}


    def test_on_stream_stop_success(self, mock_socketio):
        with patch('server_connection.settings.online_mode', True):
            stream_stop = MagicMock()
            server_conn = ServerConnection(stream_stop_handler=stream_stop)

            result = server_conn._on_stream_stop()

            stream_stop.assert_called_once()
            assert result == {"success": True}


    def test_on_stream_stop_no_handler(self, mock_socketio):
        with patch('server_connection.settings.online_mode', True):
            server_conn = ServerConnection(stream_stop_handler=None)

            result = server_conn._on_stream_stop()

            assert result == {"success": False, "Error": "no stream stop handler"}


    def test_on_assigning_id(self, mock_socketio, mock_set_feeder_id, mock_thread):
        with patch('server_connection.settings.online_mode', True):
            with patch('server_connection.threading.Timer') as mock_timer:
                timer_instance = MagicMock()
                mock_timer.return_value = timer_instance
                server_conn = ServerConnection()
                mock_set_feeder_id.reset_mock()
                mock_timer.reset_mock()

                server_conn._on_assigning_id({"id": "new_feeder_id"})

                assert server_conn.feeder_id == "new_feeder_id"
                mock_set_feeder_id.assert_called_once_with("new_feeder_id")
                mock_timer.assert_called_once_with(1, server_conn.reconnect)
                timer_instance.start.assert_called_once()


    def test_reconnect(self, mock_socketio):
        with patch('server_connection.settings.online_mode', True):
            server_conn = ServerConnection()
            mock_socketio.reset_mock()
            server_conn._connect_to_server = MagicMock()

            server_conn.reconnect()

            mock_socketio.disconnect.assert_called_once()
            mock_socketio.wait.assert_called_once()
            server_conn._connect_to_server.assert_called_once()
