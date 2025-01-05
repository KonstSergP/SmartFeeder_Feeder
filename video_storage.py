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
        path = os.path.join(Config.VIDEO_FOLDER, f"{self.last_id}")
        return path

    def go_to_next(self):
        self.last_id += 1
    
    def send_to_server(self):
        with self.lock:
            for filename in os.listdir(Config.VIDEO_FOLDER):
                if filename != f"{self.last_id}":
                    with open(os.path.join(Config.VIDEO_FOLDER, filename), "rb") as f:
                        requests.post(Config.UPLOAD_URL, files={"video": f})
