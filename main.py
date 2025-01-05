import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from time import sleep
import RPi.GPIO as GPIO
from server_communication import VideoUploader
from config import CONFIG

class SmartFeeder:
    def __init__(self):
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CONFIG['camera']['width'])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CONFIG['camera']['height'])
        
        # Initialize servo
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(CONFIG['servo']['pin'], GPIO.OUT)
        self.servo = GPIO.PWM(CONFIG['servo']['pin'], 50)
        self.servo.start(0)
        
        # Initialize TFLite interpreter
        self.interpreter = tflite.Interpreter(model_path=CONFIG['model']['path'])
        self.interpreter.allocate_tensors()
        
        self.uploader = VideoUploader(CONFIG['server']['url'])
        
    def open_cover(self):
        self.servo.ChangeDutyCycle(CONFIG['servo']['open_position'])
        sleep(0.5)
        self.servo.ChangeDutyCycle(0)
        
    def close_cover(self):
        self.servo.ChangeDutyCycle(CONFIG['servo']['close_position'])
        sleep(0.5)
        self.servo.ChangeDutyCycle(0)
        
    def detect_objects(self, frame):
        # Preprocess image for model
        input_data = cv2.resize(frame, (CONFIG['model']['input_size'], CONFIG['model']['input_size']))
        input_data = np.expand_dims(input_data, axis=0)
        
        # Get results from model
        self.interpreter.set_tensor(self.interpreter.get_input_details()[0]['index'], input_data)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.interpreter.get_output_details()[0]['index'])
        
        return self.process_detections(output_data)
        
    def run(self):
        video_writer = None
        recording = False
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                    
                detections = self.detect_objects(frame)
                
                if 'squirrel' in detections and not 'hand' in detections:
                    if not recording:
                        # Start new recording
                        filename = f"squirrel_{int(time.time())}.mp4"
                        video_writer = cv2.VideoWriter(
                            filename,
                            cv2.VideoWriter_fourcc(*'mp4v'),
                            CONFIG['camera']['fps'],
                            (CONFIG['camera']['width'], CONFIG['camera']['height'])
                        )
                        recording = True
                        self.open_cover()
                    
                    video_writer.write(frame)
                else:
                    if recording:
                        # Finish recording and upload
                        video_writer.release()
                        self.close_cover()
                        self.uploader.upload_video(filename)
                        recording = False
                        
        finally:
            self.cleanup()
            
    def cleanup(self):
        self.cap.release()
        GPIO.cleanup()
        if video_writer:
            video_writer.release()

if __name__ == "__main__":
    feeder = SmartFeeder()
    feeder.run()
