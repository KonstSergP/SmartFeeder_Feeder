import cv2
import threading

from config import *

class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
                
        self.frame = None
        self.capturing = False
        self.lock = threading.Lock()

    def update_frame(self):
        with self.lock:
            ret, self.frame = self.cap.read()
        if not ret:
            print("Where is frame?")

    def get_frame(self):
        with self.lock:
            return self.frame
    
    def capture_video(self, video_name):
        self.capturing = True
        
        out = cv2.VideoWriter(video_name, Config.FOURCC, Config.FPS, Config.FRAME_SIZE)
        
        while self.capturing:
            self.update_frame()
            with self.lock:
                if self.frame is not None:
                    out.write(self.frame)
        
        out.release()

    def stop_capture(self):
        self.capturing = False
