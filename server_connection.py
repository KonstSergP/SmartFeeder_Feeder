import socketio

from settings.config import *


class ServerConnection():
    
    def __init__(self, stream_start_handler=None, stream_stop_handler=None):
        self.stream_start_handler   = stream_start_handler
        self.stream_stop_handler     = stream_stop_handler

        self._socketio = socketio.Client(logger=log)
        self._socketio.on("connect",        self._on_connection)
        self._socketio.on("disconnect",     self._on_disconnection)
        self._socketio.on("stream start",   self._on_stream_start)
        self._socketio.on("stream stop",    self._on_stream_stop)

        self._socketio.connect(f"http://{settings.server_ip}:{settings.server_port}",
                               headers={
                                        "type": "feeder",
                                        "id":   "TEST"
                                        })
        log.info("Connected to server")


    @property
    def connected(self):
        return self._socketio.connected


    def _on_connection(self):
        pass


    def _on_disconnection(self, reason):
        log.error(f"Disconnected: {reason}")


    def _on_stream_start(self, data):
        if self.stream_start_handler is not None:
            self.stream_start_handler(data["port"], data["path"])
        return "stream started"


    def _on_stream_stop(self):
        if self.stream_stop_handler is not None:
            self.stream_stop_handler()
        return "stream stopped"
