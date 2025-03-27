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
        
        self.init_connection_parameters()

        self.handle_socketio_connection()


    def init_connection_parameters(self):
        self.feeder_id = get_feeder_id()


    def handle_socketio_connection(self):
        if settings.online_mode:
            self._socketio.on("connect",        self._on_connection)
            self._socketio.on("disconnect",     self._on_disconnection)
            self._socketio.on("stream start",   self._on_stream_start)
            self._socketio.on("stream stop",    self._on_stream_stop)
            self._socketio.on("assign id",      self._on_assigning_id)
            log.info("Attached socketio handlers")
            threading.Thread(target=self._connect_to_server, daemon=True).start()
        else:
            log.info("Selected offline mode")


    def cleanup(self):
        if self._socketio.connected:
            try:
                self._socketio.disconnect()
                log.info("Disconnected from server")
            except Exception as e:
                log.error(f"Error disconnecting from server: {e}", exc_info=True)


    def _connect_to_server(self):
        auth = {
            "type": settings.client_type,
        }
        if self.feeder_id is not None:
            auth["id"] = self.feeder_id
        else:
            auth["need id"] = "true"

        try:
            self._socketio.connect(f"http://{get_socket_address()}",
                                auth=auth,
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
            self.stream_start_handler(data["port"], self.feeder_id)
            return {"success": True}
        return {"success": False, "Error": "no stream start handler"}


    def _on_stream_stop(self):
        if self.stream_stop_handler is not None:
            self.stream_stop_handler()
            return {"success": True}
        return {"success": False, "Error": "no stream stop handler"}


    def _on_assigning_id(self, data):
        self.feeder_id = data["id"]
        set_feeder_id(self.feeder_id)
        log.info(f"Assigned new id: {self.feeder_id}")
        
        self._socketio.disconnect()
        self._socketio.wait()
        self._connect_to_server() # to change "need id" -> "id"
