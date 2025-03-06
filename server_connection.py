import socketio
import threading

from settings.config import *


class ServerConnection():
    
    def __init__(self, stream_start_handler=None, stream_stop_handler=None):
        self.stream_start_handler   = stream_start_handler
        self.stream_stop_handler    = stream_stop_handler

        self._socketio = socketio.Client(logger=log,
                                    reconnection_delay=1,
                                    reconnection_delay_max=16)

        self.handle_socketio_connection()


    def handle_socketio_connection(self):
        if settings.online_mode:
            self._socketio.on("connect",        self._on_connection)
            self._socketio.on("disconnect",     self._on_disconnection)
            self._socketio.on("stream start",   self._on_stream_start)
            self._socketio.on("stream stop",    self._on_stream_stop)
            log.info("Attached socketio handlers")
            threading.Thread(target=self._connect_to_server, daemon=True).start()
        else:
            log.info("Selected offline mode")


    def _connect_to_server(self):
        try:
            self._socketio.connect(f"http://{settings.server_ip}:{settings.server_port}",
                                headers={
                                            "type": settings.client_type,
                                            "id":   "TEST"
                                            },
                                retry=True)
        except:
            log.error("Can\'t connect to server", exc_info=True)
            return
        log.info("Connected to server")


    @property
    def connected(self):
        return self._socketio.connected


    def _on_connection(self):
        pass


    def _on_disconnection(self, reason):
        if self.stream_stop_handler is not None:
            self.stream_stop_handler()
        log.error(f"Disconnected: {reason}")


    def _on_stream_start(self, data):
        if self.stream_start_handler is not None:
            self.stream_start_handler(data["port"], data["path"])
            return "stream started"
        return "no stream start handler"


    def _on_stream_stop(self):
        if self.stream_stop_handler is not None:
            self.stream_stop_handler()
            return "stream stopped"
        return "no stream stop handler"
