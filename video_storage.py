import os
import threading
import requests

from settings.config import *


class VideoStorage:

    def __init__(self, server_connection=None):
        if not os.path.exists(settings.video_folder):
            os.makedirs(settings.video_folder)
        
        self.last_id = 0
        self.lock = threading.Lock()
        self.server_connection = server_connection


    def cleanup(self):
        while self.lock.locked(): pass

    
    def get_new_video_name(self):
        path = os.path.join(settings.video_folder, f"{self.last_id}.{settings.video_file_ext}")
        return path


    def go_to_next_video(self):
        self.last_id += 1
        threading.Thread(target=self.send_to_server, daemon=True).start()


    def send_to_server(self):
        if self.server_connection is None or self.lock.locked():
            return
        if not self.server_connection.connected:
            log.info("No connection to server, sending stopped")
            return

        with self.lock:
            log.debug("Sending files: "+" ".join(os.listdir(settings.video_folder)))
            for filename in os.listdir(settings.video_folder):
                if filename != f"{self.last_id}.{settings.video_file_ext}":
                    log.debug(f"Sending file {filename}")
                    video_sent = False
                    try:
                        with open(os.path.join(settings.video_folder, filename), "rb") as f:
                            files={"video": f}
                            r = requests.post(f"http://{settings.server_ip}:{settings.server_port}/upload", files=files, timeout=settings.connection_timeout,
                                                headers={"id": "TEST"})
                            if r.status_code == 200:
                                video_sent = True
                                log.info(f"Video {filename} sent")
                            else:
                                log.error(f"Video upload failed. Status code: {r.status_code}")
                    except requests.Timeout:
                        log.error("Timeout")
                    except:
                        log.error("Can\'t send video to server", exc_info=True)

                    if video_sent:
                        os.remove(os.path.join(settings.video_folder, filename))
                    else:
                        return
