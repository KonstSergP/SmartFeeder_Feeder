import os
import threading
import requests
from server_connection import ServerConnection
from typing import Optional
from settings.config import *


class VideoStorage:
    """
    Manages the video files captured.\n
    Handles local storage and uploading of video files to the server.
    """

    def __init__(self, server_connection: Optional[ServerConnection]=None) -> None:
        # Create videos directory if it doesn't exist
        if not os.path.exists(settings.video_folder):
            os.makedirs(settings.video_folder)

        self.last_id = 0
        self.lock = threading.Lock() # Prevents concurrent access to video files during upload
        self.server_connection = server_connection


    def cleanup(self) -> None:
        """Wait for any ongoing upload operations to complete."""
        while self.lock.locked(): pass

    
    def get_new_video_name(self) -> str:
        path = os.path.join(settings.video_folder, f"{self.last_id}.{settings.video_file_ext}")
        return path


    def go_to_next_video(self) -> None:
        """Increment the video counter and trigger an upload operation."""
        self.last_id += 1
        threading.Thread(target=self.send_to_server, daemon=True).start()


    def send_to_server(self) -> None:
        """
        Upload all stored videos to the server except the current one being recorded.\n
        Deletes videos after successful upload to save space
        """
        # Skip if no server connection or already uploading
        if self.server_connection is None or self.lock.locked():
            return
        if not self.server_connection.connected:
            log.info("No connection to server, sending stopped")
            return

        with self.lock:
            files = os.listdir(settings.video_folder)
            log.debug("Sending files: "+" ".join(files))

            for filename in files:
                # Skip the video currently being recorded
                if filename != f"{self.last_id}.{settings.video_file_ext}":
                    log.debug(f"Sending file {filename}")
                    video_sent = False
                    try:
                        with open(os.path.join(settings.video_folder, filename), "rb") as f:
                            feeder_id = self.server_connection.feeder_id
                            files={"video": f}
                            r = requests.post(f"http://{get_socket_address()}/upload",
                                                files=files,
                                                timeout=settings.connection_timeout,
                                                data={"id": feeder_id})
                            if r.status_code == 200:
                                video_sent = True
                                log.info(f"Video {filename} sent")
                            else:
                                log.error(f"Video upload failed. Status code: {r.status_code}")
                    except OSError: # for some reason Timeout can't be catched
                        log.error("Request error", exc_info=True)
                    except:
                        log.error("Can\'t send video to server", exc_info=True)

                    # Delete the video file if successfully uploaded
                    if video_sent:
                        os.remove(os.path.join(settings.video_folder, filename))
                    else:
                        return
