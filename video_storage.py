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
        self.server_reachable = False
        self.ping()
    
    def cleanup(self):
        while self.lock.locked(): pass
            
    
    def get_new_video_name(self):
        path = os.path.join(Config.VIDEO_FOLDER, f"{self.last_id}.{Config.VIDEO_FILE_EXT}")
        return path

    def go_to_next_name(self):
        self.last_id += 1
    
    def send_to_server(self):
        log.debug("Locked: "+str(bool(self.lock.locked())))
        if self.lock.locked(): return
        if not self.server_reachable and not self.ping():
            log.info("server is not reachable, sending stopped")
            return

        with self.lock:
            log.debug("Sending files: "+" ".join(os.listdir(Config.VIDEO_FOLDER)))
            for filename in os.listdir(Config.VIDEO_FOLDER):
                if filename != f"{self.last_id}.{Config.VIDEO_FILE_EXT}":
                    log.debug(f"Sending file {filename}")
                    video_sent = False
                    try:
                        with open(os.path.join(Config.VIDEO_FOLDER, filename), "rb") as f:
                            files={"video": f}
                            r = requests.post(Config.UPLOAD_URL, files=files, timeout=Config.CONN_TIMEOUT)
                            if r.status_code == 200:
                                video_sent = True
                                log.info(f"Video {filename} sent")
                            else:
                                log.error(f"Video upload failed. Status code: {r.status_code}")
                    except requests.Timeout:
                        log.error("Timeout")
                        self.server_reachable = False
                    except:
                        log.error("Can\'t send video to server", exc_info=True)

                    if video_sent:
                        os.remove(os.path.join(Config.VIDEO_FOLDER, filename))
                    else:
                        return

    def ping(self):
        packs = '-n' if os.sys.platform.lower() == 'win32' else '-c' # arg number of packets
        self.server_reachable = os.system(f'ping {packs} 1 {Config.SERVER_IP}') == 0
        log.debug(f"ping server: {str(bool(self.server_reachable))}")
        return self.server_reachable
