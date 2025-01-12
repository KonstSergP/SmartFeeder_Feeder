import os
import threading
import requests

from config import *

class VideoStorage:
    
    def __init__(self):
        self.last_id = 0
        self.lock = threading.Lock()
        if not os.path.exists(Config.VIDEO_FOLDER):
            os.makedirs(Config.VIDEO_FOLDER)
    
    def get_new_video_name(self):
        path = os.path.join(Config.VIDEO_FOLDER, f"{self.last_id}.{Config.VIDEO_FILE_EXT}")
        return path

    def go_to_next(self):
        self.last_id += 1
    
    def send_to_server(self):
        with self.lock:
            for filename in os.listdir(Config.VIDEO_FOLDER):
                print(filename)
                if filename != f"{self.last_id}.{Config.VIDEO_FILE_EXT}":
                    is_sent = False
                    with open(os.path.join(Config.VIDEO_FOLDER, filename), "rb") as f:
                        files={"video": f}
                        try:
                            r = requests.post(Config.UPLOAD_URL, files=files, timeout=Config.CONN_TIMEOUT)
                            if r.status_code == 200:
                                is_sent = True
                                log.info(f"Video {filename} sent")
                            else:
                                log.error("Server error")
                        except:
                            log.error("Can\'t send video to server", exc_info=True)
                    if is_sent:
                        os.remove(os.path.join(Config.VIDEO_FOLDER, filename))
